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


class EditConnectedStarRefBot:
    async def edit_connected_star_ref_bot(
        self: pyrogram.Client,
        chat_id: int | str,
        link: str,
        revoked: bool | None = None,
    ) -> raw.types.payments.ConnectedStarRefBots:
        """Edit or revoke a connected Star affiliate referral link.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Target channel ID.

            link (``str``):
                The affiliate referral link.

            revoked (``bool``, *optional*):
                Whether to revoke the affiliate link.

        Returns:
            :obj:`~pyrogram.raw.types.payments.ConnectedStarRefBots`: Updated bot information.

        Example:
            .. code-block:: python

                res = await app.edit_connected_star_ref_bot(channel_id, link, revoked=True)
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.payments.EditConnectedStarRefBot(
                peer=peer,
                link=link,
                revoked=revoked,
            )
        )
