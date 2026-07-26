import os
from concurrent.futures.thread import ThreadPoolExecutor


def create_crypto_executor() -> ThreadPoolExecutor:
    return ThreadPoolExecutor(
        max_workers=max(1, os.cpu_count() or 4),
        thread_name_prefix="Crypto"
    )
