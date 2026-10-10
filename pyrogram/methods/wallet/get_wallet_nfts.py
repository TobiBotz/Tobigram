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


class GetWalletNfts:
    async def get_wallet_nfts(
        self: pyrogram.Client,
        offset: str = "",
        limit: int = 100,
    ) -> raw.base.wallet.NftItems:
        """Fetch NFT items owned by the current wallet.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            offset (``str``, *optional*):
                Offset for pagination. Defaults to "".

            limit (``int``, *optional*):
                Number of NFT items to retrieve. Defaults to 100.

        Returns:
            :obj:`~pyrogram.raw.base.wallet.NftItems`: On success, the NFT items collection is returned.

        Example:
            .. code-block:: python

                nfts = await app.get_wallet_nfts()
                print(nfts)
        """
        return await self.invoke(
            raw.functions.wallet.GetNfts(
                offset=offset,
                limit=limit,
            )
        )
