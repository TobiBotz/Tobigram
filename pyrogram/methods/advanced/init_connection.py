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


class InitConnection:
    async def init_connection(
        self: pyrogram.Client,
        query: raw.core.TLObject,
        api_id: int | None = None,
        device_model: str | None = None,
        system_version: str | None = None,
        app_version: str | None = None,
        system_lang_code: str | None = None,
        lang_pack: str = "",
        lang_code: str | None = None,
        proxy: raw.base.InputClientProxy | None = None,
        params: raw.base.JSONValue | None = None,
    ) -> Any:
        """Initialize connection with client information wrapping a query.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            query (Any function from :obj:`~pyrogram.raw.functions`):
                The query to invoke.

            api_id (``int``, *optional*):
                Application identifier. Defaults to client's api_id.

            device_model (``str``, *optional*):
                Device model. Defaults to client's device_model.

            system_version (``str``, *optional*):
                Operating system version. Defaults to client's system_version.

            app_version (``str``, *optional*):
                Application version. Defaults to client's app_version.

            system_lang_code (``str``, *optional*):
                OS language code. Defaults to client's lang_code.

            lang_pack (``str``, *optional*):
                Platform identifier. Defaults to empty string.

            lang_code (``str``, *optional*):
                Language code. Defaults to client's lang_code.

            proxy (:obj:`~pyrogram.raw.base.InputClientProxy`, *optional*):
                Info about an MTProto proxy.

            params (:obj:`~pyrogram.raw.base.JSONValue`, *optional*):
                Additional initConnection parameters.

        Returns:
            Any object from :obj:`~pyrogram.raw.types`: On success, query result is returned.
        """
        return await self.invoke(
            raw.functions.InitConnection(
                api_id=api_id or self.api_id,
                device_model=device_model or self.device_model,
                system_version=system_version or self.system_version,
                app_version=app_version or self.app_version,
                system_lang_code=system_lang_code or self.lang_code,
                lang_pack=lang_pack,
                lang_code=lang_code or self.lang_code,
                query=query,
                proxy=proxy,
                params=params,
            )
        )
