#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import asyncio
import logging
import os
import secrets
from typing import TYPE_CHECKING, Any

from pyrogram import types
from pyrogram.file_id import FileId, FileType

if TYPE_CHECKING:
    import pyrogram

log = logging.getLogger(__name__)


def guess_mime_type(filename: str, client: pyrogram.Client | None = None) -> str | None:
    """Guess the MIME type of a file using Client's built-in guess_mime_type."""
    if not filename:
        return None
    if client is not None and hasattr(client, "guess_mime_type"):
        return client.guess_mime_type(filename)
    import pyrogram

    return pyrogram.Client.guess_mime_type(pyrogram.Client, filename)


def is_playable_media(
    mime_or_filename: str, client: pyrogram.Client | None = None
) -> bool:
    """Check if a MIME type or filename represents a playable audio or video format."""
    if not mime_or_filename:
        return False

    value = str(mime_or_filename).lower().strip()
    if "/" in value:
        clean_mime = value.split(";")[0].strip()
        return clean_mime.startswith(("audio/", "video/")) or clean_mime in (
            "application/ogg",
            "application/x-ogg",
        )

    guessed = guess_mime_type(value, client=client)
    if not guessed:
        return False
    clean_guessed = guessed.lower().split(";")[0].strip()
    return clean_guessed.startswith(("audio/", "video/")) or clean_guessed in (
        "application/ogg",
        "application/x-ogg",
    )


def is_playable_document(
    doc: types.Document | Any, client: pyrogram.Client | None = None
) -> bool:
    """Check if a Document is an audio or video media file."""
    mime = getattr(doc, "mime_type", None)
    if mime and is_playable_media(mime, client=client):
        return True

    file_name = getattr(doc, "file_name", None)
    if file_name and is_playable_media(file_name, client=client):
        return True

    return False


def is_telegram_media(obj: Any) -> bool:
    """Check if an object or string represents a playable Telegram media entity."""
    if obj is None:
        return False

    if isinstance(obj, types.Message):
        if any(
            getattr(obj, attr, None) is not None
            for attr in ("audio", "video", "voice", "animation", "video_note")
        ):
            return True
        if obj.document is not None:
            return is_playable_document(obj.document)
        return False

    if isinstance(obj, (types.Audio, types.Video, types.Voice, types.Animation, types.VideoNote)):
        return True

    if isinstance(obj, types.Document):
        return is_playable_document(obj)

    if hasattr(obj, "file_id") and isinstance(getattr(obj, "file_id", None), str):
        if hasattr(obj, "file_name") or hasattr(obj, "mime_type"):
            return is_playable_document(obj)
        return True

    if isinstance(obj, str):
        # Exclude local files, URLs, and pipe/fifo protocols
        if os.path.exists(obj):
            return False
        if obj.startswith(
            ("http://", "https://", "rtmp://", "rtsp://", "fifo:", "pipe:", "tcp://", "udp://")
        ):
            return False
        try:
            FileId.decode(obj)
            return True
        except Exception:
            return False

    return False


def extract_media_info(
    obj: Any,
    is_video: bool | None = None,
    client: pyrogram.Client | None = None,
) -> tuple[Any, int, str, str, bool]:
    """Extract downloadable media object, file size, mime type, clean filename, and video flag.

    Returns:
        (media_obj, file_size, mime_type, file_name, is_video)
    """
    media_target = obj
    file_size = 0
    mime_type = "application/octet-stream"
    file_name = "stream.bin"
    detected_is_video = False

    if isinstance(obj, types.Message):
        preferred_attrs = (
            ("video", "animation", "video_note", "document", "audio", "voice")
            if is_video is True
            else ("audio", "voice", "video", "animation", "video_note", "document")
        )

        for attr in preferred_attrs:
            val = getattr(obj, attr, None)
            if val is not None:
                if attr == "document" and not is_playable_document(val, client=client):
                    continue
                media_target = val
                break
        else:
            raise ValueError(
                "The provided Message does not contain any playable audio or video media."
            )

    if isinstance(media_target, (types.Audio, types.Voice)):
        file_size = getattr(media_target, "file_size", 0) or 0
        is_voice = isinstance(media_target, types.Voice)
        mime_type = getattr(media_target, "mime_type", None) or (
            "audio/ogg" if is_voice else "audio/mpeg"
        )
        file_name = getattr(media_target, "file_name", None) or (
            "voice.ogg" if is_voice else "audio.mp3"
        )
        detected_is_video = False

    elif isinstance(media_target, (types.Video, types.Animation, types.VideoNote)):
        file_size = getattr(media_target, "file_size", 0) or 0
        mime_type = getattr(media_target, "mime_type", None) or "video/mp4"
        file_name = getattr(media_target, "file_name", None) or "video.mp4"
        detected_is_video = True

    elif isinstance(media_target, types.Document):
        if not is_playable_document(media_target, client=client):
            doc_name = getattr(media_target, "file_name", "document")
            raise ValueError(
                f"The Document '{doc_name}' is not a playable audio or video format."
            )
        file_size = getattr(media_target, "file_size", 0) or 0
        file_name = getattr(media_target, "file_name", None) or "document.bin"
        mime_type = getattr(media_target, "mime_type", None)

        if not mime_type or mime_type == "application/octet-stream":
            mime_type = (
                guess_mime_type(file_name, client=client)
                or mime_type
                or "application/octet-stream"
            )

        detected_is_video = (
            (is_video is True)
            or (is_video is None and mime_type.startswith("video/"))
        )

    elif isinstance(media_target, str):
        try:
            fid = FileId.decode(media_target)
            if fid.file_type in (FileType.VIDEO, FileType.ANIMATION, FileType.VIDEO_NOTE):
                detected_is_video = True
                mime_type = "video/mp4"
                file_name = "video.mp4"
            elif fid.file_type == FileType.VOICE:
                detected_is_video = False
                mime_type = "audio/ogg"
                file_name = "voice.ogg"
            else:
                detected_is_video = False
                mime_type = "audio/mpeg"
                file_name = "audio.mp3"
        except Exception:
            pass

    if is_video is not None:
        detected_is_video = is_video

    clean_file_name = os.path.basename(file_name).replace(" ", "_") or "stream.bin"
    return media_target, file_size, mime_type, clean_file_name, detected_is_video


class MediaStreamServer:
    """In-memory zero-disk HTTP stream server for piping Telegram media directly into Voice Chats."""

    def __init__(self, client: pyrogram.Client, host: str = "127.0.0.1", port: int = 0):
        self._client = client
        self._host = host
        self._port = port
        self._server: asyncio.Server | None = None
        self._active_tokens: dict[str, dict[str, Any]] = {}
        self._chat_tokens: dict[int, set[str]] = {}
        self._lock = asyncio.Lock()

    @property
    def is_running(self) -> bool:
        return self._server is not None and self._server.is_serving()

    async def start(self) -> None:
        """Start the local streaming server on an ephemeral loopback port."""
        async with self._lock:
            if self.is_running:
                return

            self._server = await asyncio.start_server(
                self._handle_client,
                self._host,
                self._port,
            )
            sockets = self._server.sockets
            if sockets:
                self._port = sockets[0].getsockname()[1]
            log.info("MediaStreamServer started at http://%s:%d", self._host, self._port)

    async def stop(self) -> None:
        """Stop the local streaming server and release resources."""
        async with self._lock:
            if self._server is not None:
                self._server.close()
                await self._server.wait_closed()
                self._server = None
            self._active_tokens.clear()
            self._chat_tokens.clear()
            log.info("MediaStreamServer stopped")

    def register_media(
        self,
        media: Any,
        chat_id: int | None = None,
        is_video: bool | None = None,
    ) -> tuple[str, bool]:
        """Register a Telegram media object for zero-disk streaming.

        Returns:
            tuple[stream_url: str, detected_is_video: bool]
        """
        target_media, file_size, mime_type, file_name, detected_is_video = extract_media_info(
            media, is_video=is_video, client=self._client
        )
        token = secrets.token_urlsafe(16)

        self._active_tokens[token] = {
            "media": target_media,
            "file_size": file_size,
            "mime_type": mime_type,
            "file_name": file_name,
            "is_video": detected_is_video,
            "chat_id": chat_id,
        }

        if chat_id is not None:
            self._chat_tokens.setdefault(chat_id, set()).add(token)

        stream_url = f"http://{self._host}:{self._port}/stream/{token}/{file_name}"
        return stream_url, detected_is_video

    def unregister_chat(self, chat_id: int) -> None:
        """Unregister all active streams associated with a chat."""
        tokens = self._chat_tokens.pop(chat_id, set())
        for token in tokens:
            self._active_tokens.pop(token, None)

    def unregister_token(self, token: str) -> None:
        """Unregister a specific stream token."""
        entry = self._active_tokens.pop(token, None)
        if entry and entry.get("chat_id") is not None:
            chat_id = entry["chat_id"]
            if chat_id in self._chat_tokens:
                self._chat_tokens[chat_id].discard(token)
                if not self._chat_tokens[chat_id]:
                    self._chat_tokens.pop(chat_id, None)

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            req_line = await reader.readline()
            if not req_line:
                writer.close()
                await writer.wait_closed()
                return

            req_parts = req_line.decode("latin1", errors="ignore").split()
            if len(req_parts) < 2:
                writer.close()
                await writer.wait_closed()
                return

            method, path = req_parts[0].upper(), req_parts[1]

            headers: dict[str, str] = {}
            while True:
                line = await reader.readline()
                if not line or line in (b"\r\n", b"\n"):
                    break
                header_parts = line.decode("latin1", errors="ignore").split(":", 1)
                if len(header_parts) == 2:
                    headers[header_parts[0].strip().lower()] = header_parts[1].strip()

            path_clean = path.split("?")[0].strip("/")
            path_segments = path_clean.split("/")
            if len(path_segments) < 2 or path_segments[0] != "stream":
                writer.write(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return

            token = path_segments[1]
            entry = self._active_tokens.get(token)
            if not entry:
                writer.write(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return

            media = entry["media"]
            file_size = entry["file_size"]
            mime_type = entry["mime_type"]

            range_header = headers.get("range")
            start = 0
            end = (file_size - 1) if file_size > 0 else None
            is_range = False

            if range_header and range_header.startswith("bytes="):
                is_range = True
                spec = range_header[len("bytes=") :].strip()
                if "-" in spec:
                    s_str, e_str = spec.split("-", 1)
                    if s_str:
                        start = int(s_str)
                    if e_str:
                        end = int(e_str)

            if file_size > 0 and end is not None:
                end = min(end, file_size - 1)

            if file_size > 0 and start >= file_size:
                writer.write(
                    f"HTTP/1.1 416 Range Not Satisfiable\r\nContent-Range: bytes */{file_size}\r\n\r\n".encode()
                )
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                return

            content_length = (end - start + 1) if end is not None else None

            resp_lines = []
            if is_range:
                resp_lines.append("HTTP/1.1 206 Partial Content")
                if file_size > 0 and end is not None:
                    resp_lines.append(f"Content-Range: bytes {start}-{end}/{file_size}")
            else:
                resp_lines.append("HTTP/1.1 200 OK")

            resp_lines.append("Accept-Ranges: bytes")
            resp_lines.append(f"Content-Type: {mime_type}")
            if content_length is not None:
                resp_lines.append(f"Content-Length: {content_length}")
            resp_lines.append("Connection: keep-alive")
            resp_lines.append("\r\n")

            header_bytes = "\r\n".join(resp_lines).encode("latin1")
            writer.write(header_bytes)
            await writer.drain()

            if method == "HEAD":
                writer.close()
                await writer.wait_closed()
                return

            chunk_size = 1024 * 1024
            start_chunk = start // chunk_size
            offset_in_first = start % chunk_size
            remaining_bytes = content_length
            is_first = True

            async for chunk in self._client.stream_media(media, offset=start_chunk):
                if is_first:
                    chunk = chunk[offset_in_first:]
                    is_first = False

                if remaining_bytes is not None:
                    if len(chunk) > remaining_bytes:
                        chunk = chunk[:remaining_bytes]
                    remaining_bytes -= len(chunk)

                if chunk:
                    writer.write(chunk)
                    await writer.drain()

                if remaining_bytes is not None and remaining_bytes <= 0:
                    break

        except (ConnectionResetError, BrokenPipeError, asyncio.CancelledError):
            pass
        except Exception as e:
            log.debug("MediaStreamServer client error: %s", e)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
