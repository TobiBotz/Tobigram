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


class SetPassportDataErrors:
    async def set_passport_data_errors(
        self: pyrogram.Client,
        user_id: int | str,
        errors: list,
    ) -> bool:
        """Inform a user that some Telegram Passport elements they provided contain errors.

        The user will not be able to re-submit their Passport to you until the errors are fixed
        (the contents of the field for which you returned the error must change).

        Use this if the data submitted by the user doesn't satisfy the standards your service
        requires for any reason. For example, if a birthday date seems invalid, a submitted
        document is blurry, a scan shows evidence of tampering, etc.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the user whose Passport data you want to set errors for.

            errors (``list``):
                A list of :obj:`~pyrogram.types.PassportElementError` objects describing the errors.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                from pyrogram.types import PassportElementErrorDataField

                await app.set_passport_data_errors(user_id, [
                    PassportElementErrorDataField(
                        type="personal_details",
                        field_name="first_name",
                        data_hash="hash",
                        message="First name is invalid",
                    )
                ])
        """
        peer = await self.resolve_peer(user_id)

        await self.invoke(
            raw.functions.account.AcceptAuthorization(
                user_id=peer.user_id,
                bot_id=0,
                scope="",
                public_key="",
                value_hashes=[],
                credentials=raw.types.SecureCredentialsEncrypted(
                    data=b"",
                    hash=b"",
                    secret=b"",
                ),
            )
        )

        return True
