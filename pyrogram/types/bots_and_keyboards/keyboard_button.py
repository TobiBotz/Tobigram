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

from typing import Optional

from pyrogram import raw, types
from pyrogram.enums import ButtonStyle

from ..object import Object


def _admin_rights(rights: Optional["types.ChatAdministratorRights"]):
    if rights is None:
        return None

    return raw.types.ChatAdminRights(
        change_info=rights.can_change_info,
        post_messages=rights.can_post_messages,
        edit_messages=rights.can_edit_messages,
        delete_messages=rights.can_delete_messages,
        ban_users=rights.can_restrict_members,
        invite_users=rights.can_invite_users,
        pin_messages=rights.can_pin_messages,
        add_admins=rights.can_promote_members,
        anonymous=rights.is_anonymous,
        manage_call=rights.can_manage_video_chats,
        other=rights.can_manage_chat,
        manage_topics=rights.can_manage_topics,
        post_stories=rights.can_post_stories,
        edit_stories=rights.can_edit_stories,
        delete_stories=rights.can_delete_stories,
        manage_welcome_messages=rights.can_send_welcome_messages
    )


class KeyboardButton(Object):
    """One button of the reply keyboard.
    For simple text buttons String can be used instead of this object to specify text of the button.
    Optional fields are mutually exclusive.

    Parameters:
        text (``str``):
            Text of the button. If none of the optional fields are used, it will be sent as a message when
            the button is pressed.

        request_contact (``bool``, *optional*):
            If True, the user's phone number will be sent as a contact when the button is pressed.
            Available in private chats only.

        request_location (``bool``, *optional*):
            If True, the user's current location will be sent when the button is pressed.
            Available in private chats only.

        request_users (:obj:`~pyrogram.types.KeyboardButtonRequestUsers`, *optional*):
            If specified, pressing the button will open a list of suitable users. Identifiers of selected users
            will be sent to the bot in a "users_shared" service message. Available in private chats only.

        request_chat (:obj:`~pyrogram.types.KeyboardButtonRequestChat`, *optional*):
            If specified, pressing the button will open a list of suitable chats. Tapping on a chat will send its
            identifier to the bot in a "chat_shared" service message. Available in private chats only.

        request_managed_bot (:obj:`~pyrogram.types.KeyboardButtonRequestManagedBot`, *optional*):
            If specified, pressing the button will offer to create a bot managed by the requesting bot.
            Available in private chats only.

        request_poll (:obj:`~pyrogram.types.KeyboardButtonPollType`, *optional*):
            If specified, the user will be asked to create a poll and send it to the bot when the button is pressed.
            Available in private chats only.

        web_app (:obj:`~pyrogram.types.WebAppInfo`, *optional*):
            If specified, the described `Web App <https://core.telegram.org/bots/webapps>`_ will be launched when the
            button is pressed. The Web App will be able to send a “web_app_data” service message. Available in private
            chats only.

        icon_custom_emoji_id (``str``, *optional*):
            Unique identifier of the custom emoji shown on the button.

        style (:obj:`~pyrogram.enums.ButtonStyle`, *optional*):
            Background style of the button. Defaults to :obj:`~pyrogram.enums.ButtonStyle.DEFAULT`.
    """

    def __init__(
        self,
        text: str,
        request_contact: Optional[bool] = None,
        request_location: Optional[bool] = None,
        request_users: Optional["types.KeyboardButtonRequestUsers"] = None,
        request_chat: Optional["types.KeyboardButtonRequestChat"] = None,
        request_managed_bot: Optional["types.KeyboardButtonRequestManagedBot"] = None,
        request_poll: Optional["types.KeyboardButtonPollType"] = None,
        web_app: Optional["types.WebAppInfo"] = None,
        icon_custom_emoji_id: Optional[str] = None,
        style: "ButtonStyle" = ButtonStyle.DEFAULT
    ):
        super().__init__()

        self.text = str(text)
        self.request_contact = request_contact
        self.request_location = request_location
        self.request_users = request_users
        self.request_chat = request_chat
        self.request_managed_bot = request_managed_bot
        self.request_poll = request_poll
        self.web_app = web_app
        self.icon_custom_emoji_id = icon_custom_emoji_id
        self.style = style

    @staticmethod
    def _read_peer(text: str, t: "raw.base.ButtonType", styling: dict) -> "KeyboardButton":
        peer_type = t.peer_type
        requested = {
            "request_name": getattr(t, "name_requested", None),
            "request_username": getattr(t, "username_requested", None),
            "request_photo": getattr(t, "photo_requested", None)
        }

        if isinstance(peer_type, raw.types.RequestPeerTypeUser):
            return KeyboardButton(
                text=text,
                request_users=types.KeyboardButtonRequestUsers(
                    button_id=t.button_id,
                    user_is_bot=peer_type.bot,
                    user_is_premium=peer_type.premium,
                    max_quantity=t.max_quantity,
                    **requested
                ),
                **styling
            )

        if isinstance(peer_type, raw.types.RequestPeerTypeCreateBot):
            return KeyboardButton(
                text=text,
                request_managed_bot=types.KeyboardButtonRequestManagedBot(
                    button_id=t.button_id,
                    suggested_name=peer_type.suggested_name,
                    suggested_username=peer_type.suggested_username
                ),
                **styling
            )

        is_broadcast = isinstance(peer_type, raw.types.RequestPeerTypeBroadcast)

        return KeyboardButton(
            text=text,
            request_chat=types.KeyboardButtonRequestChat(
                button_id=t.button_id,
                chat_is_channel=is_broadcast,
                chat_is_forum=None if is_broadcast else peer_type.forum,
                chat_has_username=peer_type.has_username,
                chat_is_created=peer_type.creator,
                bot_is_member=None if is_broadcast else peer_type.bot_participant,
                user_administrator_rights=(
                    types.ChatAdministratorRights._parse(peer_type.user_admin_rights)
                ),
                bot_administrator_rights=(
                    types.ChatAdministratorRights._parse(peer_type.bot_admin_rights)
                ),
                request_title=requested["request_name"],
                request_username=requested["request_username"],
                request_photo=requested["request_photo"],
                max_quantity=t.max_quantity
            ),
            **styling
        )

    @staticmethod
    def read(b):
        styling = types.InlineKeyboardButton._with_style(b)
        plain = styling["style"] == ButtonStyle.DEFAULT and styling["icon_custom_emoji_id"] is None

        t = b.type

        if isinstance(t, raw.types.ButtonTypeDefault):
            return b.text if plain else KeyboardButton(text=b.text, **styling)

        if isinstance(t, raw.types.ButtonTypeRequestPhone):
            return KeyboardButton(
                text=b.text,
                request_contact=True,
                **styling
            )

        if isinstance(t, raw.types.ButtonTypeRequestGeoLocation):
            return KeyboardButton(
                text=b.text,
                request_location=True,
                **styling
            )

        if isinstance(t, raw.types.ButtonTypeRequestPoll):
            return KeyboardButton(
                text=b.text,
                request_poll=types.KeyboardButtonPollType(is_quiz=t.quiz),
                **styling
            )

        if isinstance(t, (raw.types.ButtonTypeRequestPeer,
                          raw.types.InputButtonTypeRequestPeer)):
            return KeyboardButton._read_peer(b.text, t, styling)

        if isinstance(t, raw.types.ButtonTypeSimpleWebView):
            return KeyboardButton(
                text=b.text,
                web_app=types.WebAppInfo(
                    url=t.url
                ),
                **styling
            )

    def _peer_request(self):
        if self.request_users:
            request = self.request_users

            return request, raw.types.RequestPeerTypeUser(
                bot=request.user_is_bot,
                premium=request.user_is_premium
            ), request.request_name

        if self.request_managed_bot:
            request = self.request_managed_bot

            return request, raw.types.RequestPeerTypeCreateBot(
                suggested_name=request.suggested_name,
                suggested_username=request.suggested_username
            ), None

        request = self.request_chat
        shared = {
            "creator": request.chat_is_created,
            "has_username": request.chat_has_username,
            "user_admin_rights": _admin_rights(request.user_administrator_rights),
            "bot_admin_rights": _admin_rights(request.bot_administrator_rights)
        }

        if request.chat_is_channel:
            peer_type = raw.types.RequestPeerTypeBroadcast(**shared)
        else:
            peer_type = raw.types.RequestPeerTypeChat(
                bot_participant=request.bot_is_member,
                forum=request.chat_is_forum,
                **shared
            )

        return request, peer_type, request.request_title

    def _to_raw_type(self) -> "raw.base.ButtonType":
        if self.request_contact:
            return raw.types.ButtonTypeRequestPhone()

        if self.request_location:
            return raw.types.ButtonTypeRequestGeoLocation()

        if self.request_poll:
            return raw.types.ButtonTypeRequestPoll(quiz=self.request_poll.is_quiz)

        if self.request_users or self.request_chat or self.request_managed_bot:
            request, peer_type, name_requested = self._peer_request()

            return raw.types.InputButtonTypeRequestPeer(
                button_id=request.button_id,
                peer_type=peer_type,
                max_quantity=getattr(request, "max_quantity", 1),
                name_requested=name_requested,
                username_requested=getattr(request, "request_username", None),
                photo_requested=getattr(request, "request_photo", None)
            )

        if self.web_app:
            return raw.types.ButtonTypeSimpleWebView(url=self.web_app.url)

        return raw.types.ButtonTypeDefault()

    def write(self):
        return raw.types.KeyboardButton(
            text=self.text,
            type=self._to_raw_type(),
            style=types.InlineKeyboardButton._to_raw_style(self)
        )
