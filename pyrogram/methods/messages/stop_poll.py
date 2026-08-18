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

from datetime import datetime
from typing import Union, Optional

import pyrogram
from pyrogram import raw
from pyrogram import utils
from pyrogram import types


class StopPoll:
    async def stop_poll(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        reply_markup: Optional["types.InlineKeyboardMarkup"] = None,
        schedule_date: Optional[datetime] = None,
        repeat_period: Optional[int] = None,
        quick_reply_shortcut: Optional[int] = None,
        business_connection_id: Optional[str] = None,
    ) -> "types.Poll":
        """Stop a poll which was sent by you.

        Stopped polls can't be reopened and nobody will be able to vote in it anymore.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_id (``int``):
                Identifier of the original message with the poll.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                New date when the scheduled message will be sent.

            repeat_period (``int``, *optional*):
                New period in seconds for the message to be sent repeatedly.

            quick_reply_shortcut (``int``, *optional*):
                Unique identifier of the quick reply shortcut the message belongs to.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the
                action is taken.

        Returns:
            :obj:`~pyrogram.types.Poll`: On success, the stopped poll with the final results is returned.

        Example:
            .. code-block:: python

                await app.stop_poll(chat_id, message_id)
        """
        poll = (await self.get_messages(chat_id, message_id)).poll

        r = await self.invoke(
            raw.functions.messages.EditMessage(
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                schedule_repeat_period=repeat_period,
                quick_reply_shortcut_id=quick_reply_shortcut,
                peer=await self.resolve_peer(chat_id),
                id=message_id,
                media=raw.types.InputMediaPoll(
                    poll=raw.types.Poll(
                        id=int(poll.id),
                        question=raw.types.TextWithEntities(text="", entities=[]),
                        answers=[],
                        hash=int(poll.id),
                        closed=True
                    )
                ),
                reply_markup=await reply_markup.write(self) if reply_markup else None
            ),
            business_connection_id=business_connection_id
        )

        return await types.Poll._parse(self, r.updates[0])
