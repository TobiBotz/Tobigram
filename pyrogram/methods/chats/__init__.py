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
from .ban_chat_sender_chat import BanChatSenderChat
from .close_forum_topic import CloseForumTopic
from .close_general_forum_topic import CloseGeneralForumTopic
from .convert_to_gigagroup import ConvertToGigagroup
from .create_channel import CreateChannel
from .create_folder import CreateFolder
from .create_folder_invite_link import CreateFolderInviteLink
from .create_forum_topic import CreateForumTopic
from .create_group import CreateGroup
from .create_supergroup import CreateSupergroup
from .deactivate_chat_usernames import DeactivateChatUsernames
from .delete_all_message_reactions import DeleteAllMessageReactions
from .delete_channel import DeleteChannel
from .delete_chat_photo import DeleteChatPhoto
from .delete_chat_sticker_set import DeleteChatStickerSet
from .delete_folder import DeleteFolder
from .delete_folder_invite_link import DeleteFolderInviteLink
from .delete_forum_topic import DeleteForumTopic
from .delete_message_reaction import DeleteMessageReaction
from .delete_supergroup import DeleteSupergroup
from .delete_user_history import DeleteUserHistory
from .edit_chat_location import EditChatLocation
from .edit_folder import EditFolder
from .edit_folder_invite_link import EditFolderInviteLink
from .edit_forum_topic import EditForumTopic
from .edit_general_forum_topic import EditGeneralForumTopic
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
from .get_forum_topic_icon_stickers import GetForumTopicIconStickers
from .get_forum_topics import GetForumTopics
from .get_forum_topics_by_id import GetForumTopicsByID
from .get_inactive_channels import GetInactiveChannels
from .get_left_channels import GetLeftChannels
from .get_nearby_chats import GetNearbyChats
from .get_personal_channels import GetPersonalChannels
from .get_send_as_chats import GetSendAsChats
from .get_similar_channels import GetSimilarChannels
from .get_suitable_discussion_chats import GetSuitableDiscussionChats
from .get_top_chats import GetTopChats
from .hide_general_forum_topic import HideGeneralForumTopic
from .join_chat import JoinChat
from .join_folder import JoinFolder
from .leave_chat import LeaveChat
from .leave_folder import LeaveFolder
from .mark_chat_unread import MarkChatUnread
from .pin_chat_message import PinChatMessage
from .pin_forum_topic import PinForumTopic
from .promote_chat_member import PromoteChatMember
from .remove_chat_verification import RemoveChatVerification
from .remove_user_verification import RemoveUserVerification
from .reopen_forum_topic import ReopenForumTopic
from .reopen_general_forum_topic import ReopenGeneralForumTopic
from .reorder_chat_usernames import ReorderChatUsernames
from .reorder_folders import ReorderFolders
from .reorder_pinned_forum_topics import ReorderPinnedForumTopics
from .report_anti_spam_false_positive import ReportAntiSpamFalsePositive
from .report_chat import ReportChat
from .report_spam import ReportSpam
from .restrict_chat_member import RestrictChatMember
from .restrict_sponsored_messages import RestrictSponsoredMessages
from .set_administrator_title import SetAdministratorTitle
from .set_boosts_to_unblock_restrictions import SetBoostsToUnblockRestrictions
from .set_chat_accent_color import SetChatAccentColor
from .set_chat_custom_emoji_sticker_set import SetChatCustomEmojiStickerSet
from .set_chat_description import SetChatDescription
from .set_chat_direct_messages_group import SetChatDirectMessagesGroup
from .set_chat_discussion_group import SetChatDiscussionGroup
from .set_chat_member_tag import SetChatMemberTag
from .set_chat_permissions import SetChatPermissions
from .set_chat_photo import SetChatPhoto
from .set_chat_protected_content import SetChatProtectedContent
from .set_chat_sticker_set import SetChatStickerSet
from .set_chat_title import SetChatTitle
from .set_chat_ttl import SetChatTTL
from .set_chat_username import SetChatUsername
from .set_main_profile_tab import SetMainProfileTab
from .set_send_as_chat import SetSendAsChat
from .set_slow_mode import SetSlowMode
from .set_upgraded_gift_colors import SetUpgradedGiftColors
from .toggle_anti_spam import ToggleAntiSpam
from .toggle_auto_translation import ToggleAutoTranslation
from .toggle_chat_username import ToggleChatUsername
from .toggle_folder_tags import ToggleFolderTags
from .toggle_forum import ToggleForum
from .toggle_join_request import ToggleJoinRequest
from .toggle_join_to_send import ToggleJoinToSend
from .toggle_participants_hidden import ToggleParticipantsHidden
from .toggle_pre_history_hidden import TogglePreHistoryHidden
from .toggle_signatures import ToggleSignatures
from .toggle_slow_mode import ToggleSlowMode
from .toggle_view_forum_as_messages import ToggleViewForumAsMessages
from .transfer_chat_ownership import TransferChatOwnership
from .unarchive_chats import UnarchiveChats
from .unban_chat_member import UnbanChatMember
from .unban_chat_sender_chat import UnbanChatSenderChat
from .unhide_general_forum_topic import UnhideGeneralForumTopic
from .unpin_all_chat_messages import UnpinAllChatMessages
from .unpin_all_forum_topic_messages import UnpinAllForumTopicMessages
from .unpin_all_general_forum_topic_messages import UnpinAllGeneralForumTopicMessages
from .unpin_chat_message import UnpinChatMessage
from .unpin_forum_topic import UnpinForumTopic
from .update_channel_color import UpdateChannelColor
from .update_chat_notifications import UpdateChatNotifications
from .verify_chat import VerifyChat
from .verify_user import VerifyUser


class Chats(
    AddChatMembers,
    ArchiveChats,
    BanChatMember,
    BanChatSenderChat,
    CloseForumTopic,
    CloseGeneralForumTopic,
    ConvertToGigagroup,
    CreateChannel,
    CreateFolder,
    CreateFolderInviteLink,
    CreateForumTopic,
    CreateGroup,
    CreateSupergroup,
    DeactivateChatUsernames,
    DeleteAllMessageReactions,
    DeleteChannel,
    DeleteChatPhoto,
    DeleteChatStickerSet,
    DeleteFolder,
    DeleteFolderInviteLink,
    DeleteForumTopic,
    DeleteMessageReaction,
    DeleteSupergroup,
    DeleteUserHistory,
    EditChatLocation,
    EditFolder,
    EditFolderInviteLink,
    EditForumTopic,
    EditGeneralForumTopic,
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
    GetForumTopicIconStickers,
    GetForumTopics,
    GetForumTopicsByID,
    GetInactiveChannels,
    GetLeftChannels,
    GetNearbyChats,
    GetPersonalChannels,
    GetSendAsChats,
    GetSimilarChannels,
    GetSuitableDiscussionChats,
    GetTopChats,
    HideGeneralForumTopic,
    JoinChat,
    JoinFolder,
    LeaveChat,
    LeaveFolder,
    MarkChatUnread,
    PinChatMessage,
    PinForumTopic,
    PromoteChatMember,
    RemoveChatVerification,
    RemoveUserVerification,
    ReopenForumTopic,
    ReopenGeneralForumTopic,
    ReorderChatUsernames,
    ReorderFolders,
    ReorderPinnedForumTopics,
    ReportAntiSpamFalsePositive,
    ReportChat,
    ReportSpam,
    RestrictChatMember,
    RestrictSponsoredMessages,
    SetAdministratorTitle,
    SetBoostsToUnblockRestrictions,
    SetChatAccentColor,
    SetChatCustomEmojiStickerSet,
    SetChatDescription,
    SetChatDirectMessagesGroup,
    SetChatDiscussionGroup,
    SetChatMemberTag,
    SetChatPermissions,
    SetChatPhoto,
    SetChatProtectedContent,
    SetChatStickerSet,
    SetChatTitle,
    SetChatTTL,
    SetChatUsername,
    SetMainProfileTab,
    SetSendAsChat,
    SetSlowMode,
    SetUpgradedGiftColors,
    ToggleAntiSpam,
    ToggleAutoTranslation,
    ToggleChatUsername,
    ToggleFolderTags,
    ToggleForum,
    ToggleJoinRequest,
    ToggleJoinToSend,
    ToggleParticipantsHidden,
    TogglePreHistoryHidden,
    ToggleSignatures,
    ToggleSlowMode,
    ToggleViewForumAsMessages,
    TransferChatOwnership,
    UnarchiveChats,
    UnbanChatMember,
    UnbanChatSenderChat,
    UnhideGeneralForumTopic,
    UnpinAllChatMessages,
    UnpinAllForumTopicMessages,
    UnpinAllGeneralForumTopicMessages,
    UnpinChatMessage,
    UnpinForumTopic,
    UpdateChannelColor,
    UpdateChatNotifications,
    VerifyChat,
    VerifyUser,
):
    pass
