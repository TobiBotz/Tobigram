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
from typing import TYPE_CHECKING

from pyrogram import raw
from pyrogram.types.phone import CallState, GroupCall, MediaStream, StreamEnded, StreamStarted

if TYPE_CHECKING:
    import pyrogram

log = logging.getLogger(__name__)


class CallsManager:
    """Internal WebRTC and Voice Chat lifecycle manager for Pyrogram."""

    def __init__(self, client: pyrogram.Client):
        self._client = client
        self._is_running = False
        self._engine = None
        self._active_calls: dict[int, dict] = {}
        self._lock = asyncio.Lock()

    def _init_engine(self):
        if self._engine is not None:
            return self._engine

        try:
            from pytgcalls import PyTgCalls

            self._engine = PyTgCalls(self._client)
            return self._engine
        except ImportError:
            pass

        try:
            import ntgcalls

            self._engine = ntgcalls.NTgCalls()
            self._setup_listeners()
            return self._engine
        except ImportError:
            raise ImportError(
                "py-tgcalls or ntgcalls is required for native voice chat streaming. "
                "Install it using `pip install tobigram[calls]`."
            )

    def _setup_listeners(self):
        if not self._engine:
            return

        try:
            if hasattr(self._engine, "on_stream_end"):

                @self._engine.on_stream_end()
                async def _on_stream_end(chat_id: int, stream_type: str):
                    await self._client._dispatch_call_update(
                        StreamEnded(
                            client=self._client,
                            chat_id=chat_id,
                            stream_type=stream_type or "audio",
                        )
                    )
        except Exception:
            pass

    async def start(self):
        async with self._lock:
            if not self._is_running:
                self._is_running = True

    async def stop(self):
        async with self._lock:
            if self._is_running:
                for chat_id in list(self._active_calls.keys()):
                    try:
                        await self.leave(chat_id)
                    except Exception:
                        pass
                if self._engine:
                    try:
                        if hasattr(self._engine, "stop"):
                            await self._engine.stop()
                    except Exception:
                        pass
                self._is_running = False

    async def play(
        self,
        chat_id: int | str,
        media: str | MediaStream,
    ) -> GroupCall:
        """Stream media into group voice chat."""
        peer = await self._client.resolve_peer(chat_id)
        numeric_chat_id = utils_get_chat_id(peer)

        if isinstance(media, str):
            media = MediaStream(media)

        engine = self._init_engine()

        # Step 1: Fetch active group call
        full_chat = await self._client.invoke(
            raw.functions.channels.GetFullChannel(channel=peer)
            if isinstance(peer, raw.types.InputPeerChannel)
            else raw.functions.messages.GetFullChat(chat_id=peer.chat_id)
        )

        call_info = full_chat.full_chat.call
        if not call_info or isinstance(call_info, raw.types.InputGroupCall):
            input_call = call_info
        else:
            raise ValueError(
                f"No active Voice Chat found in {chat_id}. Please start a voice chat first."
            )

        # Step 2: Join Group Call via Engine
        self._active_calls[numeric_chat_id] = {
            "media": media,
            "state": CallState.CONNECTING,
            "call_id": input_call.id if hasattr(input_call, "id") else 0,
        }

        try:
            # Check if engine is PyTgCalls
            if hasattr(engine, "play") and hasattr(engine, "_app"):
                if not getattr(engine, "_is_running", False):
                    await engine.start()
                from pytgcalls.types import MediaStream as TgMediaStream

                if media.video:
                    stream_obj = TgMediaStream(media.path)
                else:
                    stream_obj = TgMediaStream(
                        media.path,
                        video_flags=TgMediaStream.Flags.IGNORE,
                    )

                await engine.play(numeric_chat_id, stream_obj)
            elif hasattr(engine, "play"):
                await engine.play(numeric_chat_id, media.path)
            self._active_calls[numeric_chat_id]["state"] = CallState.PLAYING
            try:
                await self._client._dispatch_call_update(
                    StreamStarted(
                        client=self._client,
                        chat_id=numeric_chat_id,
                        stream_type="video" if media.video else "audio",
                        media_path=media.path,
                    )
                )
            except Exception as dispatch_err:
                log.debug(f"Error dispatching StreamStarted: {dispatch_err}")
        except Exception as e:
            self._active_calls[numeric_chat_id]["state"] = CallState.ENDED
            log.exception(f"Error streaming to voice chat in {chat_id}: {e}")
            raise e

        return GroupCall(
            client=self._client,
            id=getattr(input_call, "id", 0),
            access_hash=getattr(input_call, "access_hash", 0),
            participants_count=1,
            is_active=True,
        )

    async def leave(self, chat_id: int | str) -> bool:
        """Leave group voice chat."""
        peer = await self._client.resolve_peer(chat_id)
        numeric_chat_id = utils_get_chat_id(peer)

        if self._engine:
            try:
                if hasattr(self._engine, "leave_call"):
                    await self._engine.leave_call(numeric_chat_id)
                elif hasattr(self._engine, "leave"):
                    await self._engine.leave(numeric_chat_id)
            except Exception:
                pass

        self._active_calls.pop(numeric_chat_id, None)
        return True

    async def pause(self, chat_id: int | str) -> bool:
        peer = await self._client.resolve_peer(chat_id)
        numeric_chat_id = utils_get_chat_id(peer)
        if self._engine:
            if hasattr(self._engine, "pause_stream"):
                await self._engine.pause_stream(numeric_chat_id)
            elif hasattr(self._engine, "pause"):
                await self._engine.pause(numeric_chat_id)
        if numeric_chat_id in self._active_calls:
            self._active_calls[numeric_chat_id]["state"] = CallState.PAUSED
        return True

    async def resume(self, chat_id: int | str) -> bool:
        peer = await self._client.resolve_peer(chat_id)
        numeric_chat_id = utils_get_chat_id(peer)
        if self._engine:
            if hasattr(self._engine, "resume_stream"):
                await self._engine.resume_stream(numeric_chat_id)
            elif hasattr(self._engine, "resume"):
                await self._engine.resume(numeric_chat_id)
        if numeric_chat_id in self._active_calls:
            self._active_calls[numeric_chat_id]["state"] = CallState.PLAYING
        return True

    async def change_volume(self, chat_id: int | str, volume: int) -> bool:
        peer = await self._client.resolve_peer(chat_id)
        numeric_chat_id = utils_get_chat_id(peer)
        volume = max(0, min(volume, 200))
        if self._engine:
            if hasattr(self._engine, "change_volume_call"):
                await self._engine.change_volume_call(numeric_chat_id, volume)
            elif hasattr(self._engine, "change_volume"):
                await self._engine.change_volume(numeric_chat_id, volume)
        return True

    def get_call_state(self, chat_id: int | str) -> CallState:
        peer_id = (
            int(chat_id) if isinstance(chat_id, int) or str(chat_id).lstrip("-").isdigit() else 0
        )
        if peer_id in self._active_calls:
            return self._active_calls[peer_id].get("state", CallState.IDLE)
        return CallState.IDLE


def utils_get_chat_id(peer: raw.base.InputPeer) -> int:
    if isinstance(peer, raw.types.InputPeerChannel):
        return int(f"-100{peer.channel_id}")
    if isinstance(peer, raw.types.InputPeerChat):
        return -peer.chat_id
    if isinstance(peer, raw.types.InputPeerUser):
        return peer.user_id
    return 0
