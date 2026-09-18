import asyncio
import io
import os
from unittest.mock import AsyncMock, patch

import pytest
from pyrogram.methods.advanced.save_file import SaveFile
from pyrogram.methods.rate_limiter import TokenBucket


class DummyStorage:
    async def dc_id(self):
        return 2


class DummySession:
    def __init__(self):
        self.invoke = AsyncMock(return_value=True)


class DummyMe:
    def __init__(self, is_bot: bool = False, is_premium: bool = False):
        self.is_bot = is_bot
        self.is_premium = is_premium


class DummyClient(SaveFile):
    def __init__(self, is_bot: bool = False, is_premium: bool = False):
        self.storage = DummyStorage()
        self.me = DummyMe(is_bot=is_bot, is_premium=is_premium)
        self.loop = asyncio.get_event_loop()
        self.read_ahead_slots = asyncio.Semaphore(4)
        self.executor = None
        self.save_file_semaphore = asyncio.Semaphore(1)

    def rnd_id(self):
        return 12345

    def _media_pool(self, dc_id, pool_size):
        class PoolContext:
            async def __aenter__(self):
                session = DummySession()
                future = asyncio.Future()
                future.set_result([session])
                return future

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        return PoolContext()


@pytest.mark.asyncio
async def test_save_file_pacer_token_bucket_user():
    client = DummyClient(is_bot=False, is_premium=False)
    data = b"0" * (512 * 1024 * 2)  # 2 parts (1MB total with 512KB parts)
    bio = io.BytesIO(data)

    with patch(
        "pyrogram.methods.advanced.save_file.TokenBucket", wraps=TokenBucket
    ) as mock_bucket_cls:
        res = await client.save_file(bio)
        assert res is not None
        assert mock_bucket_cls.called
        _, kwargs = mock_bucket_cls.call_args
        assert kwargs["rate"] == 120
        assert kwargs["burst"] == 8


@pytest.mark.asyncio
async def test_save_file_pacer_token_bucket_premium():
    client = DummyClient(is_bot=False, is_premium=True)
    data = b"0" * (512 * 1024 * 2)
    bio = io.BytesIO(data)

    with patch(
        "pyrogram.methods.advanced.save_file.TokenBucket", wraps=TokenBucket
    ) as mock_bucket_cls:
        res = await client.save_file(bio)
        assert res is not None
        assert mock_bucket_cls.called
        _, kwargs = mock_bucket_cls.call_args
        assert kwargs["rate"] == 300
        assert kwargs["burst"] == 8


@pytest.mark.asyncio
async def test_save_file_pacer_token_bucket_bot():
    client = DummyClient(is_bot=True, is_premium=False)
    data = b"0" * (512 * 1024 * 2)
    bio = io.BytesIO(data)

    with patch.dict(os.environ, {"TOBIGRAM_UPLOAD_RATE_BOT": "150"}):
        with patch(
            "pyrogram.methods.advanced.save_file.TokenBucket", wraps=TokenBucket
        ) as mock_bucket_cls:
            res = await client.save_file(bio)
            assert res is not None
            assert mock_bucket_cls.called
            _, kwargs = mock_bucket_cls.call_args
            assert kwargs["rate"] == 150
            assert kwargs["burst"] == 8


@pytest.mark.asyncio
async def test_save_file_pacer_token_bucket_env_override():
    client = DummyClient(is_bot=False, is_premium=False)
    data = b"0" * (512 * 1024 * 2)
    bio = io.BytesIO(data)

    with patch.dict(os.environ, {"TOBIGRAM_UPLOAD_RATE_USER": "200"}):
        with patch(
            "pyrogram.methods.advanced.save_file.TokenBucket", wraps=TokenBucket
        ) as mock_bucket_cls:
            res = await client.save_file(bio)
            assert res is not None
            assert mock_bucket_cls.called
            _, kwargs = mock_bucket_cls.call_args
            assert kwargs["rate"] == 200
            assert kwargs["burst"] == 8
