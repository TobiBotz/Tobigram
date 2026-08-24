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

from typing import List, Optional, Union

import pyrogram
from pyrogram import enums, types, utils

from .edit_ephemeral_message import edit_ephemeral


class EditEphemeralMessageText:
    async def edit_ephemeral_message_text(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        receiver_id: Union[int, str],
        message_id: int,
        text: Optional[str] = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: Optional[List["types.MessageEntity"]] = None,
        rich_message: Optional["types.InputRichMessage"] = None,
        reply_markup: Optional["types.InlineKeyboardMarkup"] = None,
        welcome: Optional[bool] = None,
    ) -> Optional["types.Message"]:
        """Edit the text of an ephemeral message.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            receiver_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the user the ephemeral
                message was sent to.

            message_id (``int``):
                Identifier of the ephemeral message to edit.

            text (``str``, *optional*):
                New text of the message. Required if *rich_message* is not given.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes.

            entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in message text, which can be
                specified instead of *parse_mode*.

            rich_message (:obj:`~pyrogram.types.InputRichMessage`, *optional*):
                New rich content of the message. Overrides *text*. Unlike the send
                methods this takes the built object rather than a string, because a
                rich message that has to be composed is composed once and edited many
                times.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An inline keyboard.

            welcome (``bool``, *optional*):
                Pass True when editing a stored welcome message rather than one that was
                delivered once.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the edited message is returned.

        Example:
            .. code-block:: python

                await app.edit_ephemeral_message_text(
                    chat_id, receiver_id, message_id, "New text"
                )
        """
        if rich_message is not None:
            return await edit_ephemeral(
                self, chat_id, receiver_id, message_id,
                rich_message=rich_message.write(),
                reply_markup=reply_markup,
                welcome=welcome,
            )

        message, parsed_entities = (
            await utils.parse_text_entities(self, text, parse_mode, entities)
        ).values()

        return await edit_ephemeral(
            self, chat_id, receiver_id, message_id,
            message=message,
            entities=parsed_entities,
            reply_markup=reply_markup,
            welcome=welcome,
        )
