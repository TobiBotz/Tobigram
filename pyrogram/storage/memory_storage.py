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
import logging
from pathlib import Path

import aiosqlite

from .sqlite_storage import SQLiteStorage, TEST, PROD

log = logging.getLogger(__name__)


class MemoryStorage(SQLiteStorage):
    def __init__(self, name: str, workdir=None, session_string: Optional[str] = None):
        super().__init__(name, workdir=workdir if workdir is not None else Path.cwd())

        self.session_string = session_string

    async def open(self):
        self.conn = await aiosqlite.connect(":memory:")
        await self.create()

        if self.session_string:
            data = self._decode_session_string(self.session_string)
            await self.dc_id(data["dc_id"])
            await self.test_mode(data["test_mode"])
            await self.auth_key(data["auth_key"])
            await self.user_id(data["user_id"])
            await self.is_bot(data["is_bot"])
            await self.date(0)

            if data["api_id"] is not None:
                if data["server_address"] is not None:
                    await self.server_address(data["server_address"])
                    await self.port(data["port"])
                else:
                    if data["test_mode"]:
                        await self.server_address(TEST[data["dc_id"]])
                        await self.port(80)
                    else:
                        await self.server_address(PROD[data["dc_id"]])
                        await self.port(443)

                await self.api_id(data["api_id"])

    async def delete(self):
        pass
