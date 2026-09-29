import pytest
from pyrogram import Client, handlers, types


@pytest.mark.asyncio
async def test_stream_events_and_handlers():
    app = Client("test_stream_events", in_memory=True)

    started_events = []
    ended_events = []

    @app.on_stream_start()
    async def handle_start(client, update: types.StreamStarted):
        started_events.append((update.chat_id, update.stream_type, update.media_path))

    @app.on_stream_end()
    async def handle_end(client, update: types.StreamEnded):
        ended_events.append((update.chat_id, update.stream_type))

    import asyncio

    await asyncio.sleep(0.05)

    # Verify handlers registered in dispatcher
    all_handlers = [h for group in app.dispatcher.groups.values() for h in group]
    assert any(isinstance(h, handlers.StreamStartedHandler) for h in all_handlers)
    assert any(isinstance(h, handlers.StreamEndedHandler) for h in all_handlers)

    # Test dispatching StreamStarted
    start_update = types.StreamStarted(
        client=app,
        chat_id=-1001234567890,
        stream_type="video",
        media_path="sample.mp4",
    )
    await app._dispatch_call_update(start_update)

    assert len(started_events) == 1
    assert started_events[0] == (-1001234567890, "video", "sample.mp4")

    # Test dispatching StreamEnded
    end_update = types.StreamEnded(
        client=app,
        chat_id=-1001234567890,
        stream_type="video",
    )
    await app._dispatch_call_update(end_update)

    assert len(ended_events) == 1
    assert ended_events[0] == (-1001234567890, "video")
