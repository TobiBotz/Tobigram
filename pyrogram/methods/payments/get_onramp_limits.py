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


class GetOnrampLimits:
    async def get_onramp_limits(
        self: pyrogram.Client,
        provider: str,
        crypto_currency: str,
        base_currency: str,
        payment_method: str | None = None,
    ) -> raw.base.OnrampLimits:
        """Get transaction limits for an onramp provider and currency pair.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            provider (``str``):
                The onramp provider ID.

            crypto_currency (``str``):
                The cryptocurrency code (e.g. "TON").

            base_currency (``str``):
                The fiat currency code (e.g. "USD").

            payment_method (``str``, *optional*):
                The payment method identifier.

        Returns:
            :obj:`~pyrogram.raw.base.OnrampLimits`: On success, the transaction limits are returned.

        Example:
            .. code-block:: python

                # Get limits
                limits = await app.get_onramp_limits(provider="provider_id", crypto_currency="TON", base_currency="USD")
        """
        return await self.invoke(
            raw.functions.payments.GetOnrampLimits(
                provider=provider,
                crypto_currency=crypto_currency,
                base_currency=base_currency,
                payment_method=payment_method,
            )
        )
