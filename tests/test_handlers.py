from pyrogram.filters import text
from pyrogram.handlers import (
    CallbackQueryHandler,
    Handler,
    MessageHandler,
)
from pyrogram.handlers import handler as handler_module


async def dummy_callback(client, update):
    pass


def sync_callback(client, update):
    pass


class TestHandler:
    def test_create_with_async_callback(self):
        h = Handler(dummy_callback)
        assert h.callback is dummy_callback
        assert h.filters is None

    def test_create_with_sync_callback(self):
        h = Handler(sync_callback)
        assert h.callback is sync_callback

    def test_create_with_filters(self):
        h = Handler(dummy_callback, filters=text)
        assert h.filters is text

    def test_default_check_returns_true(self):
        h = Handler(dummy_callback)
        assert h.callback is dummy_callback

    async def test_check_with_no_filters(self):
        h = Handler(dummy_callback)
        result = await h.check(None, None)
        assert result is True

    def test_has_check_method(self):
        h = Handler(dummy_callback)
        assert hasattr(h, "check")


class TestMessageHandler:
    def test_create(self):
        h = MessageHandler(dummy_callback)
        assert h.callback is dummy_callback
        assert h.filters is None
        assert isinstance(h, Handler)

    def test_create_with_filters(self):
        h = MessageHandler(dummy_callback, filters=text)
        assert h.filters is text

    def test_inherits_from_handler(self):
        assert issubclass(MessageHandler, Handler)

    def test_signature(self):
        import inspect

        sig = inspect.signature(MessageHandler.__init__)
        params = list(sig.parameters.keys())
        assert "callback" in params
        assert "filters" in params


class TestCallbackQueryHandler:
    def test_create(self):
        h = CallbackQueryHandler(dummy_callback)
        assert h.callback is dummy_callback
        assert h.filters is None
        assert isinstance(h, Handler)

    def test_create_with_filters(self):
        h = CallbackQueryHandler(dummy_callback, filters=text)
        assert h.filters is text

    def test_inherits_from_handler(self):
        assert issubclass(CallbackQueryHandler, Handler)

    def test_signature(self):
        import inspect

        sig = inspect.signature(CallbackQueryHandler.__init__)
        params = list(sig.parameters.keys())
        assert "callback" in params
        assert "filters" in params


class TestHandlerCheck:
    async def test_async_filter(self):
        class AsyncFilter:
            async def __call__(self, client, update):
                return True

        h = Handler(dummy_callback, filters=AsyncFilter())
        assert await h.check(None, None) is True

    async def test_async_filter_blocks(self):
        class AsyncFilter:
            async def __call__(self, client, update):
                return False

        h = Handler(dummy_callback, filters=AsyncFilter())
        assert await h.check(None, None) is False

    async def test_handler_without_filter(self):
        h = Handler(dummy_callback)
        assert await h.check(None, None) is True
