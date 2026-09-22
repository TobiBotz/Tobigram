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


class DismissSuggestion:
    async def dismiss_suggestion(
        self: pyrogram.Client,
        peer: int | str,
        suggestion: str,
    ) -> bool:
        """Dismiss a suggestion.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            peer (``int`` | ``str``):
                Target peer (e.g. channel ID for pending channel suggestions).

            suggestion (``str``):
                Suggestion to dismiss.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.dismiss_suggestion(channel_id, "autoarchive_popular")
        """
        return bool(
            await self.invoke(
                raw.functions.help.DismissSuggestion(
                    peer=await self.resolve_peer(peer),
                    suggestion=suggestion,
                )
            )
        )
