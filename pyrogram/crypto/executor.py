import os
from concurrent.futures.thread import ThreadPoolExecutor


_crypto_pool = None


def get_crypto_executor() -> ThreadPoolExecutor:
    global _crypto_pool
    if _crypto_pool is None:
        _crypto_pool = ThreadPoolExecutor(
            max_workers=max(1, (os.cpu_count() or 4)),
            thread_name_prefix="Crypto"
        )
    return _crypto_pool


def set_crypto_executor(executor: ThreadPoolExecutor):
    global _crypto_pool
    _crypto_pool = executor


def create_crypto_executor() -> ThreadPoolExecutor:
    return ThreadPoolExecutor(
        max_workers=max(1, (os.cpu_count() or 4)),
        thread_name_prefix="Crypto"
    )
