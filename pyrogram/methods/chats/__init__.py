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

from .add_chat_members import AddChatMembers
from .archive_chats import ArchiveChats
from .ban_chat_member import BanChatMember
from .close_forum_topic import CloseForumTopic
from .create_channel import CreateChannel
from .create_folder import CreateFolder
from .create_folder_invite_link import CreateFolderInviteLink
from .create_forum_topic import CreateForumTopic
from .create_group import CreateGroup
from .create_supergroup import CreateSupergroup
from .delete_all_message_reactions import DeleteAllMessageReactions
from .delete_channel import DeleteChannel
from .delete_chat_photo import DeleteChatPhoto
from .delete_folder import DeleteFolder
from .delete_folder_invite_link import DeleteFolderInviteLink
from .delete_forum_topic import DeleteForumTopic
from .delete_message_reaction import DeleteMessageReaction
from .delete_supergroup import DeleteSupergroup
from .delete_user_history import DeleteUserHistory
from .edit_folder import EditFolder
from .edit_folder_invite_link import EditFolderInviteLink
from .edit_forum_topic import EditForumTopic
from .get_chat import GetChat
from .get_chat_event_log import GetChatEventLog
from .get_chat_member import GetChatMember
from .get_chat_members import GetChatMembers
from .get_chat_members_count import GetChatMembersCount
from .get_chat_online_count import GetChatOnlineCount
from .get_chat_settings import GetChatSettings
from .get_chats_for_folder_invite_link import GetChatsForFolderInviteLink
from .get_dialogs import GetDialogs
from .get_dialogs_count import GetDialogsCount
from .get_direct_messages_topics import GetDirectMessagesTopics
from .get_direct_messages_topics_by_id import GetDirectMessagesTopicsByID
from .get_folder_invite_links import GetFolderInviteLinks
from .get_folders import GetFolders
from .get_forum_topics import GetForumTopics
from .get_forum_topics_by_id import GetForumTopicsByID
from .get_nearby_chats import GetNearbyChats
from .get_personal_channels import GetPersonalChannels
from .get_send_as_chats import GetSendAsChats
from .get_similar_channels import GetSimilarChannels
from .get_suitable_discussion_chats import GetSuitableDiscussionChats
from .get_top_chats import GetTopChats
from .join_chat import JoinChat
from .join_folder import JoinFolder
from .leave_chat import LeaveChat
from .leave_folder import LeaveFolder
from .mark_chat_unread import MarkChatUnread
from .pin_chat_message import PinChatMessage
from .promote_chat_member import PromoteChatMember
from .restrict_chat_member import RestrictChatMember
from .restrict_sponsored_messages import RestrictSponsoredMessages
from .set_administrator_title import SetAdministratorTitle
from .set_chat_description import SetChatDescription
from .set_chat_permissions import SetChatPermissions
from .set_chat_photo import SetChatPhoto
from .set_chat_protected_content import SetChatProtectedContent
from .set_chat_title import SetChatTitle
from .set_chat_username import SetChatUsername
from .set_send_as_chat import SetSendAsChat
from .set_slow_mode import SetSlowMode
from .toggle_anti_spam import ToggleAntiSpam
from .toggle_auto_translation import ToggleAutoTranslation
from .toggle_forum import ToggleForum
from .toggle_join_to_send import ToggleJoinToSend
from .toggle_participants_hidden import ToggleParticipantsHidden
from .toggle_pre_history_hidden import TogglePreHistoryHidden
from .toggle_signatures import ToggleSignatures
from .toggle_slow_mode import ToggleSlowMode
from .toggle_view_forum_as_messages import ToggleViewForumAsMessages
from .unarchive_chats import UnarchiveChats
from .unban_chat_member import UnbanChatMember
from .unpin_all_chat_messages import UnpinAllChatMessages
from .unpin_chat_message import UnpinChatMessage
from .update_channel_color import UpdateChannelColor


class Chats(
    AddChatMembers,
    ArchiveChats,
    BanChatMember,
    CloseForumTopic,
    CreateChannel,
    CreateFolder,
    CreateFolderInviteLink,
    CreateForumTopic,
    CreateGroup,
    CreateSupergroup,
    DeleteAllMessageReactions,
    DeleteChannel,
    DeleteChatPhoto,
    DeleteFolder,
    DeleteFolderInviteLink,
    DeleteForumTopic,
    DeleteMessageReaction,
    DeleteSupergroup,
    DeleteUserHistory,
    EditFolder,
    EditFolderInviteLink,
    EditForumTopic,
    GetChat,
    GetChatEventLog,
    GetChatMember,
    GetChatMembers,
    GetChatMembersCount,
    GetChatOnlineCount,
    GetChatSettings,
    GetChatsForFolderInviteLink,
    GetDialogs,
    GetDialogsCount,
    GetDirectMessagesTopics,
    GetDirectMessagesTopicsByID,
    GetFolderInviteLinks,
    GetFolders,
    GetForumTopics,
    GetForumTopicsByID,
    GetNearbyChats,
    GetPersonalChannels,
    GetSendAsChats,
    GetSimilarChannels,
    GetSuitableDiscussionChats,
    GetTopChats,
    JoinChat,
    JoinFolder,
    LeaveChat,
    LeaveFolder,
    MarkChatUnread,
    PinChatMessage,
    PromoteChatMember,
    RestrictChatMember,
    RestrictSponsoredMessages,
    SetAdministratorTitle,
    SetChatDescription,
    SetChatPermissions,
    SetChatPhoto,
    SetChatProtectedContent,
    SetChatTitle,
    SetChatUsername,
    SetSendAsChat,
    SetSlowMode,
    ToggleAntiSpam,
    ToggleAutoTranslation,
    ToggleForum,
    ToggleJoinToSend,
    ToggleParticipantsHidden,
    TogglePreHistoryHidden,
    ToggleSignatures,
    ToggleSlowMode,
    ToggleViewForumAsMessages,
    UnarchiveChats,
    UnbanChatMember,
    UnpinAllChatMessages,
    UnpinChatMessage,
    UpdateChannelColor
):
    pass
