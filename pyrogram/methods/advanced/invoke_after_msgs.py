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

from typing import Any

import pyrogram
from pyrogram import raw


class InvokeAfterMsgs:
    async def invoke_after_msgs(
        self: pyrogram.Client,
        msg_ids: list[int],
        query: raw.core.TLObject,
    ) -> Any:
        """Invokes a query after successful completion of previous queries.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            msg_ids (List of ``int``):
                List of message identifiers on which a current query depends.

            query (Any function from :obj:`~pyrogram.raw.functions`):
                The query to invoke.

        Returns:
            Any object from :obj:`~pyrogram.raw.types`: On success, query result is returned.
        """
        return await self.invoke(
            raw.functions.InvokeAfterMsgs(
                msg_ids=msg_ids,
                query=query,
            )
        )
