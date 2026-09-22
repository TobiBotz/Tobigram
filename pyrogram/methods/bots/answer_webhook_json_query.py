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


class AnswerWebhookJSONQuery:
    async def answer_webhook_json_query(
        self: pyrogram.Client,
        query_id: int,
        data: str | raw.base.DataJSON,
    ) -> bool:
        """Answer a custom webhook JSON query (for bots).

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            query_id (``int``):
                Identifier of the custom query.

            data (``str`` | :obj:`~pyrogram.raw.base.DataJSON`):
                JSON-serialized answer to the query or a DataJSON object.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await bot.answer_webhook_json_query(123456, '{"status": "ok"}')
        """
        if isinstance(data, str):
            data = raw.types.DataJSON(data=data)

        return await self.invoke(
            raw.functions.bots.AnswerWebhookJSONQuery(
                query_id=query_id,
                data=data,
            )
        )
