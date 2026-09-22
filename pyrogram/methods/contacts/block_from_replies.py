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


class BlockFromReplies:
    async def block_from_replies(
        self: pyrogram.Client,
        msg_id: int,
        delete_message: bool | None = None,
        delete_history: bool | None = None,
        report_spam: bool | None = None,
    ) -> raw.base.Updates:
        """Stop getting notifications about discussion replies of a certain user in @replies.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            msg_id (``int``):
                ID of the message in the @replies chat.

            delete_message (``bool``, *optional*):
                Whether to delete the specified message as well.

            delete_history (``bool``, *optional*):
                Whether to delete all @replies messages from this user as well.

            report_spam (``bool``, *optional*):
                Whether to also report this user for spam.

        Returns:
            :obj:`~pyrogram.raw.base.Updates`: Updates on success.

        Example:
            .. code-block:: python

                await app.block_from_replies(12345, delete_message=True)
        """
        return await self.invoke(
            raw.functions.contacts.BlockFromReplies(
                msg_id=msg_id,
                delete_message=delete_message,
                delete_history=delete_history,
                report_spam=report_spam,
            )
        )
