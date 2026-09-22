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

from .add_profile_audio import AddProfileAudio
from .cancel_password_email import CancelPasswordEmail
from .change_authorization_settings import ChangeAuthorizationSettings
from .clear_recent_emoji_statuses import ClearRecentEmojiStatuses
from .confirm_bot_connection import ConfirmBotConnection
from .confirm_password_email import ConfirmPasswordEmail
from .confirm_phone import ConfirmPhone
from .create_theme import CreateTheme
from .decline_password_reset import DeclinePasswordReset
from .delete_account import DeleteAccount
from .delete_auto_save_exceptions import DeleteAutoSaveExceptions
from .delete_passkey import DeletePasskey
from .delete_secure_value import DeleteSecureValue
from .delete_web_browser_settings_exceptions import DeleteWebBrowserSettingsExceptions
from .disable_peer_connected_bot import DisablePeerConnectedBot
from .edit_business_chat_link import EditBusinessChatLink
from .get_account_ttl import GetAccountTTL
from .get_all_secure_values import GetAllSecureValues
from .get_authorization_form import GetAuthorizationForm
from .get_auto_download_settings import GetAutoDownloadSettings
from .get_auto_save_settings import GetAutoSaveSettings
from .get_channel_default_emoji_statuses import GetChannelDefaultEmojiStatuses
from .get_channel_restricted_status_emojis import GetChannelRestrictedStatusEmojis
from .get_chat_themes import GetChatThemes
from .get_collectible_emoji_statuses import GetCollectibleEmojiStatuses
from .get_contact_sign_up_notification import GetContactSignUpNotification
from .get_content_settings import GetContentSettings
from .get_default_background_emojis import GetDefaultBackgroundEmojis
from .get_default_group_photo_emojis import GetDefaultGroupPhotoEmojis
from .get_default_profile_photo_emojis import GetDefaultProfilePhotoEmojis
from .get_global_privacy_settings import GetGlobalPrivacySettings
from .get_multi_wall_papers import GetMultiWallPapers
from .get_notify_exceptions import GetNotifyExceptions
from .get_notify_settings import GetNotifySettings
from .get_paid_messages_revenue import GetPaidMessagesRevenue
from .get_passkeys import GetPasskeys
from .get_password_settings import GetPasswordSettings
from .get_privacy import GetPrivacy
from .get_reactions_notify_settings import GetReactionsNotifySettings
from .get_recent_emoji_statuses import GetRecentEmojiStatuses
from .get_saved_music_ids import GetSavedMusicIds
from .get_saved_ringtones import GetSavedRingtones
from .get_secure_value import GetSecureValue
from .get_theme import GetTheme
from .get_themes import GetThemes
from .get_tmp_password import GetTmpPassword
from .get_unique_gift_chat_themes import GetUniqueGiftChatThemes
from .get_wall_paper import GetWallPaper
from .get_wall_papers import GetWallPapers
from .get_web_authorizations import GetWebAuthorizations
from .get_web_browser_settings import GetWebBrowserSettings
from .init_passkey_registration import InitPasskeyRegistration
from .install_theme import InstallTheme
from .install_wall_paper import InstallWallPaper
from .invalidate_sign_in_codes import InvalidateSignInCodes
from .register_device import RegisterDevice
from .register_passkey import RegisterPasskey
from .remove_profile_audio import RemoveProfileAudio
from .reorder_usernames import ReorderUsernames
from .resend_password_email import ResendPasswordEmail
from .reset_notify_settings import ResetNotifySettings
from .reset_password import ResetPassword
from .reset_wall_papers import ResetWallPapers
from .reset_web_authorization import ResetWebAuthorization
from .reset_web_authorizations import ResetWebAuthorizations
from .save_auto_download_settings import SaveAutoDownloadSettings
from .save_auto_save_settings import SaveAutoSaveSettings
from .save_ringtone import SaveRingtone
from .save_secure_value import SaveSecureValue
from .save_theme import SaveTheme
from .save_wall_paper import SaveWallPaper
from .send_confirm_phone_code import SendConfirmPhoneCode
from .set_account_ttl import SetAccountTTL
from .set_contact_sign_up_notification import SetContactSignUpNotification
from .set_content_settings import SetContentSettings
from .set_global_privacy_settings import SetGlobalPrivacySettings
from .set_inactive_session_ttl import SetInactiveSessionTTL
from .set_privacy import SetPrivacy
from .set_profile_audio_position import SetProfileAudioPosition
from .set_reactions_notify_settings import SetReactionsNotifySettings
from .toggle_connected_bot_paused import ToggleConnectedBotPaused
from .toggle_no_paid_messages_exception import ToggleNoPaidMessagesException
from .toggle_sponsored_messages import ToggleSponsoredMessages
from .toggle_username import ToggleUsername
from .toggle_web_browser_settings_exception import ToggleWebBrowserSettingsException
from .unregister_device import UnregisterDevice
from .update_connected_bot import UpdateConnectedBot
from .update_device_locked import UpdateDeviceLocked
from .update_theme import UpdateTheme
from .update_web_browser_settings import UpdateWebBrowserSettings
from .upload_ringtone import UploadRingtone
from .upload_theme import UploadTheme
from .upload_wall_paper import UploadWallPaper
from .verify_phone import VerifyPhone


class Account(
    AddProfileAudio,
    CancelPasswordEmail,
    ChangeAuthorizationSettings,
    ClearRecentEmojiStatuses,
    ConfirmBotConnection,
    ConfirmPasswordEmail,
    ConfirmPhone,
    CreateTheme,
    DeclinePasswordReset,
    DeleteAccount,
    DeleteAutoSaveExceptions,
    DeletePasskey,
    DeleteSecureValue,
    DeleteWebBrowserSettingsExceptions,
    DisablePeerConnectedBot,
    EditBusinessChatLink,
    GetAccountTTL,
    GetAllSecureValues,
    GetAuthorizationForm,
    GetAutoDownloadSettings,
    GetAutoSaveSettings,
    GetChannelDefaultEmojiStatuses,
    GetChannelRestrictedStatusEmojis,
    GetChatThemes,
    GetCollectibleEmojiStatuses,
    GetContactSignUpNotification,
    GetContentSettings,
    GetDefaultBackgroundEmojis,
    GetDefaultGroupPhotoEmojis,
    GetDefaultProfilePhotoEmojis,
    GetGlobalPrivacySettings,
    GetMultiWallPapers,
    GetNotifyExceptions,
    GetNotifySettings,
    GetPaidMessagesRevenue,
    GetPasskeys,
    GetPasswordSettings,
    GetPrivacy,
    GetReactionsNotifySettings,
    GetRecentEmojiStatuses,
    GetSavedMusicIds,
    GetSavedRingtones,
    GetSecureValue,
    GetTheme,
    GetThemes,
    GetTmpPassword,
    GetUniqueGiftChatThemes,
    GetWallPaper,
    GetWallPapers,
    GetWebAuthorizations,
    GetWebBrowserSettings,
    InitPasskeyRegistration,
    InstallTheme,
    InstallWallPaper,
    InvalidateSignInCodes,
    RegisterDevice,
    RegisterPasskey,
    RemoveProfileAudio,
    ReorderUsernames,
    ResendPasswordEmail,
    ResetNotifySettings,
    ResetPassword,
    ResetWallPapers,
    ResetWebAuthorization,
    ResetWebAuthorizations,
    SaveAutoDownloadSettings,
    SaveAutoSaveSettings,
    SaveRingtone,
    SaveSecureValue,
    SaveTheme,
    SaveWallPaper,
    SendConfirmPhoneCode,
    SetAccountTTL,
    SetContactSignUpNotification,
    SetContentSettings,
    SetGlobalPrivacySettings,
    SetInactiveSessionTTL,
    SetPrivacy,
    SetProfileAudioPosition,
    SetReactionsNotifySettings,
    ToggleConnectedBotPaused,
    ToggleNoPaidMessagesException,
    ToggleSponsoredMessages,
    ToggleUsername,
    ToggleWebBrowserSettingsException,
    UnregisterDevice,
    UpdateConnectedBot,
    UpdateDeviceLocked,
    UpdateTheme,
    UpdateWebBrowserSettings,
    UploadRingtone,
    UploadTheme,
    UploadWallPaper,
    VerifyPhone,
):
    pass
