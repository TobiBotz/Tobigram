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


import pyrogram
from pyrogram import raw


class SetUpgradedGiftColors:
    async def set_upgraded_gift_colors(
        self: "pyrogram.Client", upgraded_gift_colors_id: int, for_profile: bool | None = None
    ) -> bool:
        """Take the colors of an upgraded gift you own as your account colors.

        Unlike :meth:`~pyrogram.Client.set_chat_accent_color`, which takes a palette
        identifier, this takes the identifier of a collectible and is accepted for your
        own account only.

        Requires a Premium account; Telegram answers
        ``[403 PREMIUM_ACCOUNT_REQUIRED]`` otherwise.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            upgraded_gift_colors_id (``int``):
                Identifier of the upgraded gift whose colors to wear.

            for_profile (``bool``, *optional*):
                Pass True to change the profile color instead of the message accent color.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.set_upgraded_gift_colors(gift.owned_gift_id)
        """
        r = await self.invoke(
            raw.functions.account.UpdateColor(
                for_profile=for_profile,
                color=raw.types.InputPeerColorCollectible(collectible_id=upgraded_gift_colors_id),
            )
        )

        return bool(r)
