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


class SetBusinessAccountGiftSettings:
    async def set_business_account_gift_settings(
        self: pyrogram.Client,
        business_connection_id: str,
        show_gift_button: bool,
        accepted_gift_types: raw.base.DisallowedGiftsSettings,
    ) -> bool:
        """Change the privacy settings for incoming gifts of a managed business account.

        Requires the ``can_manage_gifts`` business bot right.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            business_connection_id (``str``):
                Unique identifier of the business connection.

            show_gift_button (``bool``):
                Pass True to show the gift button in the business account's profile;
                pass False to hide it.

            accepted_gift_types (:obj:`~pyrogram.raw.base.DisallowedGiftsSettings`):
                Types of gifts accepted by the business account.
                Use :obj:`~pyrogram.raw.types.DisallowedGiftsSettings` to construct.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                from pyrogram.raw.types import DisallowedGiftsSettings

                await app.set_business_account_gift_settings(
                    connection_id,
                    show_gift_button=True,
                    accepted_gift_types=DisallowedGiftsSettings(
                        disallow_unlimited_stargifts=False,
                        disallow_limited_stargifts=False,
                        disallow_unique_stargifts=False,
                        disallow_premium_gifts=False,
                    ),
                )
        """
        await self.invoke(
            raw.functions.payments.SaveStarGift(
                unsave=not show_gift_button,
                stargift=None,
            ),
            business_connection_id=business_connection_id,
        )

        return True
