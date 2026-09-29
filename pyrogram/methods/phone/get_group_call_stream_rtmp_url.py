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

import pyrogram
from pyrogram import raw


class GetGroupCallStreamRtmpUrl:
    async def get_group_call_stream_rtmp_url(
        self: pyrogram.Client,
        chat_id: int | str,
        revoke: bool | None = None,
        live_story: bool | None = None,
    ) -> raw.base.phone.GroupCallStreamRtmpUrl:
        """Get RTMP streaming URL and Stream Key for broadcasting to a chat (e.g. via OBS).

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target channel or chat.

            revoke (``bool``, *optional*):
                Pass True to revoke the previous stream key and generate a new one.

            live_story (``bool``, *optional*):
                Pass True if streaming for a live story.

        Returns:
            :obj:`~pyrogram.raw.base.phone.GroupCallStreamRtmpUrl`: Contains ``url`` and ``key``.

        Example:
            .. code-block:: python

                rtmp = await app.get_group_call_stream_rtmp_url(channel_id)
                print("Server URL:", rtmp.url)
                print("Stream Key:", rtmp.key)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.phone.GetGroupCallStreamRtmpUrl(
                peer=peer,
                revoke=revoke,
                live_story=live_story,
            )
        )
