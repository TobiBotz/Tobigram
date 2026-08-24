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

from typing import Optional, Union

from pyrogram import raw, types
from pyrogram.enums import RichButtonStyle
from pyrogram.types.bots_and_keyboards.inline_keyboard_button import (
    read_button_type,
    write_button_type,
)

from ..input_content.input_rich_block import _to_rich_text
from ..object import Object


class RichMessageButton(Object):
    """A button in a rich formatted message.

    Exactly one of the optional fields other than *style* must be used to specify
    the type of the button.

    Parameters:
        text (``str`` | :obj:`~pyrogram.raw.base.RichText` | :obj:`~pyrogram.types.RichText`):
            Text of the button. May contain only plain text,
            :obj:`~pyrogram.types.RichTextCustomEmoji` and
            :obj:`~pyrogram.types.RichTextDateTime` entities.

        style (:obj:`~pyrogram.enums.RichButtonStyle`, *optional*):
            Style of the button. Defaults to
            :attr:`~pyrogram.enums.RichButtonStyle.DEFAULT`, an app-specific style.

        url (``str``, *optional*):
            HTTP or tg:// URL to be opened when the button is pressed.

        callback_data (``str`` | ``bytes``, *optional*):
            Data to be sent in a callback query to the bot when the button is
            pressed, 1-64 bytes.

        web_app (:obj:`~pyrogram.types.WebAppInfo`, *optional*):
            Description of the `Web App <https://core.telegram.org/bots/webapps>`_
            that will be launched when the user presses the button.

        login_url (:obj:`~pyrogram.types.LoginUrl`, *optional*):
            An HTTPS URL used to automatically authorize the user. Not supported
            for ephemeral messages.

        switch_inline_query (``str``, *optional*):
            If set, pressing the button will prompt the user to select one of their
            chats, open that chat and insert the bot's username and the specified
            inline query in the input field.

        switch_inline_query_current_chat (``str``, *optional*):
            If set, pressing the button will insert the bot's username and the
            specified inline query in the current chat's input field.

        switch_inline_query_chosen_chat (:obj:`~pyrogram.types.SwitchInlineQueryChosenChat`, *optional*):
            If set, pressing the button prompts the user to select one of their chats
            of the specified type, opens that chat and inserts the bot username and an
            optional inline query in the input field.

        copy_text (:obj:`~pyrogram.types.CopyTextButton`, *optional*):
            A button that copies the specified text to the clipboard.

        disabled (:obj:`~pyrogram.types.DisabledButton`, *optional*):
            If set, then the button is disabled and does nothing.
    """

    _FIELDS = (
        "url",
        "callback_data",
        "web_app",
        "login_url",
        "switch_inline_query",
        "switch_inline_query_current_chat",
        "switch_inline_query_chosen_chat",
        "copy_text",
        "disabled",
    )

    def __init__(
        self,
        text: Union[str, "raw.base.RichText", "types.RichText"],
        style: RichButtonStyle = RichButtonStyle.DEFAULT,
        url: Optional[str] = None,
        callback_data: Optional[Union[str, bytes]] = None,
        web_app: Optional["types.WebAppInfo"] = None,
        login_url: Optional["types.LoginUrl"] = None,
        switch_inline_query: Optional[str] = None,
        switch_inline_query_current_chat: Optional[str] = None,
        switch_inline_query_chosen_chat: Optional["types.SwitchInlineQueryChosenChat"] = None,
        copy_text: Optional["types.CopyTextButton"] = None,
        disabled: Optional["types.DisabledButton"] = None,
    ):
        super().__init__()

        self.text = text
        self.style = style
        self.url = url
        self.callback_data = callback_data
        self.web_app = web_app
        self.login_url = login_url
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        self.switch_inline_query_chosen_chat = switch_inline_query_chosen_chat
        self.copy_text = copy_text
        self.disabled = disabled

    @staticmethod
    def _parse_style(style: "raw.base.RichButtonStyle") -> RichButtonStyle:
        if style is None:
            return RichButtonStyle.DEFAULT
        if style.link:
            return RichButtonStyle.LINK
        if style.bg_primary:
            return RichButtonStyle.PRIMARY
        if style.bg_danger:
            return RichButtonStyle.DANGER
        if style.bg_success:
            return RichButtonStyle.SUCCESS
        return RichButtonStyle.DEFAULT

    def _write_style(self) -> Optional["raw.base.RichButtonStyle"]:
        if self.style == RichButtonStyle.LINK:
            return raw.types.RichButtonStyle(link=True)
        if self.style == RichButtonStyle.PRIMARY:
            return raw.types.RichButtonStyle(bg_primary=True)
        if self.style == RichButtonStyle.DANGER:
            return raw.types.RichButtonStyle(bg_danger=True)
        if self.style == RichButtonStyle.SUCCESS:
            return raw.types.RichButtonStyle(bg_success=True)
        return None

    @staticmethod
    async def _parse(
        client, button: Union["raw.types.PageButton", "raw.types.TextButton"]
    ) -> "RichMessageButton":
        fields = read_button_type(button.type)

        return RichMessageButton(
            text=await types.RichText._parse(client, button.text),
            style=RichMessageButton._parse_style(button.style),
            **{k: v for k, v in fields.items() if k in RichMessageButton._FIELDS},
        )

    def _write_type(self) -> "raw.base.InlineButtonType":
        return write_button_type(
            url=self.url,
            callback_data=self.callback_data,
            web_app=self.web_app,
            login_url=self.login_url,
            switch_inline_query=self.switch_inline_query,
            switch_inline_query_current_chat=self.switch_inline_query_current_chat,
            switch_inline_query_chosen_chat=self.switch_inline_query_chosen_chat,
            copy_text=self.copy_text,
            disabled=self.disabled,
        )

    def write(self) -> "raw.types.PageButton":
        return raw.types.PageButton(
            text=_to_rich_text(self.text),
            type=self._write_type(),
            style=self._write_style(),
        )

    def write_text(self) -> "raw.types.TextButton":
        return raw.types.TextButton(
            text=_to_rich_text(self.text),
            type=self._write_type(),
            style=self._write_style(),
        )
