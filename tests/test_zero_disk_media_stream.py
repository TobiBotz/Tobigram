from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from pyrogram import Client, types
from pyrogram.calls.call_manager import CallsManager
from pyrogram.calls.media_streamer import (
    MediaStreamServer,
    extract_media_info,
    is_telegram_media,
)

try:
    import pytgcalls
    import pytgcalls.types
    import pytgcalls.types.raw
except ImportError:
    import sys
    import types as py_types

    pytgcalls_mod = py_types.ModuleType("pytgcalls")
    types_mod = py_types.ModuleType("pytgcalls.types")
    raw_mod = py_types.ModuleType("pytgcalls.types.raw")

    class MockAudioQuality:
        STUDIO = MagicMock(bitrate=96000)

    class MockVideoQuality:
        FHD_1080p = MagicMock()

    class MockVideoParameters:
        def __init__(self, width=640, height=360, frame_rate=20, adjust_by_height=True):
            self.width = width
            self.height = height
            self.frame_rate = frame_rate
            self.adjust_by_height = adjust_by_height

    class MockMediaStream:
        class Flags:
            IGNORE = 2
            AUTO_DETECT = 1

        def __init__(self, media_path, **kwargs):
            self._media_path = media_path
            self._video_parameters = kwargs.get("video_parameters", None)
            self._audio_parameters = kwargs.get("audio_parameters", None)
            self._video_flags = kwargs.get("video_flags", None)

    types_mod.MediaStream = MockMediaStream
    types_mod.AudioQuality = MockAudioQuality
    types_mod.VideoQuality = MockVideoQuality
    raw_mod.VideoParameters = MockVideoParameters
    types_mod.raw = raw_mod
    pytgcalls_mod.types = types_mod

    sys.modules["pytgcalls"] = pytgcalls_mod
    sys.modules["pytgcalls.types"] = types_mod
    sys.modules["pytgcalls.types.raw"] = raw_mod


def test_is_telegram_media():
    assert not is_telegram_media(None)
    assert not is_telegram_media("music.mp3")
    assert not is_telegram_media("https://live.stream/radio.aac")
    assert not is_telegram_media("rtsp://example.com/live")

    # Message with audio
    msg_audio = types.Message(id=1)
    msg_audio.audio = types.Audio(
        file_id="CQACAgQAAx0CYg-qTQAB",
        file_unique_id="unique_1",
        duration=180,
        file_size=5_000_000,
        mime_type="audio/mpeg",
        file_name="song.mp3",
    )
    assert is_telegram_media(msg_audio)

    # Message with video
    msg_video = types.Message(id=2)
    msg_video.video = types.Video(
        file_id="BAACAgIAAxkBAAEF",
        file_unique_id="unique_2",
        width=1280,
        height=720,
        codec="h264",
        duration=60,
        file_size=10_000_000,
        mime_type="video/mp4",
        file_name="clip.mp4",
    )
    assert is_telegram_media(msg_video)

    # Empty message
    empty_msg = types.Message(id=3)
    assert not is_telegram_media(empty_msg)

    # Message with non-playable document (e.g. zip, txt, pdf)
    msg_zip = types.Message(id=4)
    msg_zip.document = types.Document(
        file_id="zip_fid",
        file_unique_id="uniq_z",
        file_size=1024,
        file_name="archive.zip",
        mime_type="application/zip",
    )
    assert not is_telegram_media(msg_zip)
    assert not is_telegram_media(msg_zip.document)

    msg_txt = types.Message(id=5)
    msg_txt.document = types.Document(
        file_id="txt_fid",
        file_unique_id="uniq_t",
        file_size=500,
        file_name="notes.txt",
        mime_type="text/plain",
    )
    assert not is_telegram_media(msg_txt)
    assert not is_telegram_media(msg_txt.document)

    # Message with playable audio document (e.g. song.flac)
    msg_flac = types.Message(id=6)
    msg_flac.document = types.Document(
        file_id="flac_fid",
        file_unique_id="uniq_f",
        file_size=20_000_000,
        file_name="song.flac",
        mime_type="audio/flac",
    )
    assert is_telegram_media(msg_flac)
    assert is_telegram_media(msg_flac.document)


def test_extract_media_info():
    audio = types.Audio(
        file_id="audio_fid",
        file_unique_id="uniq_a",
        duration=120,
        file_size=3_000_000,
        mime_type="audio/flac",
        file_name="track with spaces.flac",
    )
    target, size, mime, fname, is_vid = extract_media_info(audio)
    assert target is audio
    assert size == 3_000_000
    assert mime == "audio/flac"
    assert fname == "track_with_spaces.flac"
    assert not is_vid

    video = types.Video(
        file_id="vid_fid",
        file_unique_id="uniq_v",
        width=1920,
        height=1080,
        codec="h264",
        duration=300,
        file_size=25_000_000,
        mime_type="video/mp4",
        file_name="movie.mp4",
    )
    target, size, mime, fname, is_vid = extract_media_info(video)
    assert target is video
    assert size == 25_000_000
    assert mime == "video/mp4"
    assert fname == "movie.mp4"
    assert is_vid

    # Document test (e.g. MKV video sent as Document)
    doc_video = types.Document(
        file_id="doc_vid_fid",
        file_unique_id="uniq_dv",
        file_size=50_000_000,
        file_name="film.mkv",
        mime_type="video/x-matroska",
    )
    target, size, mime, fname, is_vid = extract_media_info(doc_video)
    assert target is doc_video
    assert size == 50_000_000
    assert fname == "film.mkv"
    assert is_vid

    # Document test (e.g. FLAC audio sent as Document with generic mime)
    doc_audio = types.Document(
        file_id="doc_aud_fid",
        file_unique_id="uniq_da",
        file_size=20_000_000,
        file_name="song.flac",
        mime_type="application/octet-stream",
    )
    target, size, mime, fname, is_vid = extract_media_info(doc_audio)
    assert target is doc_audio
    assert size == 20_000_000
    assert fname == "song.flac"
    assert "flac" in mime
    assert not is_vid


@pytest.mark.asyncio
async def test_media_stream_server_http_serving():
    app = Client("test_stream_server", in_memory=True)

    fake_chunks = [b"Chunk1-" * 10, b"Chunk2-" * 10, b"Chunk3-" * 10]
    total_data = b"".join(fake_chunks)

    async def fake_stream_media(media, offset=0, limit=0):
        # Slice chunks starting from chunk offset
        for c in fake_chunks[offset:]:
            yield c

    app.stream_media = fake_stream_media

    server = MediaStreamServer(app, host="127.0.0.1", port=0)
    await server.start()
    assert server.is_running

    audio = types.Audio(
        file_id="test_fid",
        file_unique_id="uniq",
        duration=10,
        file_size=len(total_data),
        mime_type="audio/mpeg",
        file_name="stream_test.mp3",
    )

    url, is_video = server.register_media(audio, chat_id=-1001234567890)
    assert url.startswith("http://127.0.0.1:")
    assert "stream_test.mp3" in url
    assert not is_video

    # 1. Test standard GET request via asyncio reader/writer
    port = int(url.split(":")[2].split("/")[0])
    path = "/" + "/".join(url.split("/")[3:])

    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    req = f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
    writer.write(req.encode())
    await writer.drain()

    status_line = await reader.readline()
    assert b"200 OK" in status_line

    headers = {}
    while True:
        line = await reader.readline()
        if line in (b"\r\n", b"\n", b""):
            break
        p = line.decode().split(":", 1)
        headers[p[0].strip().lower()] = p[1].strip()

    assert headers.get("content-type") == "audio/mpeg"
    assert int(headers.get("content-length")) == len(total_data)

    body = await reader.read(len(total_data))
    assert body == total_data
    writer.close()
    await writer.wait_closed()

    # 2. Test Range request
    reader2, writer2 = await asyncio.open_connection("127.0.0.1", port)
    range_req = f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1\r\nRange: bytes=5-14\r\n\r\n"
    writer2.write(range_req.encode())
    await writer2.drain()

    status_line2 = await reader2.readline()
    assert b"206 Partial Content" in status_line2

    headers2 = {}
    while True:
        line = await reader2.readline()
        if line in (b"\r\n", b"\n", b""):
            break
        p = line.decode().split(":", 1)
        headers2[p[0].strip().lower()] = p[1].strip()

    assert headers2.get("content-range") == f"bytes 5-14/{len(total_data)}"
    assert int(headers2.get("content-length")) == 10

    partial_body = await reader2.read(10)
    assert partial_body == total_data[5:15]
    writer2.close()
    await writer2.wait_closed()

    # 3. Test unregister
    server.unregister_chat(-1001234567890)
    reader3, writer3 = await asyncio.open_connection("127.0.0.1", port)
    writer3.write(req.encode())
    await writer3.drain()
    status_line3 = await reader3.readline()
    assert b"404 Not Found" in status_line3
    writer3.close()
    await writer3.wait_closed()

    await server.stop()
    assert not server.is_running


@pytest.mark.asyncio
async def test_calls_manager_auto_bridges_telegram_media():
    app = Client("test_calls_bridge", in_memory=True)
    manager = CallsManager(app)

    from pyrogram import raw

    # Mock peer resolution and engine
    app.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerChannel(channel_id=123456789, access_hash=123)
    )
    fake_full = MagicMock()
    fake_full.full_chat.call = MagicMock(id=999, access_hash=888)
    app.invoke = AsyncMock(return_value=fake_full)

    fake_engine = MagicMock()
    fake_engine.play = AsyncMock()
    fake_engine._app = app
    fake_engine._is_running = True
    manager._engine = fake_engine

    # Message with video
    msg = types.Message(id=10)
    msg.video = types.Video(
        file_id="telegram_video_id",
        file_unique_id="vid_unique",
        width=1280,
        height=720,
        codec="h264",
        duration=120,
        file_size=15_000_000,
        mime_type="video/mp4",
        file_name="vacation.mp4",
    )

    call = await manager.play(-100123456789, msg)
    assert call.is_active

    active_entry = manager._active_calls.get(-100123456789)
    assert active_entry is not None
    media = active_entry["media"]

    # Must be converted to an in-memory stream URL without disk storage
    assert media.path.startswith("http://127.0.0.1:")
    assert "vacation.mp4" in media.path
    assert media.has_video
    assert media.width == 1280
    assert media.height == 720

    # Ensure full quality video and studio audio were configured on PyTgCalls stream
    stream_obj = fake_engine.play.call_args[0][1]
    assert stream_obj._video_parameters.width == 1280
    assert stream_obj._video_parameters.height == 720
    assert stream_obj._audio_parameters.bitrate == 96000  # Studio Quality

    # Leave call cleans up server tokens
    await manager.leave(-100123456789)
    assert -100123456789 not in manager._active_calls

    await manager.stop()


@pytest.mark.asyncio
async def test_calls_manager_full_hd_1080p_quality():
    app = Client("test_calls_fhd", in_memory=True)
    manager = CallsManager(app)

    from pyrogram import raw

    app.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerChannel(channel_id=123456789, access_hash=123)
    )
    fake_full = MagicMock()
    fake_full.full_chat.call = MagicMock(id=1001, access_hash=2002)
    app.invoke = AsyncMock(return_value=fake_full)

    fake_engine = MagicMock()
    fake_engine.play = AsyncMock()
    fake_engine._app = app
    fake_engine._is_running = True
    manager._engine = fake_engine

    # 1080p Full HD video (1920x1080)
    video = types.Video(
        file_id="tg_1080p_video",
        file_unique_id="vid_1080p",
        width=1920,
        height=1080,
        codec="h264",
        duration=300,
        file_size=50_000_000,
        mime_type="video/mp4",
        file_name="movie_1080p.mp4",
    )

    await manager.play(-100123456789, video)

    stream_obj = fake_engine.play.call_args[0][1]
    # Check 1080p Full HD parameters
    assert stream_obj._video_parameters.width == 1920
    assert stream_obj._video_parameters.height == 1080
    assert stream_obj._video_parameters.frame_rate == 30
    assert stream_obj._audio_parameters.bitrate == 96000  # Studio Quality 96kHz

    await manager.leave(-100123456789)
    await manager.stop()
