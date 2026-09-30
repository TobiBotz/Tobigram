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

import random
from datetime import datetime

import pyrogram
from pyrogram import raw, utils


class StartGroupCall:
    async def start_group_call(
        self: pyrogram.Client,
        chat_id: int | str,
        title: str | None = None,
        schedule_date: datetime | int | None = None,
        rtmp_stream: bool | None = None,
    ) -> raw.base.Updates:
        """Start or schedule a group voice chat or live stream in a chat.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            title (``str``, *optional*):
                Title of the voice chat or live stream.

            schedule_date (:py:obj:`~datetime.datetime` | ``int``, *optional*):
                Schedule date for the group call. If provided, the call will be scheduled.

            rtmp_stream (``bool``, *optional*):
                Pass True if this group call will be an RTMP live stream (e.g. for OBS).

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: On success, updates are returned.

        Example:
            .. code-block:: python

                # Start an instant Voice Chat
                await app.start_group_call(chat_id, title="Community Hangout")

                # Start an RTMP Live Stream for OBS
                await app.start_group_call(chat_id, title="Live Event", rtmp_stream=True)
        """
        peer = await self.resolve_peer(chat_id)
        schedule_ts = (
            utils.datetime_to_timestamp(schedule_date)
            if isinstance(schedule_date, datetime)
            else schedule_date
        )

        return await self.invoke(
            raw.functions.phone.CreateGroupCall(
                peer=peer,
                random_id=random.randint(1, 2147483647),
                title=title,
                schedule_date=schedule_ts,
                rtmp_stream=rtmp_stream,
            )
        )
