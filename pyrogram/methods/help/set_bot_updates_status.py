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


class SetBotUpdatesStatus:
    async def set_bot_updates_status(
        self: pyrogram.Client,
        pending_updates_count: int,
        message: str,
    ) -> bool:
        """Informs the server about the number of pending bot updates if they haven't been processed for a long time (bots only).

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            pending_updates_count (``int``):
                Number of pending updates.

            message (``str``):
                Error message, if present.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.set_bot_updates_status(5, "Slow processing")
        """
        return bool(
            await self.invoke(
                raw.functions.help.SetBotUpdatesStatus(
                    pending_updates_count=pending_updates_count,
                    message=message,
                )
            )
        )
