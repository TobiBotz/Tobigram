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


class GetOnrampBaseCurrencies:
    async def get_onramp_base_currencies(
        self: pyrogram.Client,
        provider: str,
        crypto_currency: str,
    ) -> list[str]:
        """Get the supported base fiat currencies for an onramp provider.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            provider (``str``):
                The onramp provider ID.

            crypto_currency (``str``):
                The cryptocurrency code (e.g. "TON").

        Returns:
            List of ``str``: On success, a list of supported fiat currency codes is returned.

        Example:
            .. code-block:: python

                # Get supported base currencies
                currencies = await app.get_onramp_base_currencies(provider="provider_id", crypto_currency="TON")
        """
        return await self.invoke(
            raw.functions.payments.GetOnrampBaseCurrencies(
                provider=provider,
                crypto_currency=crypto_currency,
            )
        )
