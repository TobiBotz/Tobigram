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


class GetOnrampProviders:
    async def get_onramp_providers(
        self: pyrogram.Client,
        crypto_currency: str | None = None,
    ) -> list[raw.base.OnrampProviderInfo]:
        """Fetch available crypto onramp providers.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            crypto_currency (``str``, *optional*):
                The cryptocurrency code (e.g. "TON").

        Returns:
            List of :obj:`~pyrogram.raw.base.OnrampProviderInfo`: On success, a list of onramp providers is returned.

        Example:
            .. code-block:: python

                # Get available onramp providers
                providers = await app.get_onramp_providers()
        """
        return await self.invoke(
            raw.functions.payments.GetOnrampProviders(
                crypto_currency=crypto_currency,
            )
        )
