import os
from concurrent.futures.thread import ThreadPoolExecutor


def create_crypto_executor() -> ThreadPoolExecutor:
    return ThreadPoolExecutor(
        max_workers=1,
        thread_name_prefix="Crypto"
    )
