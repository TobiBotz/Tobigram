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


class StartLiveStory:
    async def start_live_story(
        self: pyrogram.Client,
        chat_id: int | str,
        caption: str | None = None,
        privacy_rules: list[raw.base.InputPrivacyRule] | None = None,
        pinned: bool | None = None,
        noforwards: bool | None = None,
        rtmp_stream: bool | None = None,
        messages_enabled: bool | None = None,
        send_paid_messages_stars: int | None = None,
    ) -> raw.types.Updates:
        """Start a live stream broadcast in a story.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            caption (``str``, *optional*):
                Caption for the live stream story.

            privacy_rules (List of :obj:`~pyrogram.raw.base.InputPrivacyRule`, *optional*):
                Privacy rules for who can view the live story.

            pinned (``bool``, *optional*):
                Whether to pin the story to the profile.

            noforwards (``bool``, *optional*):
                Whether to disable forwarding and saving of the live story.

            rtmp_stream (``bool``, *optional*):
                Whether to use RTMP stream.

            messages_enabled (``bool``, *optional*):
                Whether comments / live chat messages are enabled.

            send_paid_messages_stars (``int``, *optional*):
                Stars required to send live messages.

        Returns:
            :obj:`~pyrogram.raw.types.Updates`: On success, updates object is returned.

        Example:
            .. code-block:: python

                await app.start_live_story(chat_id, caption="Going live!")
        """
        peer = await self.resolve_peer(chat_id)
        rules = privacy_rules or [raw.types.InputPrivacyValueAllowAll()]

        return await self.invoke(
            raw.functions.stories.StartLive(
                peer=peer,
                privacy_rules=rules,
                random_id=self.rnd_id(),
                pinned=pinned,
                noforwards=noforwards,
                rtmp_stream=rtmp_stream,
                caption=caption,
                messages_enabled=messages_enabled,
                send_paid_messages_stars=send_paid_messages_stars,
            )
        )
