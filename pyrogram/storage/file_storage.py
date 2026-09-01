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

import logging
from pathlib import Path

import aiosqlite

from .sqlite_storage import SQLiteStorage

log = logging.getLogger(__name__)


class FileStorage(SQLiteStorage):
    FILE_EXTENSION = ".session"

    def __init__(self, name: str, workdir: Path):
        super().__init__(name, workdir)

    async def open(self):
        path = self.database
        file_exists = path.is_file()

        self.conn = await aiosqlite.connect(str(path), timeout=1)

        if not file_exists:
            await self.create()

            if self.session_string:
                await self.load_session_string(self.session_string)
                await self.conn.commit()
        else:
            await self.update()

        await self.conn.execute("VACUUM")
