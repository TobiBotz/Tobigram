"""Benchmark crypto throughput.

Measures AES-IGE, AES-CTR, and new batch/in-place CTR functions.

Usage:
    python -m tests.benchmarks.bench_crypto
"""

import os
import time

from pyrogram.crypto import aes

KEY = os.urandom(32)
IV_CTR = bytearray(os.urandom(16))

MB = 1024 * 1024
DATA_MB = os.urandom(MB)

SMALL = 1024
DATA_SMALL = os.urandom(SMALL)


def bench(label: str, fn, count: int):
    t0 = time.perf_counter()
    for _ in range(count):
        fn()
    elapsed = time.perf_counter() - t0
    us = elapsed / count * 1e6
    print(f"  {label:40s} {us:8.1f} us/call")


def run():
    print(f"===== Crypto Benchmarks ({os.cpu_count()} CPUs) =====\n")

    # IGE
    bench("ige256_encrypt 1MB", lambda: aes.ige256_encrypt(DATA_MB, KEY, os.urandom(32)), 100)
    bench("ige256_decrypt 1MB", lambda: aes.ige256_decrypt(DATA_MB, KEY, os.urandom(32)), 100)

    # CTR standard
    b1 = bytearray(16)
    bench("ctr256_encrypt 1MB (standard)", lambda: aes.ctr256_encrypt(DATA_MB, KEY, bytearray(os.urandom(16)), bytearray(1)), 200)
    b2 = bytearray(16)
    bench("ctr256_decrypt 1MB (standard)", lambda: aes.ctr256_decrypt(DATA_MB, KEY, bytearray(os.urandom(16)), bytearray(1)), 200)

    # CTR in-place
    buf = bytearray(DATA_MB)
    iv = bytearray(16)
    st = bytearray(1)
    def _inplace():
        iv[:] = os.urandom(16)
        st[0] = 0
        buf[:] = DATA_MB
        aes.ctr256_encrypt_inplace(buf, KEY, iv, st)
    bench("ctr256_encrypt_inplace 1MB", _inplace, 200)

    # CTR batch: 10 chunks of 100KB each
    data_chunks = [os.urandom(100 * 1024) for _ in range(10)]
    data_flat = b"".join(data_chunks)
    sizes = bytearray()
    for c in data_chunks:
        sizes += len(c).to_bytes(4, "little")
    batch_ivs = bytearray(16 * 10)
    batch_states = bytearray(10)
    def _batch():
        batch_ivs[:] = os.urandom(16 * 10)
        batch_states[:] = b"\x00" * 10
        aes.ctr256_encrypt_batch(data_flat, sizes, KEY, batch_ivs, batch_states)
    bench("ctr256_encrypt_batch 10x100KB", _batch, 200)

    # Individual calls to compare with batch
    c2 = [os.urandom(100 * 1024) for _ in range(10)]
    ivs2 = [bytearray(16) for _ in range(10)]
    sts2 = [bytearray(1) for _ in range(10)]
    def _individual():
        for iv in ivs2:
            iv[:] = os.urandom(16)
        for st in sts2:
            st[0] = 0
        for d, iv, st in zip(c2, ivs2, sts2):
            aes.ctr256_encrypt(d, KEY, iv, st)
    bench("ctr256_encrypt 10x100KB (individual)", _individual, 200)


if __name__ == "__main__":
    run()
