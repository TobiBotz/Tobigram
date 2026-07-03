"""Benchmark: tgcrypto vs WarpCrypto — multi-client scaling.

Compares full pack() operation: tgcrypto (3-step: sha256 + kdf + ige)
vs WarpCrypto (1-step: combined Rust call, single GIL release).

Simulates N concurrent clients each doing pack() operations,
varying thread pool size to measure scaling behavior.

Usage:
    python -m tests.benchmarks.bench_vs_rust
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha256

import warpcrypto
from pyrogram.crypto.aes import ige256_encrypt as tg_ige_enc
from pyrogram.crypto.mtproto import kdf

AUTH_KEY = sha256(b"t").digest() + sha256(b"t2").digest() \
         + sha256(b"t3").digest() + sha256(b"t4").digest() \
         + sha256(b"t5").digest()
AUTH_KEY_ID = sha256(AUTH_KEY).digest()[-8:]
SESSION_ID = os.urandom(8)
SALT = 1234567890
PAYLOAD = os.urandom(1024)


def tgcrypto_pack():
    data = SALT.to_bytes(8, "little") + SESSION_ID + PAYLOAD
    padding = os.urandom(-(len(data) + 12) % 16 + 12)
    msg_key_large = sha256(AUTH_KEY[88:120] + data + padding).digest()
    msg_key = msg_key_large[8:24]
    aes_key, aes_iv = kdf(AUTH_KEY, msg_key, True)
    encrypted = tg_ige_enc(data + padding, aes_key, aes_iv)
    return AUTH_KEY_ID + msg_key + encrypted


def warpcrypto_pack():
    return warpcrypto.pack_message(PAYLOAD, SALT, SESSION_ID, AUTH_KEY, AUTH_KEY_ID)


def simulate_clients(
    impl_fn,
    num_clients: int,
    ops_per_client: int,
    pool_size: int,
):
    """Simulate num_clients each doing ops_per_client crypto ops, sharing a pool."""

    def client_work(n):
        for _ in range(n):
            impl_fn()

    with ThreadPoolExecutor(max_workers=pool_size) as pool:
        t0 = time.perf_counter()
        futs = [pool.submit(client_work, ops_per_client) for _ in range(num_clients)]
        for f in as_completed(futs):
            f.result()
        return time.perf_counter() - t0


def run():
    # Verify bit-exactness first
    r1 = tgcrypto_pack()
    r2 = warpcrypto_pack()
    # Can't compare directly due to os.urandom, but we can verify length match
    assert len(r1) == len(r2), f"output lengths mismatch: {len(r1)} vs {len(r2)}"

    print(f"===== tgcrypto vs WarpCrypto — Multi-Client Scaling =====")
    print(f"Payload: {len(PAYLOAD)} bytes")
    print(f"Ops per client: 200")
    print()

    header = f"  {'Clients':>7s} | {'Pool':>5s} | {'tgcrypto':>10s} | {'WarpCrypto':>10s} | {'ratio':>7s}"
    sep = f"  {'-'*7}-+-{'-'*5}-+-{'-'*10}-+-{'-'*10}-+-{'-'*7}"
    print(header)
    print(sep)

    for num_clients in [1, 2, 4, 8, 16, 32, 64]:
        best_tg = float("inf")
        best_wp = float("inf")
        best_pool_tg = 0
        best_pool_wp = 0

        for pool_sz in [1, 2, 4, 8, 16, 32]:
            dt_tg = simulate_clients(tgcrypto_pack, num_clients, 200, pool_sz)
            dt_wp = simulate_clients(warpcrypto_pack, num_clients, 200, pool_sz)
            if dt_tg < best_tg:
                best_tg = dt_tg
                best_pool_tg = pool_sz
            if dt_wp < best_wp:
                best_wp = dt_wp
                best_pool_wp = pool_sz

        total_ops = num_clients * 200
        tg_tp = total_ops / best_tg
        wp_tp = total_ops / best_wp
        print(f"  {num_clients:>7d} | {best_pool_tg:>3d}/{best_pool_wp:<1d} | {tg_tp:>10.0f} | {wp_tp:>10.0f} | {wp_tp/tg_tp:>6.2f}x")

    print()
    print(f"  Pool column shows: optimal for tgcrypto / WarpCrypto")
    print(f"  Ratio > 1.0 means WarpCrypto faster")

    for title, nc in [("16 clients", 16), ("128 clients", 128)]:
        print(f"\n  --- Deep-dive: {title} ---")
        print(f"  {'Pool':>5s} | {'tgcrypto (s)':>13s} | {'WarpCrypto (s)':>15s} | {'ratio':>7s}")
        print(f"  {'-'*5}-+-{'-'*13}-+-{'-'*15}-+-{'-'*7}")
        for pool_sz in [1, 2, 4, 8, 16, 32]:
            dt_tg = simulate_clients(tgcrypto_pack, nc, 200, pool_sz)
            dt_wp = simulate_clients(warpcrypto_pack, nc, 200, pool_sz)
            r = dt_wp / dt_tg
            faster = "WARP" if dt_wp < dt_tg else "TGCRYPTO"
            print(f"  {pool_sz:>5d} | {dt_tg:>13.4f} | {dt_wp:>15.4f} | {r:>6.2f}x  ({faster})")


if __name__ == "__main__":
    run()
