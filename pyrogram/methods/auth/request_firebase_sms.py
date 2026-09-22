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


class RequestFirebaseSms:
    async def request_firebase_sms(
        self: pyrogram.Client,
        phone_number: str,
        phone_code_hash: str,
        safety_net_token: str | None = None,
        play_integrity_token: str | None = None,
        ios_push_secret: str | None = None,
    ) -> bool:
        """Request an SMS verification code via Firebase.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            phone_number (``str``):
                Phone number where to send the code.

            phone_code_hash (``str``):
                Phone code hash returned by send_code.

            safety_net_token (``str``, *optional*):
                SafetyNet JWS token on Android.

            play_integrity_token (``str``, *optional*):
                Play Integrity token on Android.

            ios_push_secret (``str``, *optional*):
                Secret token received via Apple push notification on iOS.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.request_firebase_sms("+1234567890", code_hash, play_integrity_token=token)
        """
        return await self.invoke(
            raw.functions.auth.RequestFirebaseSms(
                phone_number=phone_number,
                phone_code_hash=phone_code_hash,
                safety_net_token=safety_net_token,
                play_integrity_token=play_integrity_token,
                ios_push_secret=ios_push_secret,
            )
        )
