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


class GetOnrampQuote:
    async def get_onramp_quote(
        self: pyrogram.Client,
        provider: str,
        crypto_currency: str,
        base_currency: str,
        base_amount: str | None = None,
        crypto_amount: str | None = None,
        payment_method: str | None = None,
    ) -> raw.base.OnrampQuote:
        """Request a price quote for purchasing cryptocurrency via an onramp provider.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            provider (``str``):
                The onramp provider ID.

            crypto_currency (``str``):
                The cryptocurrency code (e.g. "TON").

            base_currency (``str``):
                The fiat currency code (e.g. "USD").

            base_amount (``str``, *optional*):
                The fiat currency amount to spend.

            crypto_amount (``str``, *optional*):
                The cryptocurrency amount to buy.

            payment_method (``str``, *optional*):
                The payment method identifier.

        Returns:
            :obj:`~pyrogram.raw.base.OnrampQuote`: On success, the price quotation is returned.

        Example:
            .. code-block:: python

                # Get quote
                quote = await app.get_onramp_quote(
                    provider="provider_id",
                    crypto_currency="TON",
                    base_currency="USD",
                    base_amount="50",
                )
        """
        return await self.invoke(
            raw.functions.payments.GetOnrampQuote(
                provider=provider,
                crypto_currency=crypto_currency,
                base_currency=base_currency,
                base_amount=base_amount,
                crypto_amount=crypto_amount,
                payment_method=payment_method,
            )
        )
