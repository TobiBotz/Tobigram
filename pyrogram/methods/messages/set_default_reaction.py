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


class SetDefaultReaction:
    async def set_default_reaction(
        self: pyrogram.Client,
        reaction: raw.base.Reaction | str | int,
    ) -> bool:
        """Set default quick reaction (e.g. for double-tap).

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            reaction (``raw.base.Reaction`` | ``str`` | ``int``):
                The reaction to set. Can be a Reaction object, an emoji string, or a custom emoji document ID.

        Returns:
            ``bool``: True on success.
        """
        if isinstance(reaction, str):
            reaction = raw.types.ReactionEmoji(emoticon=reaction)
        elif isinstance(reaction, int):
            reaction = raw.types.ReactionCustomEmoji(document_id=reaction)

        return await self.invoke(raw.functions.messages.SetDefaultReaction(reaction=reaction))
