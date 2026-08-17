import os
from concurrent.futures.thread import ThreadPoolExecutor


def _default_crypto_workers() -> int:
    override = os.environ.get("WZGRAM_CRYPTO_WORKERS")

    if override:
        try:
            return max(1, int(override))
        except ValueError:
            pass

    return min(4, max(2, os.cpu_count() or 1))


_crypto_pool = None


def get_crypto_executor() -> ThreadPoolExecutor:
    global _crypto_pool
    if _crypto_pool is None:
        _crypto_pool = ThreadPoolExecutor(
            max_workers=_default_crypto_workers(),
            thread_name_prefix="Crypto"
        )
    return _crypto_pool


def set_crypto_executor(executor: ThreadPoolExecutor):
    global _crypto_pool
    _crypto_pool = executor


def create_crypto_executor() -> ThreadPoolExecutor:
    return ThreadPoolExecutor(
        max_workers=1,
        thread_name_prefix="Crypto"
    )