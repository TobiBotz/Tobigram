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


class GetWebPagePreview:
    async def get_web_page_preview(
        self: pyrogram.Client,
        message: str,
        entities: list[raw.base.MessageEntity] | None = None,
    ) -> raw.base.MessageMedia:
        """Get a web page preview from a message containing a URL.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            message (``str``):
                The message text that contains the URL to preview.

            entities (List of :obj:`~pyrogram.raw.base.MessageEntity`, *optional*):
                Text entities for the message.

        Returns:
            :obj:`~pyrogram.raw.base.MessageMedia`: The web page preview media.

        Example:
            .. code-block:: python

                preview = await app.get_web_page_preview("Check https://example.com")
        """
        return await self.invoke(
            raw.functions.messages.GetWebPagePreview(message=message, entities=entities)
        )
