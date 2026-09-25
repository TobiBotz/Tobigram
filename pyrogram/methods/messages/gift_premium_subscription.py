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
from pyrogram import raw, utils


class GiftPremiumSubscription:
    async def gift_premium_subscription(
        self: pyrogram.Client,
        user_id: int | str,
        month_count: int,
        star_count: int,
        text: str | None = None,
        text_parse_mode: str | None = None,
        text_entities: list | None = None,
    ) -> bool:
        """Gift a Telegram Premium subscription to a user.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.

            month_count (``int``):
                Number of months the Telegram Premium subscription will be active for the user;
                must be one of 3, 6, or 12.

            star_count (``int``):
                Number of Telegram Stars to pay for the gift.

            text (``str``, *optional*):
                Text that will be shown along with the service message about the subscription;
                0-255 characters.

            text_parse_mode (``str``, *optional*):
                Mode for parsing entities in the text. See formatting options for more details.

            text_entities (``list``, *optional*):
                Special entities that appear in the gift text.
                It can be specified instead of text_parse_mode.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Gift 3-month Premium to a user for 1000 Stars
                await app.gift_premium_subscription(user_id, month_count=3, star_count=1000)
        """
        parsed_text = None
        if text is not None:
            text_result = await utils.parse_text_entities(
                self, text, text_parse_mode, text_entities
            )
            parsed_text = raw.types.TextWithEntities(
                text=text_result["message"],
                entities=text_result.get("entities") or [],
            )

        invoice = raw.types.InputInvoicePremiumGiftStars(
            user_id=utils.get_input_user(await self.resolve_peer(user_id)),
            months=month_count,
            message=parsed_text,
        )

        form = await self.invoke(raw.functions.payments.GetPaymentForm(invoice=invoice))

        await self.invoke(
            raw.functions.payments.SendStarsForm(
                form_id=form.form_id,
                invoice=invoice,
            )
        )

        return True
