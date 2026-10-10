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


class CreateOnrampSession:
    async def create_onramp_session(
        self: pyrogram.Client,
        provider: str,
        crypto_currency: str,
        address: str,
        payment_method: str | None = None,
        base_currency: str | None = None,
        base_amount: str | None = None,
        memo: str | None = None,
        theme: str | None = None,
        success_return_url: str | None = None,
        fail_return_url: str | None = None,
        crypto_amount: str | None = None,
    ) -> raw.base.OnrampSession:
        """Initiate a purchase session with an onramp provider.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            provider (``str``):
                The onramp provider ID.

            crypto_currency (``str``):
                The cryptocurrency code (e.g. "TON").

            address (``str``):
                The target wallet address.

            payment_method (``str``, *optional*):
                The payment method identifier.

            base_currency (``str``, *optional*):
                The fiat currency code (e.g. "USD").

            base_amount (``str``, *optional*):
                The fiat amount to spend.

            memo (``str``, *optional*):
                Optional memo/tag for the transfer.

            theme (``str``, *optional*):
                UI theme ("light" or "dark").

            success_return_url (``str``, *optional*):
                Callback URL on successful purchase.

            fail_return_url (``str``, *optional*):
                Callback URL on failed purchase.

            crypto_amount (``str``, *optional*):
                The cryptocurrency amount to buy.

        Returns:
            :obj:`~pyrogram.raw.base.OnrampSession`: On success, the onramp session details with the checkout URL are returned.

        Example:
            .. code-block:: python

                # Create onramp session
                session = await app.create_onramp_session(
                    provider="provider_id",
                    crypto_currency="TON",
                    address="EQD...",
                    base_currency="USD",
                    base_amount="50",
                )
        """
        return await self.invoke(
            raw.functions.payments.CreateOnrampSession(
                provider=provider,
                crypto_currency=crypto_currency,
                address=address,
                payment_method=payment_method,
                base_currency=base_currency,
                base_amount=base_amount,
                memo=memo,
                theme=theme,
                success_return_url=success_return_url,
                fail_return_url=fail_return_url,
                crypto_amount=crypto_amount,
            )
        )
