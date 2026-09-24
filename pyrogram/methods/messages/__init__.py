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

from .accept_encryption import AcceptEncryption
from .accept_url_auth import AcceptUrlAuth
from .add_checklist_tasks import AddChecklistTasks
from .add_poll_option import AddPollOption
from .add_to_gifs import AddToGifs
from .approve_suggested_post import ApproveSuggestedPost
from .check_history_import import CheckHistoryImport
from .check_history_import_peer import CheckHistoryImportPeer
from .check_quick_reply_shortcut import CheckQuickReplyShortcut
from .check_search_posts_flood import CheckSearchPostsFlood
from .check_url_auth_match_code import CheckUrlAuthMatchCode
from .clear_all_drafts import ClearAllDrafts
from .clear_recent_reactions import ClearRecentReactions
from .click_sponsored_message import ClickSponsoredMessage
from .compose_rich_message_with_ai import ComposeRichMessageWithAI
from .compose_text_with_ai import ComposeTextWithAI
from .copy_media_group import CopyMediaGroup
from .copy_message import CopyMessage
from .copy_messages import CopyMessages
from .decline_suggested_post import DeclineSuggestedPost
from .decline_url_auth import DeclineUrlAuth
from .delete_chat import DeleteChat
from .delete_chat_history import DeleteChatHistory
from .delete_direct_messages_chat_topic_history import DeleteDirectMessagesChatTopicHistory
from .delete_fact_check import DeleteFactCheck
from .delete_messages import DeleteMessages
from .delete_participant_reaction import DeleteParticipantReaction
from .delete_participant_reactions import DeleteParticipantReactions
from .delete_phone_call_history import DeletePhoneCallHistory
from .delete_poll_option import DeletePollOption
from .delete_quick_reply_messages import DeleteQuickReplyMessages
from .delete_quick_reply_shortcut import DeleteQuickReplyShortcut
from .delete_scheduled_messages import DeleteScheduledMessages
from .discard_encryption import DiscardEncryption
from .download_media import DownloadMedia
from .edit_chat_admin import EditChatAdmin
from .edit_fact_check import EditFactCheck
from .edit_inline_caption import EditInlineCaption
from .edit_inline_media import EditInlineMedia
from .edit_inline_reply_markup import EditInlineReplyMarkup
from .edit_inline_text import EditInlineText
from .edit_message_caption import EditMessageCaption
from .edit_message_checklist import EditMessageChecklist
from .edit_message_live_location import EditMessageLiveLocation
from .edit_message_media import EditMessageMedia
from .edit_message_reply_markup import EditMessageReplyMarkup
from .edit_message_text import EditMessageText
from .edit_quick_reply_shortcut import EditQuickReplyShortcut
from .emojify_text_with_ai import EmojifyTextWithAI
from .export_message_link import ExportMessageLink
from .fix_text_with_ai import FixTextWithAI
from .forward_media_group import ForwardMediaGroup
from .forward_messages import ForwardMessages
from .get_all_drafts import GetAllDrafts
from .get_all_stickers import GetAllStickers
from .get_archived_stickers import GetArchivedStickers
from .get_attach_menu_bot import GetAttachMenuBot
from .get_attach_menu_bots import GetAttachMenuBots
from .get_attached_stickers import GetAttachedStickers
from .get_available_effects import GetAvailableEffects
from .get_available_reactions import GetAvailableReactions
from .get_bot_app import GetBotApp
from .get_chat_history import GetChatHistory
from .get_chat_history_count import GetChatHistoryCount
from .get_custom_emoji_stickers import GetCustomEmojiStickers
from .get_default_history_ttl import GetDefaultHistoryTTL
from .get_default_tag_reactions import GetDefaultTagReactions
from .get_dh_config import GetDhConfig
from .get_dialog_unread_marks import GetDialogUnreadMarks
from .get_direct_messages_chat_topic_history import GetDirectMessagesChatTopicHistory
from .get_discussion_message import GetDiscussionMessage
from .get_discussion_replies import GetDiscussionReplies
from .get_discussion_replies_count import GetDiscussionRepliesCount
from .get_document_by_hash import GetDocumentByHash
from .get_emoji_game_info import GetEmojiGameInfo
from .get_emoji_groups import GetEmojiGroups
from .get_emoji_keywords import GetEmojiKeywords
from .get_emoji_keywords_difference import GetEmojiKeywordsDifference
from .get_emoji_keywords_languages import GetEmojiKeywordsLanguages
from .get_emoji_profile_photo_groups import GetEmojiProfilePhotoGroups
from .get_emoji_status_groups import GetEmojiStatusGroups
from .get_emoji_sticker_groups import GetEmojiStickerGroups
from .get_emoji_stickers import GetEmojiStickers
from .get_emoji_url import GetEmojiURL
from .get_extended_media import GetExtendedMedia
from .get_fact_check import GetFactCheck
from .get_featured_emoji_stickers import GetFeaturedEmojiStickers
from .get_featured_stickers import GetFeaturedStickers
from .get_future_chat_creator_after_leave import GetFutureChatCreatorAfterLeave
from .get_main_web_app import GetMainWebApp
from .get_mask_stickers import GetMaskStickers
from .get_media_group import GetMediaGroup
from .get_message_author import GetMessageAuthor
from .get_message_edit_data import GetMessageEditData
from .get_message_reactions import GetMessageReactions
from .get_message_read_participants import GetMessageReadParticipants
from .get_messages import GetMessages
from .get_messages_reactions import GetMessagesReactions
from .get_old_featured_stickers import GetOldFeaturedStickers
from .get_outbox_read_date import GetOutboxReadDate
from .get_paid_reaction_privacy import GetPaidReactionPrivacy
from .get_pinned_saved_dialogs import GetPinnedSavedDialogs
from .get_poll_results import GetPollResults
from .get_poll_stats import GetPollStats
from .get_poll_votes import GetPollVotes
from .get_prepared_inline_message import GetPreparedInlineMessage
from .get_quick_replies import GetQuickReplies
from .get_quick_reply_messages import GetQuickReplyMessages
from .get_recent_locations import GetRecentLocations
from .get_recent_reactions import GetRecentReactions
from .get_rich_message import GetRichMessage
from .get_saved_gifs import GetSavedGifs
from .get_saved_history import GetSavedHistory
from .get_saved_reaction_tags import GetSavedReactionTags
from .get_scheduled_messages import GetScheduledMessages
from .get_search_results_calendar import GetSearchResultsCalendar
from .get_search_results_positions import GetSearchResultsPositions
from .get_split_ranges import GetSplitRanges
from .get_sponsored_messages import GetSponsoredMessages
from .get_stickers import GetStickers
from .get_stickers_by_emoticon import GetStickersByEmoticon
from .get_suggested_dialog_filters import GetSuggestedDialogFilters
from .get_top_reactions import GetTopReactions
from .get_unread_mentions import GetUnreadMentions
from .get_unread_poll_votes import GetUnreadPollVotes
from .get_unread_reactions import GetUnreadReactions
from .get_user_gifts import GetUserGifts
from .get_user_personal_chat_messages import GetUserPersonalChatMessages
from .get_user_profile_audios import GetUserProfileAudios
from .get_web_app_link_url import GetWebAppLinkUrl
from .get_web_app_url import GetWebAppUrl
from .get_web_page import GetWebPage
from .get_web_page_preview import GetWebPagePreview
from .gift_premium_subscription import GiftPremiumSubscription
from .hide_peer_settings_bar import HidePeerSettingsBar
from .init_history_import import InitHistoryImport
from .mark_checklist_tasks_as_done import MarkChecklistTasksAsDone
from .migrate_chat import MigrateChat
from .open_web_app import OpenWebApp
from .prolong_web_view import ProlongWebView
from .rate_transcribed_audio import RateTranscribedAudio
from .read_chat_history import ReadChatHistory
from .read_chat_message_contents import ReadChatMessageContents
from .read_discussion import ReadDiscussion
from .read_encrypted_history import ReadEncryptedHistory
from .read_featured_stickers import ReadFeaturedStickers
from .read_mentions import ReadMentions
from .read_message_contents import ReadMessageContents
from .read_poll_votes import ReadPollVotes
from .read_reactions import ReadReactions
from .read_saved_history import ReadSavedHistory
from .received_messages import ReceivedMessages
from .received_queue import ReceivedQueue
from .reorder_pinned_dialogs import ReorderPinnedDialogs
from .reorder_pinned_saved_dialogs import ReorderPinnedSavedDialogs
from .reorder_quick_replies import ReorderQuickReplies
from .reorder_sticker_sets import ReorderStickerSets
from .rephrase_text_with_ai import RephraseTextWithAI
from .report_encrypted_spam import ReportEncryptedSpam
from .report_messages import ReportMessages
from .report_messages_delivery import ReportMessagesDelivery
from .report_music_listen import ReportMusicListen
from .report_reaction import ReportReaction
from .report_read_metrics import ReportReadMetrics
from .report_sponsored_message import ReportSponsoredMessage
from .request_chat_join_web_view import RequestChatJoinWebView
from .request_encryption import RequestEncryption
from .request_url_auth import RequestUrlAuth
from .retract_vote import RetractVote
from .save_draft import SaveDraft
from .save_prepared_inline_message import SavePreparedInlineMessage
from .save_prepared_keyboard_button import SavePreparedKeyboardButton
from .save_recent_sticker import SaveRecentSticker
from .search_custom_emoji import SearchCustomEmoji
from .search_emoji_sticker_sets import SearchEmojiStickerSets
from .search_global import SearchGlobal
from .search_global_count import SearchGlobalCount
from .search_messages import SearchMessages
from .search_messages_count import SearchMessagesCount
from .search_posts import SearchPosts
from .search_posts_count import SearchPostsCount
from .search_sent_media import SearchSentMedia
from .send_animation import SendAnimation
from .send_audio import SendAudio
from .send_bot_requested_peer import SendBotRequestedPeer
from .send_cached_media import SendCachedMedia
from .send_chat_action import SendChatAction
from .send_checklist import SendChecklist
from .send_contact import SendContact
from .send_dice import SendDice
from .send_document import SendDocument
from .send_encrypted import SendEncrypted
from .send_encrypted_file import SendEncryptedFile
from .send_encrypted_service import SendEncryptedService
from .send_live_photo import SendLivePhoto
from .send_location import SendLocation
from .send_media_group import SendMediaGroup
from .send_message import SendMessage
from .send_message_draft import SendMessageDraft
from .send_paid_media import SendPaidMedia
from .send_paid_reaction import SendPaidReaction
from .send_photo import SendPhoto
from .send_poll import SendPoll
from .send_quick_reply_messages import SendQuickReplyMessages
from .send_reaction import SendReaction
from .send_rich_message import SendRichMessage
from .send_rich_message_draft import SendRichMessageDraft
from .send_scheduled_messages import SendScheduledMessages
from .send_screenshot_notification import SendScreenshotNotification
from .send_sticker import SendSticker
from .send_venue import SendVenue
from .send_video import SendVideo
from .send_video_note import SendVideoNote
from .send_voice import SendVoice
from .send_web_view_data import SendWebViewData
from .set_chat_available_reactions import SetChatAvailableReactions
from .set_chat_theme import SetChatTheme
from .set_chat_wallpaper import SetChatWallPaper
from .set_default_history_ttl import SetDefaultHistoryTTL
from .set_default_reaction import SetDefaultReaction
from .set_direct_messages_chat_topic_is_marked_as_unread import (
    SetDirectMessagesChatTopicIsMarkedAsUnread,
)
from .set_encrypted_typing import SetEncryptedTyping
from .set_passport_data_errors import SetPassportDataErrors
from .start_bot import StartBot
from .start_history_import import StartHistoryImport
from .stop_message_live_location import StopMessageLiveLocation
from .stop_poll import StopPoll
from .stream_media import StreamMedia
from .summarize_text import SummarizeText
from .toggle_bot_in_attach_menu import ToggleBotInAttachMenu
from .toggle_dialog_pin import ToggleDialogPin
from .toggle_paid_reaction_privacy import TogglePaidReactionPrivacy
from .toggle_peer_translations import TogglePeerTranslations
from .toggle_saved_dialog_pin import ToggleSavedDialogPin
from .toggle_sticker_sets import ToggleStickerSets
from .transcribe_audio import TranscribeAudio
from .translate_rich_message import TranslateRichMessage
from .translate_text import TranslateText
from .update_saved_reaction_tag import UpdateSavedReactionTag
from .upload_encrypted_file import UploadEncryptedFile
from .upload_imported_media import UploadImportedMedia
from .view_messages import ViewMessages
from .view_sponsored_message import ViewSponsoredMessage
from .vote_poll import VotePoll


class Messages(
    AcceptEncryption,
    AcceptUrlAuth,
    AddChecklistTasks,
    AddPollOption,
    AddToGifs,
    ApproveSuggestedPost,
    CheckHistoryImport,
    CheckHistoryImportPeer,
    CheckQuickReplyShortcut,
    CheckSearchPostsFlood,
    CheckUrlAuthMatchCode,
    ClearAllDrafts,
    ClearRecentReactions,
    ClickSponsoredMessage,
    ComposeRichMessageWithAI,
    ComposeTextWithAI,
    CopyMediaGroup,
    CopyMessage,
    CopyMessages,
    DeclineSuggestedPost,
    DeclineUrlAuth,
    DeleteChat,
    DeleteChatHistory,
    DeleteDirectMessagesChatTopicHistory,
    DeleteFactCheck,
    DeleteMessages,
    DeleteParticipantReaction,
    DeleteParticipantReactions,
    DeletePhoneCallHistory,
    DeletePollOption,
    DeleteQuickReplyMessages,
    DeleteQuickReplyShortcut,
    DeleteScheduledMessages,
    DiscardEncryption,
    DownloadMedia,
    EditChatAdmin,
    EditFactCheck,
    EditInlineCaption,
    EditInlineMedia,
    EditInlineReplyMarkup,
    EditInlineText,
    EditMessageCaption,
    EditMessageChecklist,
    EditMessageLiveLocation,
    EditMessageMedia,
    EditMessageReplyMarkup,
    EditMessageText,
    EditQuickReplyShortcut,
    EmojifyTextWithAI,
    ExportMessageLink,
    FixTextWithAI,
    ForwardMediaGroup,
    ForwardMessages,
    GetAllDrafts,
    GetAllStickers,
    GetArchivedStickers,
    GetAttachMenuBot,
    GetAttachMenuBots,
    GetAttachedStickers,
    GetAvailableEffects,
    GetAvailableReactions,
    GetBotApp,
    GetChatHistory,
    GetChatHistoryCount,
    GetCustomEmojiStickers,
    GetDefaultHistoryTTL,
    GetDefaultTagReactions,
    GetDhConfig,
    GetDialogUnreadMarks,
    GetDirectMessagesChatTopicHistory,
    GetDiscussionMessage,
    GetDiscussionReplies,
    GetDiscussionRepliesCount,
    GetDocumentByHash,
    GetEmojiGameInfo,
    GetEmojiGroups,
    GetEmojiKeywords,
    GetEmojiKeywordsDifference,
    GetEmojiKeywordsLanguages,
    GetEmojiProfilePhotoGroups,
    GetEmojiStatusGroups,
    GetEmojiStickerGroups,
    GetEmojiStickers,
    GetEmojiURL,
    GetExtendedMedia,
    GetFactCheck,
    GetFeaturedEmojiStickers,
    GetFeaturedStickers,
    GetFutureChatCreatorAfterLeave,
    GetMainWebApp,
    GetMaskStickers,
    GetMediaGroup,
    GetMessageAuthor,
    GetMessageEditData,
    GetMessageReactions,
    GetMessageReadParticipants,
    GetMessages,
    GetMessagesReactions,
    GetOldFeaturedStickers,
    GetOutboxReadDate,
    GetPaidReactionPrivacy,
    GetPinnedSavedDialogs,
    GetPollResults,
    GetPollStats,
    GetPollVotes,
    GetPreparedInlineMessage,
    GetQuickReplies,
    GetQuickReplyMessages,
    GetRecentLocations,
    GetRecentReactions,
    GetRichMessage,
    GetSavedGifs,
    GetSavedHistory,
    GetSavedReactionTags,
    GetScheduledMessages,
    GetSearchResultsCalendar,
    GetSearchResultsPositions,
    GetSplitRanges,
    GetSponsoredMessages,
    GetStickers,
    GetStickersByEmoticon,
    GetSuggestedDialogFilters,
    GetTopReactions,
    GetUnreadMentions,
    GetUnreadPollVotes,
    GetUnreadReactions,
    GetUserGifts,
    GetUserPersonalChatMessages,
    GetUserProfileAudios,
    GetWebAppLinkUrl,
    GetWebAppUrl,
    GetWebPage,
    GetWebPagePreview,
    GiftPremiumSubscription,
    HidePeerSettingsBar,
    InitHistoryImport,
    MarkChecklistTasksAsDone,
    MigrateChat,
    OpenWebApp,
    ProlongWebView,
    RateTranscribedAudio,
    ReadChatHistory,
    ReadChatMessageContents,
    ReadDiscussion,
    ReadEncryptedHistory,
    ReadFeaturedStickers,
    ReadMentions,
    ReadMessageContents,
    ReadPollVotes,
    ReadReactions,
    ReadSavedHistory,
    ReceivedMessages,
    ReceivedQueue,
    ReorderPinnedDialogs,
    ReorderPinnedSavedDialogs,
    ReorderQuickReplies,
    ReorderStickerSets,
    RephraseTextWithAI,
    ReportEncryptedSpam,
    ReportMessages,
    ReportMessagesDelivery,
    ReportMusicListen,
    ReportReaction,
    ReportReadMetrics,
    ReportSponsoredMessage,
    RequestChatJoinWebView,
    RequestEncryption,
    RequestUrlAuth,
    RetractVote,
    SaveDraft,
    SavePreparedInlineMessage,
    SavePreparedKeyboardButton,
    SaveRecentSticker,
    SearchCustomEmoji,
    SearchEmojiStickerSets,
    SearchGlobal,
    SearchGlobalCount,
    SearchMessages,
    SearchMessagesCount,
    SearchPosts,
    SearchPostsCount,
    SearchSentMedia,
    SendAnimation,
    SendAudio,
    SendBotRequestedPeer,
    SendCachedMedia,
    SendChatAction,
    SendChecklist,
    SendContact,
    SendDice,
    SendDocument,
    SendEncrypted,
    SendEncryptedFile,
    SendEncryptedService,
    SendLivePhoto,
    SendLocation,
    SendMediaGroup,
    SendMessage,
    SendMessageDraft,
    SendPaidMedia,
    SendPaidReaction,
    SendPhoto,
    SendPoll,
    SendQuickReplyMessages,
    SendReaction,
    SendRichMessage,
    SendRichMessageDraft,
    SendScheduledMessages,
    SendScreenshotNotification,
    SendSticker,
    SendVenue,
    SendVideo,
    SendVideoNote,
    SendVoice,
    SendWebViewData,
    SetChatAvailableReactions,
    SetChatTheme,
    SetChatWallPaper,
    SetDefaultHistoryTTL,
    SetDefaultReaction,
    SetDirectMessagesChatTopicIsMarkedAsUnread,
    SetEncryptedTyping,
    SetPassportDataErrors,
    StartBot,
    StartHistoryImport,
    StopMessageLiveLocation,
    StopPoll,
    StreamMedia,
    SummarizeText,
    ToggleBotInAttachMenu,
    ToggleDialogPin,
    TogglePaidReactionPrivacy,
    TogglePeerTranslations,
    ToggleSavedDialogPin,
    ToggleStickerSets,
    TranscribeAudio,
    TranslateRichMessage,
    TranslateText,
    UpdateSavedReactionTag,
    UploadEncryptedFile,
    UploadImportedMedia,
    ViewMessages,
    ViewSponsoredMessage,
    VotePoll,
):
    pass
