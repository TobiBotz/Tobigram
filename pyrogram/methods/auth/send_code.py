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

import pyrogram
from pyrogram import raw
from pyrogram import types
from pyrogram.errors import PhoneMigrate, NetworkMigrate

log = logging.getLogger(__name__)


class SendCode:
    async def send_code(
        self: "pyrogram.Client",
        phone_number: str
    ) -> "types.SentCode":
        """Send the confirmation code to the given phone number.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            phone_number (``str``):
                Phone number in international format (includes the country prefix).

        Returns:
            :obj:`~pyrogram.types.SentCode`: On success, an object containing information on the sent confirmation code
            is returned.

        Raises:
            BadRequest: In case the phone number is invalid.
        """
        phone_number = phone_number.strip(" +")

        while True:
            try:
                r = await self.invoke(
                    raw.functions.auth.SendCode(
                        phone_number=phone_number,
                        api_id=self.api_id,
                        api_hash=self.api_hash,
                        settings=raw.types.CodeSettings()
                    )
                )
            except (PhoneMigrate, NetworkMigrate) as e:
                dc_option = await self.get_dc_option(e.value, ipv6=self.ipv6)
                await self.session.stop()

                self.session = await self.get_session(
                    dc_id=e.value,
                    server_address=dc_option.ip_address,
                    port=dc_option.port,
                    export_authorization=False,
                    temporary=True,
                    adopt_as_main=True,
                )

                await self.storage.dc_id(e.value)
                await self.storage.server_address(dc_option.ip_address)
                await self.storage.port(dc_option.port)
                await self.storage.auth_key(self.session.auth_key)
            else:
                return types.SentCode._parse(r)
