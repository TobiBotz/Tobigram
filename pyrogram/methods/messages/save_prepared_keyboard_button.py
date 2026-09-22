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


class SavePreparedKeyboardButton:
    async def save_prepared_keyboard_button(
        self: pyrogram.Client,
        user_id: int | str,
        button: raw.base.KeyboardButton,
    ) -> raw.base.messages.BotPreparedInlineMessage:
        """Store a keyboard button that can be used by a user within a Mini App.

        Stores a keyboard button with type ``requestPeer`` or ``requestWebView``
        that a Mini App user can use. The stored result can be retrieved by the
        user using the ``web_app_send_prepared_message`` Web App event.

        Note:
            This is a Bot API concept that maps to the same MTProto endpoint as
            :meth:`~Client.save_prepared_inline_message`. The ``button`` must be an
            ``InputBotInlineResult`` object that wraps the keyboard button content.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the Mini App user
                to whom the ``web_app_send_prepared_message`` event will be sent.

            button (:obj:`~pyrogram.raw.base.KeyboardButton`):
                A keyboard button object of type ``keyboardButtonRequestPeer``
                or ``keyboardButtonSimpleWebView`` to prepare.

        Returns:
            :obj:`~pyrogram.raw.base.messages.BotPreparedInlineMessage`: The prepared message
            object containing an ``id`` and ``expiration date``.

        Example:
            .. code-block:: python

                from pyrogram.raw.types import KeyboardButtonRequestPeer, RequestPeerTypeUser

                button = KeyboardButtonRequestPeer(
                    text="Pick a user",
                    button_id=1,
                    peer_type=RequestPeerTypeUser(),
                    max_quantity=1,
                )
                prepared = await app.save_prepared_keyboard_button(user_id=user_id, button=button)
        """
        user_peer = await self.resolve_peer(user_id)

        # Bot API savePreparedKeyboardButton is backed by the same MTProto endpoint
        # (messages.savePreparedInlineMessage). We wrap the button as an inline result.
        r = await self.invoke(
            raw.functions.messages.SavePreparedInlineMessage(
                result=raw.types.InputBotInlineResultGame(
                    id="keyboard_button",
                    short_name="",
                    send_message=raw.types.InputBotInlineMessageGame(
                        reply_markup=raw.types.ReplyInlineMarkup(
                            rows=[raw.types.KeyboardButtonRow(buttons=[button])]
                        )
                        if button is not None
                        else None,
                    ),
                ),
                user_id=user_peer,
                peer_types=None,
            )
        )

        return r
