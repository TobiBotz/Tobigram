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


class GetOnrampAvailability:
    async def get_onramp_availability(
        self: pyrogram.Client,
        provider: str,
        crypto_currency: str,
        base_currency: str | None = None,
    ) -> raw.base.OnrampAvailability:
        """Check availability and supported payment methods for an onramp provider.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            provider (``str``):
                The onramp provider ID.

            crypto_currency (``str``):
                The cryptocurrency code (e.g. "TON").

            base_currency (``str``, *optional*):
                The fiat currency code (e.g. "USD").

        Returns:
            :obj:`~pyrogram.raw.base.OnrampAvailability`: On success, the availability details are returned.

        Example:
            .. code-block:: python

                # Check onramp availability
                avail = await app.get_onramp_availability(provider="provider_id", crypto_currency="TON")
        """
        return await self.invoke(
            raw.functions.payments.GetOnrampAvailability(
                provider=provider,
                crypto_currency=crypto_currency,
                base_currency=base_currency,
            )
        )
