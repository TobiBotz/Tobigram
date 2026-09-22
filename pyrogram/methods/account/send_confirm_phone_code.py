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


class SendConfirmPhoneCode:
    async def send_confirm_phone_code(
        self: pyrogram.Client,
        hash: str,
        settings: raw.base.CodeSettings,
    ) -> raw.base.auth.SentCode:
        """Send confirmation code to cancel account deletion.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            hash (``str``):
                The hash from the service notification.

            settings (:obj:`~pyrogram.raw.base.CodeSettings`):
                Phone code settings.

        Returns:
            :obj:`~pyrogram.raw.base.auth.SentCode`: On success, sent code info is returned.
        """
        return await self.invoke(
            raw.functions.account.SendConfirmPhoneCode(
                hash=hash,
                settings=settings,
            )
        )
