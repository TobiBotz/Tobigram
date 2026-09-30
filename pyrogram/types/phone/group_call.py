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

from typing import TYPE_CHECKING

from pyrogram import raw, utils
from ..object import Object

if TYPE_CHECKING:
    from datetime import datetime
    import pyrogram


class GroupCall(Object):
    """Contains information about a group voice chat or live stream.

    Parameters:
        id (``int``):
            Group call identifier.

        access_hash (``int``):
            Group call access hash.

        participants_count (``int``):
            Number of participants currently in the call.

        title (``str``, *optional*):
            Group call title, if set.

        is_active (``bool``, *optional*):
            True if the call is currently active.

        can_start_video (``bool``, *optional*):
            True if you can start video in this call.

        record_video_active (``bool``, *optional*):
            True if video recording is active.

        schedule_date (:py:obj:`~datetime.datetime`, *optional*):
            Point in time (calendar date) when the call is scheduled to start.

        unmuted_video_count (``int``, *optional*):
            Number of unmuted video participants.

        unmuted_video_limit (``int``, *optional*):
            Maximum number of unmuted video participants allowed.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client = None,
        id: int,
        access_hash: int,
        participants_count: int,
        title: str | None = None,
        is_active: bool = True,
        can_start_video: bool | None = None,
        record_video_active: bool | None = None,
        schedule_date: datetime | None = None,
        unmuted_video_count: int | None = None,
        unmuted_video_limit: int | None = None,
    ):
        super().__init__(client)
        self.id = id
        self.access_hash = access_hash
        self.participants_count = participants_count
        self.title = title
        self.is_active = is_active
        self.can_start_video = can_start_video
        self.record_video_active = record_video_active
        self.schedule_date = schedule_date
        self.unmuted_video_count = unmuted_video_count
        self.unmuted_video_limit = unmuted_video_limit

    @classmethod
    def _parse(cls, client: pyrogram.Client, raw_call: raw.base.GroupCall) -> GroupCall | None:
        if isinstance(raw_call, raw.types.GroupCallDiscarded):
            return cls(
                client=client,
                id=raw_call.id,
                access_hash=raw_call.access_hash,
                participants_count=0,
                is_active=False,
            )

        if isinstance(raw_call, raw.types.GroupCall):
            return cls(
                client=client,
                id=raw_call.id,
                access_hash=raw_call.access_hash,
                participants_count=raw_call.participants_count,
                title=raw_call.title,
                is_active=not getattr(raw_call, "flags_schedule_start_subscribed", False),
                can_start_video=getattr(raw_call, "can_start_video", None),
                record_video_active=getattr(raw_call, "record_video_active", None),
                schedule_date=utils.timestamp_to_datetime(raw_call.schedule_date)
                if raw_call.schedule_date
                else None,
                unmuted_video_count=raw_call.unmuted_video_count,
                unmuted_video_limit=raw_call.unmuted_video_limit,
            )

        return None

    async def start_recording(
        self,
        title: str | None = None,
        video: bool | None = None,
        video_portrait: bool | None = None,
    ) -> bool:
        """Bound method *start_recording* of :obj:`~pyrogram.types.GroupCall`.

        Start server-side recording of this group call.

        Parameters:
            title (``str``, *optional*):
                Recording title.

            video (``bool``, *optional*):
                Pass True to record video in addition to audio.

            video_portrait (``bool``, *optional*):
                Pass True to record video in portrait orientation.

        Returns:
            ``bool``: True on success.
        """
        call_input = raw.types.InputGroupCall(id=self.id, access_hash=self.access_hash)
        return await self._client.toggle_group_call_record(
            call_input,
            start=True,
            title=title,
            video=video,
            video_portrait=video_portrait,
        )

    async def stop_recording(self) -> bool:
        """Bound method *stop_recording* of :obj:`~pyrogram.types.GroupCall`.

        Stop server-side recording of this group call.

        Returns:
            ``bool``: True on success.
        """
        call_input = raw.types.InputGroupCall(id=self.id, access_hash=self.access_hash)
        return await self._client.toggle_group_call_record(
            call_input,
            start=False,
        )

    async def discard(self) -> bool:
        """Bound method *discard* of :obj:`~pyrogram.types.GroupCall`.

        End and discard this group call for all members.

        Returns:
            ``bool``: True on success.
        """
        call_input = raw.types.InputGroupCall(id=self.id, access_hash=self.access_hash)
        return await self._client.discard_group_call(call_input)

    async def edit_title(self, title: str) -> bool:
        """Bound method *edit_title* of :obj:`~pyrogram.types.GroupCall`.

        Change the title of this group call.

        Parameters:
            title (``str``):
                New group call title.

        Returns:
            ``bool``: True on success.
        """
        call_input = raw.types.InputGroupCall(id=self.id, access_hash=self.access_hash)
        return await self._client.edit_group_call_title(call_input, title=title)
