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

from typing import Optional

import pyrogram
from pyrogram import raw


async def get_session(client: "pyrogram.Client", dc_id: int):
    if dc_id == await client.storage.dc_id():
        return client

    return await client.get_session(dc_id, is_media=True)


async def invoke_inline(
    client: "pyrogram.Client",
    dc_id: int,
    query: "raw.core.TLObject",
    business_connection_id: Optional[str] = None
):
    session = await get_session(client, dc_id)

    if session is client:
        return await client.invoke(
            query,
            sleep_threshold=client.sleep_threshold,
            business_connection_id=business_connection_id
        )

    if business_connection_id:
        query = raw.functions.InvokeWithBusinessConnection(
            connection_id=business_connection_id,
            query=query
        )

    return await session.invoke(query, sleep_threshold=client.sleep_threshold)
