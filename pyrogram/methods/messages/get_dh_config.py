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


class GetDhConfig:
    async def get_dh_config(
        self: pyrogram.Client,
        version: int = 0,
        random_length: int = 256,
    ) -> raw.base.messages.DhConfig:
        """Get Diffie-Hellman configuration for end-to-end encryption.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            version (``int``, *optional*):
                Current DH config version (0 to always fetch fresh).

            random_length (``int``, *optional*):
                Length of random bytes to generate. Defaults to 256.

        Returns:
            :obj:`~pyrogram.raw.base.messages.DhConfig`: The DH configuration.

        Example:
            .. code-block:: python

                dh = await app.get_dh_config()
        """
        return await self.invoke(
            raw.functions.messages.GetDhConfig(
                version=version,
                random_length=random_length,
            )
        )
