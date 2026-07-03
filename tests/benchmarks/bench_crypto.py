"""Benchmark crypto throughput with shared executor.

Measures AES-IGE encrypt/decrypt + KDF throughput under varying thread
counts to demonstrate the benefit of a shared crypto executor pool over
per-session single-thread pools.

Covers two data sizes:
  - Small (1 KB):  typical message body for pack/unpack hot path
  - Large (1 MB):  typical file chunk for upload/download CDN decrypt

Usage:
    python -m tests.benchmarks.bench_crypto
"""

import asyncio
import os
import time
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256

from pyrogram.crypto import aes
from pyrogram.crypto.mtproto import kdf
from pyrogram.crypto.executor import get_crypto_executor, set_crypto_executor

AUTH_KEY = os.urandom(256)
MSG_KEY = sha256(b"msg").digest()[8:24]
KEY = sha256(b"key").digest()
IV_IGE = sha256(b"iv").digest()
IV_CTR = bytearray(sha256(b"iv").digest()[:16])

DATA_SMALL = os.urandom(1024)
DATA_LARGE = os.urandom(1024 * 1024)
_IGE_SMALL_ENC = aes.ige256_encrypt(DATA_SMALL, KEY, IV_IGE)
_IGE_LARGE_ENC = aes.ige256_encrypt(DATA_LARGE, KEY, IV_IGE)


def _bench(data: bytes, fn) -> float:
    count, total = 500, 0.0
    for _ in range(count):
        t0 = time.perf_counter()
        fn(data)
        total += time.perf_counter() - t0
    return total


async def bench_concurrent(
    total_calls: int,
    concurrency: int,
    executor: ThreadPoolExecutor,
    fn,
) -> float:
    loop = asyncio.get_event_loop()
    tasks = []
    for _ in range(concurrency):
        count = total_calls // concurrency
        tasks.append(loop.run_in_executor(executor, fn, count))
    results = await asyncio.gather(*tasks)
    return sum(results)


def _run_scenario(label: str, run_fn, rounds: int, concurrency: int) -> tuple:
    print(f"\n  --- {label} ---")

    single = ThreadPoolExecutor(max_workers=1, thread_name_prefix="Single")
    t = asyncio.run(bench_concurrent(rounds, concurrency, single, run_fn))
    rps = (rounds * concurrency) / t
    print(f"    Per-session (1 worker):  {t*1000:.1f}ms total, {rps:>8.0f} calls/s")
    single.shutdown()

    shared = get_crypto_executor()
    t2 = asyncio.run(bench_concurrent(rounds, concurrency, shared, run_fn))
    rps2 = (rounds * concurrency) / t2
    print(f"    Shared pool (auto):      {t2*1000:.1f}ms total, {rps2:>8.0f} calls/s")

    sized = ThreadPoolExecutor(max_workers=concurrency, thread_name_prefix="Sized")
    old = get_crypto_executor()
    set_crypto_executor(sized)
    t3 = asyncio.run(bench_concurrent(rounds, concurrency, sized, run_fn))
    rps3 = (rounds * concurrency) / t3
    print(f"    Sized pool ({concurrency}w):  {t3*1000:.1f}ms total, {rps3:>8.0f} calls/s")
    set_crypto_executor(old)
    sized.shutdown()

    return rps, rps2, rps3


def make_kdf_fn():
    def _fn(n: int):
        total = 0.0
        for _ in range(n):
            t0 = time.perf_counter()
            kdf(AUTH_KEY, MSG_KEY, True)
            total += time.perf_counter() - t0
        return total
    return _fn


def make_ige_enc_fn(data: bytes):
    def _fn(n: int):
        total = 0.0
        for _ in range(n):
            t0 = time.perf_counter()
            aes.ige256_encrypt(data, KEY, IV_IGE)
            total += time.perf_counter() - t0
        return total
    return _fn


def make_ige_dec_fn(data: bytes):
    enc_data = aes.ige256_encrypt(data, KEY, IV_IGE)
    def _fn(n: int):
        total = 0.0
        for _ in range(n):
            t0 = time.perf_counter()
            aes.ige256_decrypt(enc_data, KEY, IV_IGE)
            total += time.perf_counter() - t0
        return total
    return _fn


def make_ctr_enc_fn(data: bytes):
    def _fn(n: int):
        total = 0.0
        for _ in range(n):
            t0 = time.perf_counter()
            aes.ctr256_encrypt(data, KEY, IV_CTR, bytearray(1))
            total += time.perf_counter() - t0
        return total
    return _fn


def make_ctr_dec_fn(data: bytes):
    def _fn(n: int):
        total = 0.0
        for _ in range(n):
            t0 = time.perf_counter()
            aes.ctr256_decrypt(data, KEY, IV_CTR, bytearray(1))
            total += time.perf_counter() - t0
        return total
    return _fn


def run():
    rounds = 200
    concurrency = 8

    print(f"===== Crypto Executor Benchmark =====")
    print(f"Calls per benchmark: {rounds}, concurrency: {concurrency}")
    print(f"Small data: {len(DATA_SMALL)} bytes, Large data: {len(DATA_LARGE)} bytes")
    print()

    scenarios = [
        ("KDF (pure Python)", make_kdf_fn()),
        ("IGE256 ENC (small)", make_ige_enc_fn(DATA_SMALL)),
        ("IGE256 ENC (large)", make_ige_enc_fn(DATA_LARGE)),
        ("IGE256 DEC (small)", make_ige_dec_fn(DATA_SMALL)),
        ("IGE256 DEC (large)", make_ige_dec_fn(DATA_LARGE)),
        ("CTR256 ENC (small)", make_ctr_enc_fn(DATA_SMALL)),
        ("CTR256 ENC (large)", make_ctr_enc_fn(DATA_LARGE)),
        ("CTR256 DEC (small)", make_ctr_dec_fn(DATA_SMALL)),
        ("CTR256 DEC (large)", make_ctr_dec_fn(DATA_LARGE)),
    ]

    results = {}
    for name, fn in scenarios:
        results[name] = _run_scenario(name, fn, rounds, concurrency)

    print(f"\n  --- Summary ---")
    header = f"  {'Operation':30s} {'1-worker':>10s} {'Shared':>10s} {'Sized':>10s}  {'S/1w':>7s} {'Sz/1w':>7s}"
    print(header)
    print(f"  {'-'*80}")
    for name, (b, s, sz) in results.items():
        print(f"  {name:30s} {b:10.0f} {s:10.0f} {sz:10.0f}  {s/b:6.2f}x {sz/b:6.2f}x")

    print(f"\n  --- Analysis ---")
    print(f"  KDF (pure Python): no GIL release -- all pools similar")
    print(f"  Small data (1KB):  1-worker fastest -- dispatch overhead dwarfs actual work")
    print(f"  Large data (1MB):  1-worker fastest -- tgcrypto releases GIL but")
    print(f"     thread dispatch + memory/cache contention erases parallelism gains")
    print(f"  => Main win of shared executor is NOT per-call throughput.")
    print(f"     It is thread RESOURCE CONSOLIDATION:")
    print(f"       - N clients -> 1 pool (not N pools)")
    print(f"       - Caps at auto-scaled workers (no thread explosion)")
    print(f"       - Future WarpCrypto: kdf+AES in 1 Rust call halves overhead")


if __name__ == "__main__":
    run()
