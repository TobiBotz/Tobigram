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

# ***************************
# GENERATED FILE - DO NOT EDIT
# Source: tl:messages.summarizeText
# ***************************

from typing import Union, Optional

import pyrogram
from pyrogram import raw
from pyrogram import types


class SummarizeText:
    async def summarize_text(
        self: "pyrogram.Client",
        peer: Optional[Union[int, str]] = None,
        id: Optional[int] = None,
        to_lang: Optional[str] = None,
        tone: Optional[str] = None,
    ) -> "raw.types.TextWithEntities":
        """Summarize text content using AI.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            peer (Union[int, str]): Chat from which to get the source message
            id (int): Message ID to summarize
            to_lang (str): Target language for the summary
            tone (str): AI summary tone preset

        Returns:
            :obj:`~pyrogram.raw.types.TextWithEntities`

        Example:
            .. code-block:: python

                await app.summarize_text(...)
        """

        r = await self.invoke(
            raw.functions.messages.summarizeText(
                peer=await self.resolve_peer(peer),
                id=id,
                to_lang=to_lang,
                tone=tone,
            )
        )
