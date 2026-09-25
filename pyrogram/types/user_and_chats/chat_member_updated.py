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
from pyrogram import enums, raw, types, utils

from ..object import Object
from ..update import Update
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


class ChatMemberUpdated(Object, Update):
    """Represents changes in the status of a chat member.

    Parameters:
        chat (:obj:`~pyrogram.types.Chat`):
            Chat the user belongs to.

        from_user (:obj:`~pyrogram.types.User`):
            Performer of the action, which resulted in the change.

        date (:py:obj:`~datetime.datetime`):
            Date the change was done.

        old_chat_member (:obj:`~pyrogram.types.ChatMember`, *optional*):
            Previous information about the chat member.

        new_chat_member (:obj:`~pyrogram.types.ChatMember`, *optional*):
            New information about the chat member.

        invite_link (:obj:`~pyrogram.types.ChatInviteLink`, *optional*):
            Chat invite link, which was used by the user to join the chat; for joining by invite link events only.

        via_chat_folder_invite_link (``bool``, *optional*):
            True, if the user joined through a chat folder invite link.

        via_join_request (``bool``, *optional*):
            True, if the user joined the chat after sending a join request and being approved by an administrator.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        chat: types.Chat,
        from_user: types.User,
        date: datetime,
        old_chat_member: types.ChatMember | None = None,
        new_chat_member: types.ChatMember | None = None,
        invite_link: types.ChatInviteLink | None = None,
        via_join_request: bool | None = None,
        via_chat_folder_invite_link: bool | None = None,
    ):
        super().__init__(client)

        self.chat = chat
        self.from_user = from_user
        self.date = date
        self.old_chat_member = old_chat_member
        self.new_chat_member = new_chat_member
        self.invite_link = invite_link
        self.via_join_request = via_join_request
        self.via_chat_folder_invite_link = via_chat_folder_invite_link

    @property
    def user(self) -> types.User | None:
        """The user whose membership status has changed."""
        if self.new_chat_member and self.new_chat_member.user:
            return self.new_chat_member.user
        if self.old_chat_member and self.old_chat_member.user:
            return self.old_chat_member.user
        return None

    @property
    def left_chat_member(self) -> types.User | None:
        """Alias for :attr:`user` when a member has left or was removed from the chat."""
        return self.user if self.is_left else None

    @property
    def is_left(self) -> bool:
        """True if the member left voluntarily, was kicked, or was banned from the chat."""
        if not self.old_chat_member:
            return False

        old_status = self.old_chat_member.status
        if old_status not in {
            enums.ChatMemberStatus.MEMBER,
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.RESTRICTED,
        }:
            return False

        if self.new_chat_member is None:
            return True

        new_status = self.new_chat_member.status
        if new_status in {enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED}:
            return True

        if new_status == enums.ChatMemberStatus.RESTRICTED and not self.new_chat_member.is_member:
            return True

        return False

    @property
    def is_self_left(self) -> bool:
        """True if the user left the chat voluntarily (not removed by an administrator)."""
        if not self.is_left:
            return False
        user = self.user
        return bool(user and self.from_user and user.id == self.from_user.id)

    @property
    def is_kicked(self) -> bool:
        """True if the user was kicked or banned by an administrator."""
        if not self.is_left:
            return False
        user = self.user
        return bool(user and self.from_user and user.id != self.from_user.id)

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        update: raw.types.UpdateChatParticipant | raw.types.UpdateChannelParticipant,
        users: dict[int, raw.types.User],
        chats: dict[int, raw.types.Chat],
    ) -> ChatMemberUpdated:
        chat_id = getattr(update, "chat_id", None) or update.channel_id

        old_chat_member = None
        new_chat_member = None
        invite_link = None
        via_join_request = None

        if update.prev_participant:
            old_chat_member = types.ChatMember._parse(client, update.prev_participant, users, chats)

        if update.new_participant:
            new_chat_member = types.ChatMember._parse(client, update.new_participant, users, chats)

        if update.invite:
            invite_link = types.ChatInviteLink._parse(client, update.invite, users)

            if isinstance(update.invite, raw.types.ChatInvitePublicJoinRequests):
                via_join_request = True

        return ChatMemberUpdated(
            chat=types.Chat._parse_chat(client, chats[chat_id]),
            from_user=types.User._parse(client, users[update.actor_id]),
            via_chat_folder_invite_link=getattr(update, "via_chatlist", None),
            date=utils.timestamp_to_datetime(update.date),
            old_chat_member=old_chat_member,
            new_chat_member=new_chat_member,
            invite_link=invite_link,
            via_join_request=via_join_request,
            client=client,
        )
