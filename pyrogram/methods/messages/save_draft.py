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


class SaveDraft:
    async def save_draft(
        self: pyrogram.Client,
        chat_id: int | str,
        message: str,
        no_webpage: bool | None = None,
        invert_media: bool | None = None,
        reply_to: raw.base.InputReplyTo | None = None,
        entities: list[raw.base.MessageEntity] | None = None,
        media: raw.base.InputMedia | None = None,
    ) -> bool:
        """Save a message draft.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message (``str``):
                The draft message text.

            no_webpage (``bool``, *optional*):
                If True, disables link previews for links in this draft.

            invert_media (``bool``, *optional*):
                If True, inverts the position of the media (above/below the caption).

            reply_to (:obj:`~pyrogram.raw.base.InputReplyTo`, *optional*):
                The message to reply to.

            entities (List of :obj:`~pyrogram.raw.base.MessageEntity`, *optional*):
                Text entities (bold, italic, etc.) in the draft.

            media (:obj:`~pyrogram.raw.base.InputMedia`, *optional*):
                Media attached to the draft.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.save_draft("me", "My draft text")
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.messages.SaveDraft(
                peer=peer,
                message=message,
                no_webpage=no_webpage,
                invert_media=invert_media,
                reply_to=reply_to,
                entities=entities,
                media=media,
            )
        )
