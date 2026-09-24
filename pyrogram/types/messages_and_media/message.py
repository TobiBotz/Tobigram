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

import contextlib
import logging
from collections.abc import AsyncGenerator, Callable
from datetime import datetime
from functools import partial
from itertools import groupby
from re import Match
from typing import BinaryIO, SupportsIndex

import pyrogram
from pyrogram import enums, raw, types, utils
from pyrogram.errors import (
    ChannelForumMissing,
    ChannelInvalid,
    ChannelPrivate,
    ChatAdminRequired,
    MessageIdsEmpty,
    PeerIdInvalid,
    RPCError,
)
from pyrogram.parser import Parser, utils as parser_utils

from ..listeners.listener import UNSET
from ..object import Object
from ..update import Update

log = logging.getLogger(__name__)


class Str(str):
    """A message text or caption, indexed the way Telegram counts it.

    Entity offsets and lengths are counted in UTF-16 units, so indexing and slicing count
    them too: ``text[entity.offset:entity.offset + entity.length]`` is that entity's text.
    An emoji, and any other code point outside the Basic Multilingual Plane, takes two of
    those units, and a cut falling between them widens outward to the whole code point, so
    a slice can come back one code point longer at either end than it asked for. Half a
    code point is never returned.
    """

    __slots__ = ("entities",)

    def __init__(self, *args):
        super().__init__()

        self.entities: list[types.MessageEntity] | None = None

    def init(self, entities: list):
        self.entities = entities

        return self

    @property
    def markdown(self) -> str:
        return Parser.unparse(self, self.entities, False)

    @property
    def html(self) -> str:
        return Parser.unparse(self, self.entities, True)

    def __getitem__(self, item: SupportsIndex | slice) -> str:
        text = str(self)

        if not parser_utils.SMP_RE.search(text):
            return text[item]

        # Telegram counts offsets in UTF-16 units, where a code point above `0xFFFF` takes
        #  two, so "🔥 250" is 6 offsets long over 5 characters. This table says which
        #  character each offset lands in: [0, 0, 1, 2, 3, 4]. The emoji owns offsets 0 and
        #  1, so an index or a cut between the two still names the whole emoji.
        character_index_at_offset: list[int] = []
        for character_index, character in enumerate(text):
            utf_16_units = 2 if ord(character) > 0xFFFF else 1
            character_index_at_offset += [character_index] * utf_16_units

        if not isinstance(item, slice):
            return text[character_index_at_offset[item]]

        # A slice spanning both offsets of the emoji names its character twice, and
        #  `groupby` drops the repeat.
        selected = character_index_at_offset[item]

        return "".join(text[character_index] for character_index, _ in groupby(selected))


def _parse_reply_markup(reply_markup: raw.base.ReplyMarkup):
    if isinstance(reply_markup, raw.types.ReplyKeyboardForceReply):
        return types.ForceReply.read(reply_markup)

    if isinstance(reply_markup, raw.types.ReplyKeyboardMarkup):
        return types.ReplyKeyboardMarkup.read(reply_markup)

    if isinstance(reply_markup, raw.types.ReplyInlineMarkup):
        return types.InlineKeyboardMarkup.read(reply_markup)

    if isinstance(reply_markup, raw.types.ReplyKeyboardHide):
        return types.ReplyKeyboardRemove.read(reply_markup)

    return None


class Message(Object, Update):
    """A message.

    Parameters:
        id (``int``):
            Unique message identifier inside this chat.

        from_user (:obj:`~pyrogram.types.User`, *optional*):
            Sender, empty for messages sent to channels.

        sender_chat (:obj:`~pyrogram.types.Chat`, *optional*):
            Sender of the message, sent on behalf of a chat.
            The channel itself for channel messages.
            The supergroup itself for messages from anonymous group administrators.
            The linked channel for messages automatically forwarded to the discussion group.

        sender_boost_count (``int``, *optional*):
            If the sender of the message boosted the chat, the number of boosts added by the user.

        sender_business_bot (:obj:`~pyrogram.types.User`, *optional*):
            The bot that actually sent the message on behalf of the business account. Available only for outgoing messages sent on behalf of the connected business account.

        sender_tag (``str``, *optional*):
            Tag or custom title of the sender of the message.
            For supergroups only.

        date (:py:obj:`~datetime.datetime`, *optional*):
            Date the message was sent.

        guest_query_id (``str``, *optional*):
            The unique identifier for the guest query.
            Use this identifier with the method :meth:`~pyrogram.Client.answer_guest_query` to send a response message.
            If non-empty, the message belongs to the chat where the guest bot was summoned, which may not coincide with other existing bot chats sharing the same identifier.

        chat (:obj:`~pyrogram.types.Chat`, *optional*):
            Conversation the message belongs to.

        topic_message (``bool``, *optional*):
            True, if the message is a forum topic message.

        automatic_forward (``bool``, *optional*):
            True, if the message is a channel post that was automatically forwarded to the connected discussion group.

        from_offline (``bool``, *optional*):
            True, if the message was sent by an implicit action, for example, as an away or a greeting business message, or as a scheduled message.

        topic (:obj:`~pyrogram.types.ForumTopic`, *optional*):
            Topic the message belongs to.

        forward_origin (:obj:`~pyrogram.types.MessageOrigin`, *optional*):
            Information about the original message for forwarded messages.

        message_thread_id (``int``, *optional*):
            Unique identifier of a message thread to which the message belongs.
            For forums only.

        direct_messages_topic_id (``int``, *optional*):
            Unique identifier of a topic in a channel direct messages chat administered by the current user.
            For direct chats only.

        effect_id (``int``, *optional*):
            Unique identifier of the message effect.
            For private chats only.

        is_welcome_template (``bool``, *optional*):
            True, if the ephemeral message is a stored welcome message rather than one
            delivered once.

        anchor_message_id (``int``, *optional*):
            Identifier of the message this ephemeral message is anchored to, if any.

        rich_message (:obj:`~pyrogram.types.RichMessage`, *optional*):
            Message is a rich formatted message.

        reply_to_message_id (``int``, *optional*):
            The id of the message which this message directly replied to.

        reply_to_story_id (``int``, *optional*):
            The id of the story which this message directly replied to.

        reply_to_story_user_id (``int``, *optional*):
            The id of the story sender which this message directly replied to.

        reply_to_top_message_id (``int``, *optional*):
            The id of the first message which started this message thread.

        reply_to_poll_option_id (``str``, *optional*):
            Persistent identifier of the specific poll option that is being replied to.

        reply_to_message (:obj:`~pyrogram.types.Message`, *optional*):
            For replies, the original message. Note that the Message object in this field will not contain
            further reply_to_message fields even if it itself is a reply.

        reply_to_story (:obj:`~pyrogram.types.Story`, *optional*):
            For replies, the original story.

        reply_to_checklist_task_id (``int``, *optional*):
            Identifier of the specific checklist task that is being replied to.

        mentioned (``bool``, *optional*):
            The message contains a mention.

        empty (``bool``, *optional*):
            The message is empty.
            A message can be empty in case it was deleted or you tried to retrieve a message that doesn't exist yet.

        service (:obj:`~pyrogram.enums.MessageServiceType`, *optional*):
            The message is a service message.
            This field will contain the enumeration type of the service message.
            You can use ``service = getattr(message, message.service.value)`` to access the service message.

        media (:obj:`~pyrogram.enums.MessageMediaType`, *optional*):
            The message is a media message.
            This field will contain the enumeration type of the media message.
            You can use ``media = getattr(message, message.media.value)`` to access the media message.

        media_content (:obj:`~pyrogram.types.MessageContent`, *optional*):
            Structured container for attached message media (photos, videos, documents, etc.).

        paid_media (:obj:`~pyrogram.types.PaidMediaInfo`, *optional*):
            The message is a paid media message.

        checklist (:obj:`~pyrogram.types.Checklist`, *optional*):
            The message is a checklist message.

        show_caption_above_media (``bool``, *optional*):
            If True, caption must be shown above the message media.

        edit_date (:py:obj:`~datetime.datetime`, *optional*):
            Date the message was last edited.

        edit_hidden (``bool``, *optional*):
            The message shown as not modified.
            A message can be not modified in case it has received a reaction.

        media_group_id (``int``, *optional*):
            The unique identifier of a media message group this message belongs to.

        author_signature (``str``, *optional*):
            Signature of the post author for messages in channels, or the custom title of an anonymous group
            administrator.

        is_paid_post (``bool``, *optional*):
            True, if the message is a paid post.
            Note that such posts must not be deleted for 24 hours to receive the payment and can't be edited.

        has_protected_content (``bool``, *optional*):
            True, if the message can't be forwarded.

        has_media_spoiler (``bool``, *optional*):
            True, if the message media is covered by a spoiler animation.

        text (``str``, *optional*):
            For text messages, the actual UTF-8 text of the message, 0-4096 characters.
            If the message contains entities (bold, italic, ...) you can access *text.markdown* or
            *text.html* to get the marked up message text. In case there is no entity, the fields
            will contain the same text as *text*.

        entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            For text messages, special entities like usernames, URLs, bot commands, etc. that appear in the text.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            For messages with a caption, special entities like usernames, URLs, bot commands, etc. that appear
            in the caption.

        audio (:obj:`~pyrogram.types.Audio`, *optional*):
            Message is an audio file, information about the file.

        document (:obj:`~pyrogram.types.Document`, *optional*):
            Message is a general file, information about the file.

        photo (:obj:`~pyrogram.types.Photo`, *optional*):
            Message is a photo, information about the photo.

        live_photo (:obj:`~pyrogram.types.LivePhoto`, *optional*):
            Message is a live photo, information about the live photo.
            For backward compatibility, when this field is set, the photo field will also be set.

        sticker (:obj:`~pyrogram.types.Sticker`, *optional*):
            Message is a sticker, information about the sticker.

        animation (:obj:`~pyrogram.types.Animation`, *optional*):
            Message is an animation, information about the animation.

        game (:obj:`~pyrogram.types.Game`, *optional*):
            Message is a game, information about the game.

        giveaway (:obj:`~pyrogram.types.Giveaway`, *optional*):
            Message is a giveaway, information about the giveaway.

        invoice (:obj:`~pyrogram.types.Invoice`, *optional*):
            Message is a invoice, information about the invoice.
            `More about payments » <https://core.telegram.org/bots/api#payments>`_

        story (:obj:`~pyrogram.types.Story`, *optional*):
            Message is a story, information about the story.

        video (:obj:`~pyrogram.types.Video`, *optional*):
            Message is a video, information about the video.

        video_processing_pending (``bool``, *optional*):
            True, if the video is still processing.

        voice (:obj:`~pyrogram.types.Voice`, *optional*):
            Message is a voice message, information about the file.

        video_note (:obj:`~pyrogram.types.VideoNote`, *optional*):
            Message is a video note, information about the video message.

        caption (``str``, *optional*):
            Caption for the audio, document, photo, video or voice, 0-1024 characters.
            If the message contains caption entities (bold, italic, ...) you can access *caption.markdown* or
            *caption.html* to get the marked up caption text. In case there is no caption entity, the fields
            will contain the same text as *caption*.

        contact (:obj:`~pyrogram.types.Contact`, *optional*):
            Message is a shared contact, information about the contact.

        location (:obj:`~pyrogram.types.Location`, *optional*):
            Message is a shared location, information about the location.

        venue (:obj:`~pyrogram.types.Venue`, *optional*):
            Message is a venue, information about the venue.

        web_page (:obj:`~pyrogram.types.WebPage`, *optional*):
            Message was sent with a webpage preview.

        link_preview_options (:obj:`~pyrogram.types.LinkPreviewOptions`, *optional*):
            Options used for link preview generation for the message.

        poll (:obj:`~pyrogram.types.Poll`, *optional*):
            Message is a native poll, information about the poll.

        dice (:obj:`~pyrogram.types.Dice`, *optional*):
            A dice containing a value that is randomly generated by Telegram.

        new_chat_members (List of :obj:`~pyrogram.types.User`, *optional*):
            New members that were added to the group or supergroup and information about them
            (the bot itself may be one of these members).

        left_chat_member (:obj:`~pyrogram.types.User`, *optional*):
            A member was removed from the group, information about them (this member may be the bot itself).

        chat_owner_left (:obj:`~pyrogram.types.ChatOwnerLeft`, *optional*):
            Service message: chat owner has left.

        chat_owner_changed (:obj:`~pyrogram.types.ChatOwnerChanged`, *optional*):
            Service message: chat owner has changed.

        chat_join_type (:obj:`~pyrogram.enums.ChatJoinType`, *optional*):
            This field will contain the enumeration type of how the user had joined the chat.

        new_chat_title (``str``, *optional*):
            A chat title was changed to this value.

        new_chat_photo (:obj:`~pyrogram.types.Photo`, *optional*):
            A chat photo was change to this value.

        delete_chat_photo (``bool``, *optional*):
            Service message: the chat photo was deleted.

        group_chat_created (``bool``, *optional*):
            Service message: the group has been created.

        supergroup_chat_created (``bool``, *optional*):
            Service message: the supergroup has been created.
            This field can't be received in a message coming through updates, because bot can't be a member of a
            supergroup when it is created. It can only be found in reply_to_message if someone replies to a very
            first message in a directly created supergroup.

        channel_chat_created (``bool``, *optional*):
            Service message: the channel has been created.
            This field can't be received in a message coming through updates, because bot can't be a member of a
            channel when it is created. It can only be found in reply_to_message if someone replies to a very
            first message in a channel.

        migrate_to_chat_id (``int``, *optional*):
            The group has been migrated to a supergroup with the specified identifier.
            This number may be greater than 32 bits and some programming languages may have difficulty/silent defects
            in interpreting it. But it is smaller than 52 bits, so a signed 64 bit integer or double-precision float
            type are safe for storing this identifier.

        migrate_from_chat_id (``int``, *optional*):
            The supergroup has been migrated from a group with the specified identifier.
            This number may be greater than 32 bits and some programming languages may have difficulty/silent defects
            in interpreting it. But it is smaller than 52 bits, so a signed 64 bit integer or double-precision float
            type are safe for storing this identifier.

        pinned_message (:obj:`~pyrogram.types.Message`, *optional*):
            Specified message was pinned.
            Note that the Message object in this field will not contain further reply_to_message fields even if it
            is itself a reply.

        game_high_score (:obj:`~pyrogram.types.GameHighScore`, *optional*):
            The game score for a user.
            The reply_to_message field will contain the game Message.

        views (``int``, *optional*):
            Channel post views.

        forwards (``int``, *optional*):
            Channel post forwards.

        via_bot (:obj:`~pyrogram.types.User`):
            The information of the bot that generated the message from an inline query of a user.

        outgoing (``bool``, *optional*):
            Whether the message is incoming or outgoing.
            Messages received from other chats are incoming (*outgoing* is False).
            Messages sent from yourself to other chats are outgoing (*outgoing* is True).
            An exception is made for your own personal chat; messages sent there will be incoming.

        external_reply (:obj:`~pyrogram.types.ExternalReplyInfo`, *optional*):
            Information about the message that is being replied to, which may come from another chat or forum topic.

        quote (:obj:`~pyrogram.types.TextQuote`, *optional*):
            Chosen quote from the replied message.

        matches (List of regex Matches, *optional*):
            A list containing all `Match Objects <https://docs.python.org/3/library/re.html#match-objects>`_ that match
            the text of this message. Only applicable when using :meth:`filters.regex() <pyrogram.filters.regex>`.

        command (List of ``str``, *optional*):
            A list containing the command and its arguments, if any.
            E.g.: "/start 1 2 3" would produce ["start", "1", "2", "3"].
            Only applicable when using :obj:`~pyrogram.filters.command`.

        forum_topic_created (:obj:`~pyrogram.types.ForumTopicCreated`, *optional*):
            Service message: forum topic created

        forum_topic_closed (:obj:`~pyrogram.types.ForumTopicClosed`, *optional*):
            Service message: forum topic closed

        forum_topic_reopened (:obj:`~pyrogram.types.ForumTopicReopened`, *optional*):
            Service message: forum topic reopened

        forum_topic_edited (:obj:`~pyrogram.types.ForumTopicEdited`, *optional*):
            Service message: forum topic edited

        general_forum_topic_hidden (:obj:`~pyrogram.types.GeneralForumTopicHidden`, *optional*):
            Service message: general forum topic hidden

        general_forum_topic_unhidden (:obj:`~pyrogram.types.GeneralForumTopicUnhidden`, *optional*):
            Service message: general forum topic unhidden

        video_chat_scheduled (:obj:`~pyrogram.types.VideoChatScheduled`, *optional*):
            Service message: voice chat scheduled.

        history_cleared (:obj:`~pyrogram.types.HistoryCleared`, *optional*):
            Service message: history cleared

        video_chat_started (:obj:`~pyrogram.types.VideoChatStarted`, *optional*):
            Service message: the voice chat started.

        video_chat_ended (:obj:`~pyrogram.types.VideoChatEnded`, *optional*):
            Service message: the voice chat has ended.

        video_chat_members_invited (:obj:`~pyrogram.types.VoiceChatParticipantsInvited`, *optional*):
            Service message: new members were invited to the voice chat.

        phone_call_started (:obj:`~pyrogram.types.PhoneCallStarted`, *optional*):
            Service message: phone call started.

        phone_call_ended (:obj:`~pyrogram.types.PhoneCallEnded`, *optional*):
            Service message: phone call ended.

        web_app_data (:obj:`~pyrogram.types.WebAppData`, *optional*):
            Service message: web app data sent to the bot.

        paid_messages_refunded (:obj:`~pyrogram.types.PaidMessagesRefunded`, *optional*):
            Service message: paid messages refunded.

        paid_messages_price_changed (:obj:`~pyrogram.types.PaidMessagesPriceChanged`, *optional*):
            Service message: paid messages price.

        direct_message_price_changed (:obj:`~pyrogram.types.DirectMessagePriceChanged`, *optional*):
            Service message: direct messages price.

        checklist_tasks_done (:obj:`~pyrogram.types.ChecklistTasksDone`, *optional*):
            Service message: checklist tasks done.

        checklist_tasks_added (:obj:`~pyrogram.types.ChecklistTasksAdded`, *optional*):
            Service message: checklist tasks added.

        premium_gift_code (:obj:`~pyrogram.types.PremiumGiftCode`, *optional*):
            Service message: premium gift code information.

        gifted_premium (:obj:`~pyrogram.types.GiftedPremium`, *optional*):
            Service message: gifted premium information.

        gifted_stars (:obj:`~pyrogram.types.GiftedStars`, *optional*):
            Service message: gifted stars information.

        gifted_grams (:obj:`~pyrogram.types.GiftedGrams`, *optional*):
            Service message: gifted grams information.

        gift (:obj:`~pyrogram.types.Gift`, *optional*):
            Service message: star gift information.

        is_prepaid_upgrade (``bool``, *optional*):
            True, if the messages is about prepaid upgrade of the gift by another user.

        is_from_auction (``bool``, *optional*):
            True, if the message is a notification about a gift won on an auction.

        suggest_profile_photo (:obj:`~pyrogram.types.Photo`, *optional*):
            Service message: suggested profile photo.

        suggest_birthday (:obj:`~pyrogram.types.Birthday`, *optional*):
            Service message: suggested birthday.

        users_shared (:obj:`~pyrogram.types.UsersShared`, *optional*):
            Service message: users shared information.

        chat_shared (:obj:`~pyrogram.types.ChatShared`, *optional*):
            Service message: chat shared information.

        successful_payment (:obj:`~pyrogram.types.SuccessfulPayment`, *optional*):
            Service message: successful payment.

        refunded_payment (:obj:`~pyrogram.types.RefundedPayment`, *optional*):
            Service message: refunded payment.

        suggested_post_approval_failed (:obj:`~pyrogram.types.SuggestedPostApprovalFailed`, *optional*):
            Service message: suggested post approval failed.

        suggested_post_approved (:obj:`~pyrogram.types.SuggestedPostApproved`, *optional*):
            Service message: suggested post approved.

        suggested_post_declined (:obj:`~pyrogram.types.SuggestedPostDeclined`, *optional*):
            Service message: suggested post declined.

        suggested_post_paid (:obj:`~pyrogram.types.SuggestedPostPaid`, *optional*):
            Service message: suggested post paid.

        suggested_post_refunded (:obj:`~pyrogram.types.SuggestedPostRefunded`, *optional*):
            Service message: suggested post refunded.

        giveaway_created (``bool``, *optional*):
            Service message: giveaway launched.

        giveaway_winners (:obj:`~pyrogram.types.GiveawayWinners`, *optional*):
            A giveaway with public winners was completed.

        giveaway_completed (:obj:`~pyrogram.types.GiveawayCompleted`, *optional*):
            Service message: a giveaway without public winners was completed.

        managed_bot_created (:obj:`~pyrogram.types.ManagedBotCreated`, *optional*):
            Service message: user created a bot that will be managed by the current bot.

        poll_option_added (:obj:`~pyrogram.types.PollOptionAdded`, *optional*):
            Service message: answer option was added to a poll.

        poll_option_deleted (:obj:`~pyrogram.types.PollOptionDeleted`, *optional*):
            Service message: answer option was deleted from a poll.

        chat_set_theme (:obj:`~pyrogram.types.ChatTheme`, *optional*):
            Service message: The chat theme was changed.

        chat_set_background (:obj:`~pyrogram.types.ChatBackground`, *optional*):
            Service message: The chat background was changed.

        set_message_auto_delete_time (``int``, *optional*):
            Service message: The auto-delete or self-destruct timer for messages in the chat has been changed.

        chat_boost (``int``, *optional*):
            Service message: The chat was boosted by the sender of the message.
            Number of times the chat was boosted.

        write_access_allowed (:obj:`~pyrogram.types.WriteAccessAllowed`, *optional*):
            Service message: the user allowed the bot to write messages after adding it to the attachment or side menu, launching a Web App from a link, or accepting an explicit request from a Web App sent by the method `requestWriteAccess <https://core.telegram.org/bots/webapps#initializing-mini-apps>`__

        connected_website (``str``, *optional*):
            The domain name of the website on which the user has logged in. `More about Telegram Login <https://core.telegram.org/widgets/login>`__

        contact_registered (:obj:`~pyrogram.types.ContactRegistered`, *optional*):
            Service message: Contact registered in Telegram.

        proximity_alert_triggered (:obj:`~pyrogram.types.ProximityAlertTriggered`, *optional*):
            Service message: A user in the chat came within proximity alert range.

        giveaway_prize_stars (:obj:`~pyrogram.types.GiveawayPrizeStars`, *optional*):
            Service message: Stars were received by the current user from a giveaway.

        screenshot_taken (:obj:`~pyrogram.types.ScreenshotTaken`, *optional*):
            Service message: screenshot of a message in the chat has been taken.

        upgraded_gift_purchase_offer (:obj:`~pyrogram.types.UpgradedGiftPurchaseOffer`, *optional*):
            Service message: An offer to purchase an upgraded gift was sent or received.

        upgraded_gift_purchase_offer_rejected (:obj:`~pyrogram.types.UpgradedGiftPurchaseOfferRejected`, *optional*):
            Service message: An offer to purchase a gift was rejected or expired.

        chat_has_protected_content_toggled (:obj:`~pyrogram.types.ChatHasProtectedContentToggled`, *optional*):
            Service message: An ``has_protected_content`` setting was changed or request to change it was rejected in a chat.

        chat_has_protected_content_disable_requested (:obj:`~pyrogram.types.ChatProtectedContentDisableRequested`, *optional*):
            Service message: An process requested to disable ``has_protected_content`` in a chat.

        business_connection_id (``str``, *optional*):
            Unique identifier of the business connection from which the message was received.
            If non-empty, the message belongs to a chat of the corresponding business account that is independent from any potential bot chat which might share the same identifier.
            This update may at times be triggered by unavailable changes to message fields that are either unavailable or not actively used by the current bot.

        reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
            Additional interface options. An object for an inline keyboard, custom reply keyboard,
            instructions to remove reply keyboard or to force a reply from the user.

        reactions (:obj:`~pyrogram.types.MessageReactions`):
            Reactions of this message.

        send_paid_messages_stars (``int``, *optional*):
            The number of Telegram Stars the sender paid to send the message.

        unread_media (``bool``, *optional*):
            True, if there are unread media attachments in this message.

        silent (``bool``, *optional*):
            True, if the message sent without notification.

        legacy (``bool``, *optional*):
            True, if the message is a legacy message.
            This means that the message is based on the old layer and should be refetched with the new layer.

        pinned (``bool``, *optional*):
            True, if the message is pinned.

        restriction_reason (List of :obj:`~pyrogram.types.RestrictionReason`, *optional*):
            Contains a list of human-readable description of the reason why access to this message must be restricted.

        fact_check (:obj:`~pyrogram.types.FactCheck`, *optional*):
            Information about fact-check added to the message.

        suggested_post_info (:obj:`~pyrogram.types.SuggestedPostInfo`, *optional*):
            Information about the suggested post.

        channel_post (``bool``, *optional*):
            True, if the message is a channel post.

        repeat_period (``int``, *optional*):
            Period after which the message will be sent again in seconds.

        summary_language_code (``str``, *optional*):
            IETF language tag of the message language on which it can be summarized.
            None if summary isn't available for the message.

        guest_bot_caller_user (:obj:`~pyrogram.types.User`, *optional*):
            For a message sent by a guest bot, this is the user whose original message triggered the bot's response.

        guest_bot_caller_chat (:obj:`~pyrogram.types.Chat`, *optional*):
            For a message sent by a guest bot, this is the chat whose original message triggered the bot's response.

        receiver_user (:obj:`~pyrogram.types.User`, *optional*):
            For an ephemeral message, the user who received the copy of the message.

        ephemeral_message_id (``int``, *optional*):
            For an ephemeral message, the identifier of the ephemeral copy of the message.
            This can be used with :meth:`~pyrogram.Client.edit_message_text` and other edit methods
            to edit the ephemeral copy, or with :meth:`~pyrogram.Client.delete_ephemeral_message`.

        raw (:obj:`~pyrogram.raw.types.Message`, *optional*):
            The raw message object, as received from the Telegram API.

        link (``str``, *property*):
            Generate a link to this message, only for groups and channels.

        content (``str``, *property*):
            The text or caption content of the message.

        community_chat_added (:obj:`~pyrogram.types.CommunityChatAdded`, *optional*):
            Service message: a chat was added to the community.

        community_chat_removed (:obj:`~pyrogram.types.CommunityChatRemoved`, *optional*):
            Service message: a chat was removed from the community.

        community_chat_joined (:obj:`~pyrogram.types.CommunityChatJoined`, *optional*):
            Service message: the chat was joined by a user from a community.

        scheduled (``bool``, *optional*):
            True, if the message is a scheduled message that has not been sent yet.

        from_scheduled (``bool``, *optional*):
            True, if the message was sent by a scheduled message that has now fired.
    """

    # Note: Media parameters are accessible directly on Message (for backward compatibility)
    # and structured within Message.content (MessageContent).
    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        id: int,
        from_user: types.User | None = None,
        sender_chat: types.Chat | None = None,
        sender_boost_count: int | None = None,
        sender_business_bot: types.User | None = None,
        sender_tag: str | None = None,
        date: datetime | None = None,
        guest_query_id: str | None = None,
        chat: types.Chat | None = None,
        topic_message: bool | None = None,
        automatic_forward: bool | None = None,
        from_offline: bool | None = None,
        show_caption_above_media: bool | None = None,
        external_reply: types.ExternalReplyInfo | None = None,
        quote: types.TextQuote | None = None,
        topic: types.ForumTopic | None = None,
        forward_origin: types.MessageOrigin | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        is_welcome_template: bool | None = None,
        anchor_message_id: int | None = None,
        rich_message: types.RichMessage | None = None,
        reply_to_message_id: int | None = None,
        reply_to_story_id: int | None = None,
        reply_to_story_user_id: int | None = None,
        reply_to_top_message_id: int | None = None,
        reply_to_poll_option_id: str | None = None,
        reply_to_message: Message | None = None,
        reply_to_story: types.Story | None = None,
        reply_to_checklist_task_id: int | None = None,
        mentioned: bool | None = None,
        empty: bool | None = None,
        service: enums.MessageServiceType | None = None,
        scheduled: bool | None = None,
        from_scheduled: bool | None = None,
        media: enums.MessageMediaType | None = None,
        media_content: types.MessageContent | None = None,
        content: str | types.MessageContent | None = None,
        paid_media: types.PaidMediaInfo | None = None,
        checklist: types.Checklist | None = None,
        edit_date: datetime | None = None,
        edit_hidden: bool | None = None,
        media_group_id: int | None = None,
        author_signature: str | None = None,
        is_paid_post: bool | None = None,
        has_protected_content: bool | None = None,
        has_media_spoiler: bool | None = None,
        text: Str | None = None,
        entities: list[types.MessageEntity] | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        audio: types.Audio | None = None,
        document: types.Document | None = None,
        photo: types.Photo | None = None,
        live_photo: types.LivePhoto | None = None,
        sticker: types.Sticker | None = None,
        animation: types.Animation | None = None,
        game: types.Game | None = None,
        giveaway: types.Giveaway | None = None,
        giveaway_winners: types.GiveawayWinners | None = None,
        giveaway_completed: types.GiveawayCompleted | None = None,
        managed_bot_created: types.ManagedBotCreated | None = None,
        poll_option_added: types.PollOptionAdded | None = None,
        poll_option_deleted: types.PollOptionDeleted | None = None,
        invoice: types.Invoice | None = None,
        story: types.Story | None = None,
        video: types.Video | None = None,
        video_processing_pending: bool | None = None,
        voice: types.Voice | None = None,
        video_note: types.VideoNote | None = None,
        caption: Str | None = None,
        contact: types.Contact | None = None,
        location: types.Location | None = None,
        venue: types.Venue | None = None,
        web_page: types.WebPage | None = None,
        link_preview_options: types.LinkPreviewOptions | None = None,
        poll: types.Poll | None = None,
        dice: types.Dice | None = None,
        new_chat_members: list[types.User] | None = None,
        left_chat_member: types.User | None = None,
        chat_owner_left: types.ChatOwnerLeft | None = None,
        chat_owner_changed: types.ChatOwnerChanged | None = None,
        chat_join_type: enums.ChatJoinType | None = None,
        new_chat_title: str | None = None,
        new_chat_photo: types.Photo | None = None,
        delete_chat_photo: bool | None = None,
        group_chat_created: bool | None = None,
        supergroup_chat_created: bool | None = None,
        channel_chat_created: bool | None = None,
        migrate_to_chat_id: int | None = None,
        migrate_from_chat_id: int | None = None,
        pinned_message: Message | None = None,
        game_high_score: types.GameHighScore | None = None,
        views: int | None = None,
        forwards: int | None = None,
        via_bot: types.User | None = None,
        outgoing: bool | None = None,
        matches: list[Match] | None = None,
        command: list[str] | None = None,
        forum_topic_created: types.ForumTopicCreated | None = None,
        forum_topic_closed: types.ForumTopicClosed | None = None,
        forum_topic_reopened: types.ForumTopicReopened | None = None,
        forum_topic_edited: types.ForumTopicEdited | None = None,
        general_forum_topic_hidden: types.GeneralForumTopicHidden | None = None,
        general_forum_topic_unhidden: types.GeneralForumTopicUnhidden | None = None,
        video_chat_scheduled: types.VideoChatScheduled | None = None,
        history_cleared: types.HistoryCleared | None = None,
        video_chat_started: types.VideoChatStarted | None = None,
        video_chat_ended: types.VideoChatEnded | None = None,
        video_chat_members_invited: types.VideoChatMembersInvited | None = None,
        phone_call_started: types.PhoneCallStarted | None = None,
        phone_call_ended: types.PhoneCallEnded | None = None,
        web_app_data: types.WebAppData | None = None,
        paid_messages_refunded: types.PaidMessagesRefunded | None = None,
        paid_messages_price_changed: types.PaidMessagesPriceChanged | None = None,
        direct_message_price_changed: types.DirectMessagePriceChanged | None = None,
        checklist_tasks_done: list[types.ChecklistTasksDone] | None = None,
        checklist_tasks_added: list[types.ChecklistTasksAdded] | None = None,
        community_chat_added: types.CommunityChatAdded | None = None,
        community_chat_joined: types.CommunityChatJoined | None = None,
        community_chat_removed: types.CommunityChatRemoved | None = None,
        premium_gift_code: types.PremiumGiftCode | None = None,
        gifted_premium: types.GiftedPremium | None = None,
        gifted_stars: types.GiftedStars | None = None,
        gifted_grams: types.GiftedGrams | None = None,
        gift: types.Gift | None = None,
        is_prepaid_upgrade: bool | None = None,
        is_from_auction: bool | None = None,
        suggest_profile_photo: types.Photo | None = None,
        suggest_birthday: types.Birthday | None = None,
        users_shared: types.UsersShared | None = None,
        chat_shared: types.ChatShared | None = None,
        successful_payment: types.SuccessfulPayment | None = None,
        refunded_payment: types.RefundedPayment | None = None,
        suggested_post_approval_failed: types.SuggestedPostApprovalFailed | None = None,
        suggested_post_approved: types.SuggestedPostApproved | None = None,
        suggested_post_declined: types.SuggestedPostDeclined | None = None,
        suggested_post_paid: types.SuggestedPostPaid | None = None,
        suggested_post_refunded: types.SuggestedPostRefunded | None = None,
        giveaway_created: bool | None = None,
        chat_set_theme: types.ChatTheme | None = None,
        chat_set_background: types.ChatBackground | None = None,
        set_message_auto_delete_time: int | None = None,
        chat_boost: int | None = None,
        write_access_allowed: types.WriteAccessAllowed | None = None,
        connected_website: str | None = None,
        contact_registered: types.ContactRegistered | None = None,
        proximity_alert_triggered: types.ProximityAlertTriggered | None = None,
        giveaway_prize_stars: types.GiveawayPrizeStars | None = None,
        screenshot_taken: types.ScreenshotTaken | None = None,
        upgraded_gift_purchase_offer: types.UpgradedGiftPurchaseOffer | None = None,
        upgraded_gift_purchase_offer_rejected: types.UpgradedGiftPurchaseOfferRejected
        | None = None,
        chat_has_protected_content_toggled: types.ChatHasProtectedContentToggled | None = None,
        chat_has_protected_content_disable_requested: types.ChatHasProtectedContentDisableRequested
        | None = None,
        business_connection_id: str | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        reactions: types.MessageReactions | None = None,
        send_paid_messages_stars: int | None = None,
        unread_media: bool | None = None,
        silent: bool | None = None,
        legacy: bool | None = None,
        pinned: bool | None = None,
        restriction_reason: list[types.RestrictionReason] | None = None,
        fact_check: types.FactCheck | None = None,
        suggested_post_info: types.SuggestedPostInfo | None = None,
        channel_post: bool | None = None,
        repeat_period: int | None = None,
        summary_language_code: str | None = None,
        guest_bot_caller_user: types.User | None = None,
        guest_bot_caller_chat: types.Chat | None = None,
        receiver_user: types.User | None = None,
        ephemeral_message_id: int | None = None,
        raw: raw.types.Message | None = None,
    ):
        super().__init__(client)

        self.id = id
        self.from_user = from_user
        self.sender_chat = sender_chat
        self.sender_boost_count = sender_boost_count
        self.sender_business_bot = sender_business_bot
        self.sender_tag = sender_tag
        self.date = date
        self.guest_query_id = guest_query_id
        self.chat = chat
        self.topic_message = topic_message
        self.automatic_forward = automatic_forward
        self.from_offline = from_offline
        self.show_caption_above_media = show_caption_above_media
        self.external_reply = external_reply
        self.quote = quote
        self.topic = topic
        self.forward_origin = forward_origin
        self.message_thread_id = message_thread_id
        self.direct_messages_topic_id = direct_messages_topic_id
        self.effect_id = effect_id
        self.is_welcome_template = is_welcome_template
        self.anchor_message_id = anchor_message_id
        self.rich_message = rich_message
        self.reply_to_message_id = reply_to_message_id
        self.reply_to_story_id = reply_to_story_id
        self.reply_to_story_user_id = reply_to_story_user_id
        self.reply_to_top_message_id = reply_to_top_message_id
        self.reply_to_poll_option_id = reply_to_poll_option_id
        self.reply_to_message = reply_to_message
        self.reply_to_story = reply_to_story
        self.reply_to_checklist_task_id = reply_to_checklist_task_id
        self.mentioned = mentioned
        self.empty = empty
        self.service = service
        self.scheduled = scheduled
        self.from_scheduled = from_scheduled

        if isinstance(content, types.MessageContent):
            media_content = content

        if media_content is not None:
            if audio is None:
                audio = media_content.audio
            if document is None:
                document = media_content.document
            if photo is None:
                photo = media_content.photo
            if live_photo is None:
                live_photo = media_content.live_photo
            if sticker is None:
                sticker = media_content.sticker
            if animation is None:
                animation = media_content.animation
            if game is None:
                game = media_content.game
            if giveaway is None:
                giveaway = media_content.giveaway
            if giveaway_winners is None:
                giveaway_winners = media_content.giveaway_winners
            if invoice is None:
                invoice = media_content.invoice
            if story is None:
                story = media_content.story
            if video is None:
                video = media_content.video
            if voice is None:
                voice = media_content.voice
            if video_note is None:
                video_note = media_content.video_note
            if contact is None:
                contact = media_content.contact
            if location is None:
                location = media_content.location
            if venue is None:
                venue = media_content.venue
            if web_page is None:
                web_page = media_content.web_page
            if poll is None:
                poll = media_content.poll
            if dice is None:
                dice = media_content.dice
            if paid_media is None:
                paid_media = media_content.paid_media
            if checklist is None:
                checklist = media_content.checklist
            if media is None:
                media = media_content.type
        elif any(
            (
                audio,
                document,
                photo,
                live_photo,
                sticker,
                animation,
                game,
                giveaway,
                giveaway_winners,
                invoice,
                story,
                video,
                voice,
                video_note,
                contact,
                location,
                venue,
                web_page,
                poll,
                dice,
                paid_media,
                checklist,
            )
        ):
            media_content = types.MessageContent(
                type=media or enums.MessageMediaType.UNSUPPORTED,
                audio=audio,
                document=document,
                photo=photo,
                live_photo=live_photo,
                sticker=sticker,
                animation=animation,
                game=game,
                giveaway=giveaway,
                giveaway_winners=giveaway_winners,
                invoice=invoice,
                story=story,
                video=video,
                voice=voice,
                video_note=video_note,
                contact=contact,
                location=location,
                venue=venue,
                web_page=web_page,
                poll=poll,
                dice=dice,
                paid_media=paid_media,
                checklist=checklist,
            )

        self.media = media
        self.media_content = media_content
        self.paid_media = paid_media
        self.checklist = checklist
        self.edit_date = edit_date
        self.edit_hidden = edit_hidden
        self.media_group_id = media_group_id
        self.author_signature = author_signature
        self.is_paid_post = is_paid_post
        self.has_protected_content = has_protected_content
        self.has_media_spoiler = has_media_spoiler
        self.text = text
        self.entities = entities
        self.caption_entities = caption_entities
        self.audio = audio
        self.document = document
        self.photo = photo
        self.live_photo = live_photo
        self.sticker = sticker
        self.animation = animation
        self.game = game
        self.giveaway = giveaway
        self.giveaway_winners = giveaway_winners
        self.giveaway_completed = giveaway_completed
        self.managed_bot_created = managed_bot_created
        self.poll_option_added = poll_option_added
        self.poll_option_deleted = poll_option_deleted
        self.invoice = invoice
        self.story = story
        self.video = video
        self.video_processing_pending = video_processing_pending
        self.voice = voice
        self.video_note = video_note
        self.caption = caption
        self.contact = contact
        self.location = location
        self.venue = venue
        self.web_page = web_page
        self.link_preview_options = link_preview_options
        self.poll = poll
        self.dice = dice
        self.new_chat_members = new_chat_members
        self.left_chat_member = left_chat_member
        self.chat_owner_left = chat_owner_left
        self.chat_owner_changed = chat_owner_changed
        self.chat_join_type = chat_join_type
        self.new_chat_title = new_chat_title
        self.new_chat_photo = new_chat_photo
        self.delete_chat_photo = delete_chat_photo
        self.group_chat_created = group_chat_created
        self.supergroup_chat_created = supergroup_chat_created
        self.channel_chat_created = channel_chat_created
        self.migrate_to_chat_id = migrate_to_chat_id
        self.migrate_from_chat_id = migrate_from_chat_id
        self.pinned_message = pinned_message
        self.game_high_score = game_high_score
        self.views = views
        self.forwards = forwards
        self.via_bot = via_bot
        self.outgoing = outgoing
        self.matches = matches
        self.command = command
        self.giveaway_prize_stars = giveaway_prize_stars
        self.screenshot_taken = screenshot_taken
        self.upgraded_gift_purchase_offer = upgraded_gift_purchase_offer
        self.upgraded_gift_purchase_offer_rejected = upgraded_gift_purchase_offer_rejected
        self.chat_has_protected_content_toggled = chat_has_protected_content_toggled
        self.chat_has_protected_content_disable_requested = (
            chat_has_protected_content_disable_requested
        )
        self.business_connection_id = business_connection_id
        self.reply_markup = reply_markup
        self.forum_topic_created = forum_topic_created
        self.forum_topic_closed = forum_topic_closed
        self.forum_topic_reopened = forum_topic_reopened
        self.forum_topic_edited = forum_topic_edited
        self.general_forum_topic_hidden = general_forum_topic_hidden
        self.general_forum_topic_unhidden = general_forum_topic_unhidden
        self.video_chat_scheduled = video_chat_scheduled
        self.history_cleared = history_cleared
        self.video_chat_started = video_chat_started
        self.video_chat_ended = video_chat_ended
        self.video_chat_members_invited = video_chat_members_invited
        self.phone_call_started = phone_call_started
        self.phone_call_ended = phone_call_ended
        self.web_app_data = web_app_data
        self.paid_messages_refunded = paid_messages_refunded
        self.paid_messages_price_changed = paid_messages_price_changed
        self.direct_message_price_changed = direct_message_price_changed
        self.checklist_tasks_done = checklist_tasks_done
        self.checklist_tasks_added = checklist_tasks_added
        self.community_chat_added = community_chat_added
        self.community_chat_joined = community_chat_joined
        self.community_chat_removed = community_chat_removed
        self.premium_gift_code = premium_gift_code
        self.gifted_premium = gifted_premium
        self.gifted_stars = gifted_stars
        self.gifted_grams = gifted_grams
        self.gift = gift
        self.is_prepaid_upgrade = is_prepaid_upgrade
        self.is_from_auction = is_from_auction
        self.suggest_profile_photo = suggest_profile_photo
        self.suggest_birthday = suggest_birthday
        self.users_shared = users_shared
        self.chat_shared = chat_shared
        self.successful_payment = successful_payment
        self.refunded_payment = refunded_payment
        self.suggested_post_approval_failed = suggested_post_approval_failed
        self.suggested_post_approved = suggested_post_approved
        self.suggested_post_declined = suggested_post_declined
        self.suggested_post_paid = suggested_post_paid
        self.suggested_post_refunded = suggested_post_refunded
        self.giveaway_created = giveaway_created
        self.chat_set_theme = chat_set_theme
        self.chat_set_background = chat_set_background
        self.set_message_auto_delete_time = set_message_auto_delete_time
        self.chat_boost = chat_boost
        self.write_access_allowed = write_access_allowed
        self.connected_website = connected_website
        self.contact_registered = contact_registered
        self.proximity_alert_triggered = proximity_alert_triggered
        self.reactions = reactions
        self.send_paid_messages_stars = send_paid_messages_stars
        self.unread_media = unread_media
        self.silent = silent
        self.legacy = legacy
        self.pinned = pinned
        self.restriction_reason = restriction_reason
        self.fact_check = fact_check
        self.suggested_post_info = suggested_post_info
        self.channel_post = channel_post
        self.repeat_period = repeat_period
        self.summary_language_code = summary_language_code
        self.guest_bot_caller_user = guest_bot_caller_user
        self.guest_bot_caller_chat = guest_bot_caller_chat
        self.receiver_user = receiver_user
        self.ephemeral_message_id = ephemeral_message_id
        self.raw = raw

    @staticmethod
    async def _parse_service(
        client: pyrogram.Client,
        message: raw.types.MessageService,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
        replies: int = 1,
        business_connection_id: str | None = None,
        raw_reply_to_message: raw.base.Message | None = None,
    ) -> Message:
        from_id = utils.get_raw_peer_id(message.from_id)
        peer_id = utils.get_raw_peer_id(message.peer_id)

        if isinstance(message.from_id, raw.types.PeerUser) and isinstance(
            message.peer_id, raw.types.PeerUser
        ):
            if from_id not in users or peer_id not in users:
                try:
                    r = await client.invoke(
                        raw.functions.users.GetUsers(
                            id=[
                                await client.resolve_peer(from_id),
                                await client.resolve_peer(peer_id),
                            ]
                        )
                    )
                except PeerIdInvalid:
                    pass
                else:
                    users.update({i.id: i for i in r})

        from_user = types.User._parse(client, users.get(from_id or peer_id))
        chat = types.Chat._parse(client, message, users, chats, is_chat=True)

        if from_user:
            sender_chat = None
        elif (from_id or peer_id) == (peer_id or from_id):
            sender_chat = chat
        else:
            sender_chat = types.Chat._parse(client, message, users, chats, is_chat=False)

        action = message.action

        connected_website = None
        write_access_allowed = None
        chat_boost = None
        supergroup_chat_created = None
        channel_chat_created = None
        migrate_from_chat_id = None
        new_chat_members = None
        chat_join_type = None
        group_chat_created = None
        delete_chat_photo = None
        left_chat_member = None
        chat_owner_left = None
        chat_owner_changed = None
        new_chat_photo = None
        new_chat_title = None
        migrate_to_chat_id = None
        contact_registered = None
        text = None
        proximity_alert_triggered = None
        premium_gift_code = None
        gifted_premium = None
        gifted_stars = None
        gifted_grams = None
        giveaway_created = None
        giveaway_completed = None
        managed_bot_created = None
        video_chat_ended = None
        video_chat_started = None
        video_chat_scheduled = None
        history_cleared = None
        video_chat_members_invited = None
        successful_payment = None
        refunded_payment = None
        suggested_post_approval_failed = None
        suggested_post_declined = None
        suggested_post_approved = None
        suggested_post_paid = None
        suggested_post_refunded = None
        phone_call_ended = None
        phone_call_started = None
        giveaway_prize_stars = None
        users_shared = None
        chat_shared = None
        screenshot_taken = None
        upgraded_gift_purchase_offer = None
        upgraded_gift_purchase_offer_rejected = None
        chat_has_protected_content_toggled = None
        chat_has_protected_content_disable_requested = None
        # passport_data_send = None
        # passport_data_received = None
        chat_set_theme = None
        chat_set_background = None
        set_message_auto_delete_time = None
        gift = None
        is_prepaid_upgrade = None
        is_from_auction = None
        suggest_profile_photo = None
        suggest_birthday = None
        forum_topic_created = None
        forum_topic_edited = None
        general_forum_topic_hidden = None
        forum_topic_closed = None
        general_forum_topic_unhidden = None
        forum_topic_reopened = None
        web_app_data = None
        paid_messages_refunded = None
        paid_messages_price_changed = None
        direct_message_price_changed = None
        checklist_tasks_done = None
        checklist_tasks_added = None
        community_chat_added = None
        community_chat_joined = None
        community_chat_removed = None

        service_type = enums.MessageServiceType.UNSUPPORTED

        if isinstance(action, raw.types.MessageActionBotAllowed):
            if getattr(action, "domain", None):
                service_type = enums.MessageServiceType.CONNECTED_WEBSITE
                connected_website = action.domain
            else:
                service_type = enums.MessageServiceType.WRITE_ACCESS_ALLOWED
                write_access_allowed = types.WriteAccessAllowed._parse(action)
        elif isinstance(action, raw.types.MessageActionBoostApply):
            service_type = enums.MessageServiceType.CHAT_BOOST
            chat_boost = action.boosts
        elif isinstance(action, raw.types.MessageActionChannelCreate):
            service_type = enums.MessageServiceType.CHANNEL_CHAT_CREATED

            if chat.type == enums.ChatType.SUPERGROUP:
                supergroup_chat_created = True
                service_type = enums.MessageServiceType.SUPERGROUP_CHAT_CREATED
            else:
                channel_chat_created = True
                service_type = enums.MessageServiceType.CHANNEL_CHAT_CREATED
        elif isinstance(action, raw.types.MessageActionChannelMigrateFrom):
            service_type = enums.MessageServiceType.MIGRATE_FROM_CHAT_ID
            migrate_from_chat_id = -action.chat_id
        elif isinstance(action, raw.types.MessageActionChatAddUser):
            service_type = enums.MessageServiceType.NEW_CHAT_MEMBERS
            new_chat_members = [types.User._parse(client, users[i]) for i in action.users]
            chat_join_type = enums.ChatJoinType.BY_ADD
        elif isinstance(action, raw.types.MessageActionChatCreate):
            service_type = enums.MessageServiceType.GROUP_CHAT_CREATED
            group_chat_created = True
        elif isinstance(action, raw.types.MessageActionChatDeletePhoto):
            service_type = enums.MessageServiceType.DELETE_CHAT_PHOTO
            delete_chat_photo = True
        elif isinstance(action, raw.types.MessageActionChatDeleteUser):
            service_type = enums.MessageServiceType.LEFT_CHAT_MEMBER
            left_chat_member = types.User._parse(client, users[action.user_id])
        elif isinstance(action, raw.types.MessageActionNewCreatorPending):
            service_type = enums.MessageServiceType.CHAT_OWNER_LEFT
            chat_owner_left = types.ChatOwnerLeft._parse(client, action, users)
        elif isinstance(action, raw.types.MessageActionChangeCreator):
            service_type = enums.MessageServiceType.CHAT_OWNER_CHANGED
            chat_owner_changed = types.ChatOwnerChanged._parse(client, action, users)
        elif isinstance(action, raw.types.MessageActionChatEditPhoto):
            service_type = enums.MessageServiceType.NEW_CHAT_PHOTO
            new_chat_photo = types.Photo._parse(client, action.photo)
        elif isinstance(action, raw.types.MessageActionChatEditTitle):
            service_type = enums.MessageServiceType.NEW_CHAT_TITLE
            new_chat_title = action.title
        elif isinstance(action, raw.types.MessageActionChatJoinedByLink):
            service_type = enums.MessageServiceType.NEW_CHAT_MEMBERS
            joined_peer_id = utils.get_raw_peer_id(message.from_id)
            if joined_peer_id in users:
                new_chat_members = [types.User._parse(client, users[joined_peer_id])]
            chat_join_type = enums.ChatJoinType.BY_LINK
        elif isinstance(action, raw.types.MessageActionChatJoinedByRequest):
            service_type = enums.MessageServiceType.NEW_CHAT_MEMBERS
            joined_peer_id = utils.get_raw_peer_id(message.from_id)
            if joined_peer_id in users:
                new_chat_members = [types.User._parse(client, users[joined_peer_id])]
            chat_join_type = enums.ChatJoinType.BY_REQUEST
        elif isinstance(action, raw.types.MessageActionChatMigrateTo):
            service_type = enums.MessageServiceType.MIGRATE_TO_CHAT_ID
            migrate_to_chat_id = utils.get_channel_id(action.channel_id)
        elif isinstance(action, raw.types.MessageActionContactSignUp):
            service_type = enums.MessageServiceType.CONTACT_REGISTERED
            contact_registered = types.ContactRegistered()
        elif isinstance(action, raw.types.MessageActionCustomAction):
            service_type = enums.MessageServiceType.CUSTOM_ACTION
            text = action.message
        elif isinstance(action, raw.types.MessageActionGeoProximityReached):
            service_type = enums.MessageServiceType.PROXIMITY_ALERT_TRIGGERED
            proximity_alert_triggered = types.ProximityAlertTriggered._parse(
                client, action, users, chats
            )
        elif isinstance(action, raw.types.MessageActionGiftCode):
            service_type = enums.MessageServiceType.PREMIUM_GIFT_CODE
            premium_gift_code = await types.PremiumGiftCode._parse(client, action, users, chats)
        elif isinstance(action, raw.types.MessageActionGiftPremium):
            service_type = enums.MessageServiceType.GIFTED_PREMIUM
            gifted_premium = await types.GiftedPremium._parse(
                client,
                action,
                gifter=users.get(from_id),
                receiver=users.get(peer_id or from_id),
                users=users,
            )
        elif isinstance(action, raw.types.MessageActionGiftStars):
            service_type = enums.MessageServiceType.GIFTED_STARS
            gifted_stars = await types.GiftedStars._parse(
                client, action, gifter=users.get(from_id), receiver=users.get(peer_id or from_id)
            )
        elif isinstance(action, raw.types.MessageActionGiftTon):
            service_type = enums.MessageServiceType.GIFTED_GRAMS
            gifted_grams = await types.GiftedGrams._parse(
                client, action, gifter=users.get(from_id), receiver=users.get(peer_id or from_id)
            )
        elif isinstance(action, raw.types.MessageActionGiveawayLaunch):
            service_type = enums.MessageServiceType.GIVEAWAY_CREATED
            giveaway_created = types.GiveawayCreated._parse(client, action)
        elif isinstance(action, raw.types.MessageActionGiveawayResults):
            service_type = enums.MessageServiceType.GIVEAWAY_COMPLETED
            giveaway_completed = await types.GiveawayCompleted._parse(
                client,
                action,
                types.Chat._parse(client, message, users, chats, is_chat=True),
                getattr(getattr(message, "reply_to", None), "reply_to_msg_id", None),
            )
        elif isinstance(action, raw.types.MessageActionManagedBotCreated):
            service_type = enums.MessageServiceType.MANAGED_BOT_CREATED
            managed_bot_created = await types.ManagedBotCreated._parse(client, action, users)
        elif isinstance(action, raw.types.MessageActionGroupCall):
            if action.duration:
                service_type = enums.MessageServiceType.VIDEO_CHAT_ENDED
                video_chat_ended = types.VideoChatEnded._parse(action)
            else:
                service_type = enums.MessageServiceType.VIDEO_CHAT_STARTED
                video_chat_started = types.VideoChatStarted()
        elif isinstance(action, raw.types.MessageActionGroupCallScheduled):
            service_type = enums.MessageServiceType.VIDEO_CHAT_SCHEDULED
            video_chat_scheduled = types.VideoChatScheduled._parse(action)
        elif isinstance(action, raw.types.MessageActionConferenceCall):
            service_type = enums.MessageServiceType.CONFERENCE_CALL
        elif isinstance(action, raw.types.MessageActionHistoryClear):
            service_type = enums.MessageServiceType.HISTORY_CLEARED
            history_cleared = types.HistoryCleared()
        elif isinstance(action, raw.types.MessageActionInviteToGroupCall):
            service_type = enums.MessageServiceType.VIDEO_CHAT_MEMBERS_INVITED
            video_chat_members_invited = types.VideoChatMembersInvited._parse(client, action, users)
        elif isinstance(
            action, (raw.types.MessageActionPaymentSent, raw.types.MessageActionPaymentSentMe)
        ):
            service_type = enums.MessageServiceType.SUCCESSFUL_PAYMENT
            successful_payment = types.SuccessfulPayment._parse(action)
        elif isinstance(action, raw.types.MessageActionPaymentRefunded):
            service_type = enums.MessageServiceType.REFUNDED_PAYMENT
            refunded_payment = types.RefundedPayment._parse(action)
        elif isinstance(action, raw.types.MessageActionSuggestedPostApproval):
            if action.balance_too_low:
                service_type = enums.MessageServiceType.SUGGESTED_POST_APPROVAL_FAILED
                suggested_post_approval_failed = await types.SuggestedPostApprovalFailed._parse(
                    client, message
                )
            elif action.rejected:
                service_type = enums.MessageServiceType.SUGGESTED_POST_DECLINED
                suggested_post_declined = await types.SuggestedPostDeclined._parse(client, message)
            else:
                service_type = enums.MessageServiceType.SUGGESTED_POST_APPROVED
                suggested_post_approved = await types.SuggestedPostApproved._parse(client, message)
        elif isinstance(action, raw.types.MessageActionSuggestedPostSuccess):
            service_type = enums.MessageServiceType.SUGGESTED_POST_PAID
            suggested_post_paid = await types.SuggestedPostPaid._parse(client, message)
        elif isinstance(action, raw.types.MessageActionSuggestedPostRefund):
            service_type = enums.MessageServiceType.SUGGESTED_POST_REFUNDED
            suggested_post_refunded = await types.SuggestedPostRefunded._parse(client, message)
        elif isinstance(action, raw.types.MessageActionPhoneCall):
            if action.reason:
                service_type = enums.MessageServiceType.PHONE_CALL_ENDED
                phone_call_ended = types.PhoneCallEnded._parse(action)
            else:
                service_type = enums.MessageServiceType.PHONE_CALL_STARTED
                phone_call_started = types.PhoneCallStarted._parse(action)
        elif isinstance(action, raw.types.MessageActionPrizeStars):
            service_type = enums.MessageServiceType.GIVEAWAY_PRIZE_STARS
            giveaway_prize_stars = await types.GiveawayPrizeStars._parse(client, action, chats)
        elif isinstance(
            action,
            (raw.types.MessageActionRequestedPeer, raw.types.MessageActionRequestedPeerSentMe),
        ):
            _requested_chat = types.ChatShared._parse(client, action, chats)

            if _requested_chat is None:
                service_type = enums.MessageServiceType.USERS_SHARED
                users_shared = types.UsersShared._parse(client, action, users)
            else:
                service_type = enums.MessageServiceType.CHAT_SHARED
                chat_shared = _requested_chat
        elif isinstance(action, raw.types.MessageActionScreenshotTaken):
            service_type = enums.MessageServiceType.SCREENSHOT_TAKEN
            screenshot_taken = types.ScreenshotTaken()
        elif isinstance(action, raw.types.MessageActionStarGiftPurchaseOffer):
            service_type = enums.MessageServiceType.UPGRADED_GIFT_PURCHASE_OFFER
            upgraded_gift_purchase_offer = await types.UpgradedGiftPurchaseOffer._parse(
                client, action, users, chats
            )
        elif isinstance(action, raw.types.MessageActionStarGiftPurchaseOfferDeclined):
            service_type = enums.MessageServiceType.UPGRADED_GIFT_PURCHASE_OFFER_REJECTED
            upgraded_gift_purchase_offer_rejected = (
                await types.UpgradedGiftPurchaseOfferRejected._parse(
                    client, action, getattr(message.reply_to, "reply_to_msg_id", None), users, chats
                )
            )
        elif isinstance(action, raw.types.MessageActionNoForwardsToggle):
            service_type = enums.MessageServiceType.CHAT_HAS_PROTECTED_CONTENT_TOGGLED
            chat_has_protected_content_toggled = types.ChatHasProtectedContentToggled._parse(
                getattr(message.reply_to, "reply_to_msg_id", None), action
            )
        elif isinstance(action, raw.types.MessageActionNoForwardsRequest):
            service_type = enums.MessageServiceType.CHAT_HAS_PROTECTED_CONTENT_DISABLE_REQUESTED
            chat_has_protected_content_disable_requested = (
                types.ChatHasProtectedContentDisableRequested._parse(action)
            )
        elif isinstance(action, raw.types.MessageActionSecureValuesSent):
            service_type = enums.MessageServiceType.PASSPORT_DATA_SEND
        elif isinstance(action, raw.types.MessageActionSecureValuesSentMe):
            service_type = enums.MessageServiceType.PASSPORT_DATA_RECEIVED
        elif isinstance(action, raw.types.MessageActionSetChatTheme):
            service_type = enums.MessageServiceType.CHAT_SET_THEME
            chat_set_theme = await types.ChatTheme._parse(client, action.theme)
        elif isinstance(action, raw.types.MessageActionSetChatWallPaper):
            service_type = enums.MessageServiceType.CHAT_SET_BACKGROUND
            chat_set_background = types.ChatBackground._parse(
                client, action.wallpaper, action.same, action.for_both
            )
        elif isinstance(action, raw.types.MessageActionSetMessagesTTL):
            service_type = enums.MessageServiceType.SET_MESSAGE_AUTO_DELETE_TIME
            set_message_auto_delete_time = action.period
        elif isinstance(
            action, (raw.types.MessageActionStarGift, raw.types.MessageActionStarGiftUnique)
        ):
            service_type = enums.MessageServiceType.GIFT
            is_prepaid_upgrade = action.prepaid_upgrade
            is_from_auction = getattr(action, "auction_acquired", None)
            gift = await types.Gift._parse(client, action, users=users, chats=chats)
        elif isinstance(action, raw.types.MessageActionSuggestProfilePhoto):
            service_type = enums.MessageServiceType.SUGGEST_PROFILE_PHOTO
            suggest_profile_photo = types.Photo._parse(client, action.photo)
        elif isinstance(action, raw.types.MessageActionSuggestBirthday):
            service_type = enums.MessageServiceType.SUGGEST_BIRTHDAY
            suggest_birthday = types.Birthday._parse(action.birthday)
        elif isinstance(action, raw.types.MessageActionTopicCreate):
            service_type = enums.MessageServiceType.FORUM_TOPIC_CREATED
            forum_topic_created = types.ForumTopicCreated._parse(message)
        elif isinstance(action, raw.types.MessageActionTopicEdit):
            if action.hidden is True:
                service_type = enums.MessageServiceType.GENERAL_FORUM_TOPIC_HIDDEN
                general_forum_topic_hidden = types.GeneralForumTopicHidden()
            elif action.hidden is False:
                service_type = enums.MessageServiceType.GENERAL_FORUM_TOPIC_UNHIDDEN
                general_forum_topic_unhidden = types.GeneralForumTopicUnhidden()
            elif action.closed is True:
                service_type = enums.MessageServiceType.FORUM_TOPIC_CLOSED
                forum_topic_closed = types.ForumTopicClosed()
            elif action.closed is False:
                service_type = enums.MessageServiceType.FORUM_TOPIC_REOPENED
                forum_topic_reopened = types.ForumTopicReopened()
            else:
                service_type = enums.MessageServiceType.FORUM_TOPIC_EDITED
                forum_topic_edited = types.ForumTopicEdited._parse(action)
        elif isinstance(
            action,
            (raw.types.MessageActionWebViewDataSent, raw.types.MessageActionWebViewDataSentMe),
        ):
            service_type = enums.MessageServiceType.WEB_APP_DATA
            web_app_data = types.WebAppData._parse(action)
        elif isinstance(action, raw.types.MessageActionPaidMessagesRefunded):
            service_type = enums.MessageServiceType.PAID_MESSAGES_REFUNDED
            paid_messages_refunded = types.PaidMessagesRefunded._parse(action)
        elif isinstance(action, raw.types.MessageActionPaidMessagesPrice):
            if chat.type == enums.ChatType.PRIVATE:
                service_type = enums.MessageServiceType.DIRECT_MESSAGE_PRICE_CHANGED
                direct_message_price_changed = types.DirectMessagePriceChanged._parse(action)
            else:
                service_type = enums.MessageServiceType.PAID_MESSAGES_PRICE_CHANGED
                paid_messages_price_changed = types.PaidMessagesPriceChanged._parse(action)
        elif isinstance(action, raw.types.MessageActionTodoCompletions):
            service_type = enums.MessageServiceType.CHECKLIST_TASKS_DONE
            checklist_tasks_done = types.ChecklistTasksDone._parse(message)
        elif isinstance(action, raw.types.MessageActionTodoAppendTasks):
            service_type = enums.MessageServiceType.CHECKLIST_TASKS_ADDED
            checklist_tasks_added = types.ChecklistTasksAdded._parse(client, message, users, chats)
        elif isinstance(action, raw.types.MessageActionChangeCommunity):
            community_chat_added = types.CommunityChatAdded._parse(client, action, chats)
            community_chat_removed = types.CommunityChatRemoved._parse(action)

            if community_chat_added is not None:
                service_type = enums.MessageServiceType.COMMUNITY_CHAT_ADDED
            elif community_chat_removed is not None:
                service_type = enums.MessageServiceType.COMMUNITY_CHAT_REMOVED
        elif isinstance(action, raw.types.MessageActionChatJoinedViaCommunity):
            service_type = enums.MessageServiceType.COMMUNITY_CHAT_JOINED
            community_chat_joined = types.CommunityChatJoined._parse(client, action, chats)
            joined_peer_id = utils.get_raw_peer_id(message.from_id)
            if joined_peer_id in users:
                new_chat_members = [types.User._parse(client, users[joined_peer_id])]

        parsed_message = Message(
            id=message.id,
            date=utils.timestamp_to_datetime(message.date),
            chat=chat,
            from_user=from_user,
            sender_chat=sender_chat,
            service=service_type,
            connected_website=connected_website,
            write_access_allowed=write_access_allowed,
            chat_boost=chat_boost,
            supergroup_chat_created=supergroup_chat_created,
            channel_chat_created=channel_chat_created,
            migrate_from_chat_id=migrate_from_chat_id,
            new_chat_members=new_chat_members,
            chat_join_type=chat_join_type,
            group_chat_created=group_chat_created,
            delete_chat_photo=delete_chat_photo,
            left_chat_member=left_chat_member,
            chat_owner_left=chat_owner_left,
            chat_owner_changed=chat_owner_changed,
            new_chat_photo=new_chat_photo,
            new_chat_title=new_chat_title,
            migrate_to_chat_id=migrate_to_chat_id,
            contact_registered=contact_registered,
            text=text,
            proximity_alert_triggered=proximity_alert_triggered,
            premium_gift_code=premium_gift_code,
            gifted_premium=gifted_premium,
            gifted_stars=gifted_stars,
            gifted_grams=gifted_grams,
            giveaway_created=giveaway_created,
            giveaway_completed=giveaway_completed,
            managed_bot_created=managed_bot_created,
            video_chat_ended=video_chat_ended,
            video_chat_started=video_chat_started,
            video_chat_scheduled=video_chat_scheduled,
            history_cleared=history_cleared,
            video_chat_members_invited=video_chat_members_invited,
            successful_payment=successful_payment,
            refunded_payment=refunded_payment,
            suggested_post_approval_failed=suggested_post_approval_failed,
            suggested_post_declined=suggested_post_declined,
            suggested_post_approved=suggested_post_approved,
            suggested_post_paid=suggested_post_paid,
            suggested_post_refunded=suggested_post_refunded,
            suggest_birthday=suggest_birthday,
            phone_call_ended=phone_call_ended,
            phone_call_started=phone_call_started,
            giveaway_prize_stars=giveaway_prize_stars,
            users_shared=users_shared,
            chat_shared=chat_shared,
            screenshot_taken=screenshot_taken,
            upgraded_gift_purchase_offer=upgraded_gift_purchase_offer,
            upgraded_gift_purchase_offer_rejected=upgraded_gift_purchase_offer_rejected,
            chat_has_protected_content_toggled=chat_has_protected_content_toggled,
            chat_has_protected_content_disable_requested=chat_has_protected_content_disable_requested,
            chat_set_theme=chat_set_theme,
            chat_set_background=chat_set_background,
            set_message_auto_delete_time=set_message_auto_delete_time,
            gift=gift,
            is_prepaid_upgrade=is_prepaid_upgrade,
            is_from_auction=is_from_auction,
            suggest_profile_photo=suggest_profile_photo,
            forum_topic_created=forum_topic_created,
            forum_topic_edited=forum_topic_edited,
            general_forum_topic_hidden=general_forum_topic_hidden,
            forum_topic_closed=forum_topic_closed,
            general_forum_topic_unhidden=general_forum_topic_unhidden,
            forum_topic_reopened=forum_topic_reopened,
            web_app_data=web_app_data,
            paid_messages_refunded=paid_messages_refunded,
            paid_messages_price_changed=paid_messages_price_changed,
            direct_message_price_changed=direct_message_price_changed,
            checklist_tasks_done=checklist_tasks_done,
            checklist_tasks_added=checklist_tasks_added,
            community_chat_added=community_chat_added,
            community_chat_joined=community_chat_joined,
            community_chat_removed=community_chat_removed,
            reactions=types.MessageReactions._parse(client, message.reactions, users, chats),
            business_connection_id=business_connection_id,
            raw=message,
            client=client,
        )

        if message.reply_to:
            parsed_message = await types.Message.__parse_reply(
                client=client,
                parsed_message=parsed_message,
                message=message,
                users=users,
                chats=chats,
                replies=replies,
                business_connection_id=business_connection_id,
                raw_reply_to_message=raw_reply_to_message,
            )

        if isinstance(action, raw.types.MessageActionGameScore):
            parsed_message.service = enums.MessageServiceType.GAME_HIGH_SCORE
            parsed_message.game_high_score = types.GameHighScore._parse_action(
                client, message, users
            )
        elif isinstance(action, raw.types.MessageActionPinMessage):
            parsed_message.service = enums.MessageServiceType.PINNED_MESSAGE
            parsed_message.pinned_message = parsed_message.reply_to_message  # Why...
        elif isinstance(action, raw.types.MessageActionPollAppendAnswer):
            parsed_message.service = enums.MessageServiceType.POLL_OPTION_ADDED
            parsed_message.poll_option_added = await types.PollOptionAdded._parse(
                client, parsed_message.reply_to_message, action
            )
        elif isinstance(action, raw.types.MessageActionPollDeleteAnswer):
            parsed_message.service = enums.MessageServiceType.POLL_OPTION_DELETED
            parsed_message.poll_option_deleted = await types.PollOptionDeleted._parse(
                client, parsed_message.reply_to_message, action
            )

        client.message_cache[(parsed_message.chat.id, parsed_message.id)] = parsed_message

        return parsed_message

    @staticmethod
    async def _parse_message(
        client: pyrogram.Client,
        message: raw.types.Message,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
        topics: dict[int, raw.base.ForumTopic] | None = None,
        is_scheduled: bool = False,
        replies: int = 1,
        business_connection_id: str | None = None,
        guest_query_id: str | None = None,
        raw_reply_to_message: raw.base.Message | None = None,
    ) -> Message:
        from_id = utils.get_raw_peer_id(message.from_id)
        peer_id = utils.get_raw_peer_id(message.peer_id)

        if isinstance(message.from_id, raw.types.PeerUser) and isinstance(
            message.peer_id, raw.types.PeerUser
        ):
            if from_id not in users or peer_id not in users:
                try:
                    r = await client.invoke(
                        raw.functions.users.GetUsers(
                            id=[
                                await client.resolve_peer(from_id),
                                await client.resolve_peer(peer_id),
                            ]
                        )
                    )
                except PeerIdInvalid:
                    pass
                else:
                    users.update({i.id: i for i in r})

        # read once: each of these is asked for twice below, and for an ordinary
        # message all of them are absent
        guest_caller_id = utils.get_raw_peer_id(message.guestchat_via_from)
        business_bot_id = getattr(message, "via_business_bot_id", None)

        from_user = types.User._parse(client, users.get(from_id or peer_id))
        chat = types.Chat._parse(client, message, users, chats, is_chat=True)

        if from_user:
            sender_chat = None
        elif (from_id or peer_id) == (peer_id or from_id):
            sender_chat = chat
        else:
            sender_chat = types.Chat._parse(client, message, users, chats, is_chat=False)

        entities = types.List(
            filter(
                lambda x: x is not None,
                [types.MessageEntity._parse(client, entity, users) for entity in message.entities],
            )
        )

        forward_header = message.fwd_from
        forward_origin = None

        if forward_header:
            forward_origin = types.MessageOrigin._parse(
                client,
                forward_header,
                users,
                chats,
            )

        photo = None
        live_photo = None
        location = None
        contact = None
        venue = None
        game = None
        giveaway = None
        giveaway_winners = None
        invoice = None
        story = None
        audio = None
        voice = None
        animation = None
        video = None
        video_note = None
        sticker = None
        document = None
        web_page = None
        link_preview_options = None
        poll = None
        dice = None
        paid_media = None
        checklist = None

        media = message.media
        media_type = None
        has_media_spoiler = None
        content = None

        if media:
            content = await types.MessageContent._parse(
                client,
                media,
                message=raw.types.TextWithEntities(text=message.message, entities=message.entities)
                if message.message
                else None,
                users=users,
                chats=chats,
            )
            has_media_spoiler = getattr(media, "spoiler", None)
            photo = content.photo
            live_photo = content.live_photo
            location = content.location
            contact = content.contact
            venue = content.venue
            game = content.game
            giveaway = content.giveaway
            giveaway_winners = content.giveaway_winners
            invoice = content.invoice
            story = content.story
            audio = content.audio
            voice = content.voice
            animation = content.animation
            video = content.video
            video_note = content.video_note
            sticker = content.sticker
            document = content.document
            web_page = content.web_page
            poll = content.poll
            dice = content.dice
            paid_media = content.paid_media
            checklist = content.checklist
            media_type = content.type

            if media_type == enums.MessageMediaType.UNSUPPORTED:
                media = None

        link_preview_options = types.LinkPreviewOptions._parse(
            media,
            getattr(getattr(media, "webpage", None), "url", utils.get_first_url(message.message)),
            message.invert_media,
        )

        reply_markup = _parse_reply_markup(message.reply_markup)

        reactions = (
            types.MessageReactions._parse(client, message.reactions, users, chats)
            if message.reactions is not None
            else None
        )

        parsed_message = Message(
            id=message.id,
            effect_id=getattr(message, "effect", None),
            rich_message=(
                await types.RichMessage._parse(client, message.rich_message, users, chats)
                if message.rich_message is not None
                else None
            ),
            date=utils.timestamp_to_datetime(message.date),
            guest_query_id=str(guest_query_id) if guest_query_id else None,
            chat=chat,
            from_user=from_user,
            sender_chat=sender_chat,
            sender_business_bot=(
                types.User._parse(client, users.get(business_bot_id))
                if business_bot_id is not None
                else None
            ),
            sender_tag=message.from_rank,
            text=(
                Str(message.message).init(entities) or None
                if media is None or web_page is not None
                else None
            ),
            caption=(
                Str(message.message).init(entities) or None
                if media is not None and web_page is None
                else None
            ),
            entities=(entities or None if media is None or web_page is not None else None),
            caption_entities=(entities or None if media is not None and web_page is None else None),
            author_signature=message.post_author,
            is_paid_post=bool(getattr(message.suggested_post, "price", None)),
            has_protected_content=message.noforwards,
            has_media_spoiler=has_media_spoiler,
            forward_origin=forward_origin,
            mentioned=message.mentioned,
            scheduled=is_scheduled,
            from_scheduled=message.from_scheduled,
            media=media_type,
            media_content=content,
            paid_media=paid_media,
            checklist=checklist,
            show_caption_above_media=message.invert_media,
            edit_date=utils.timestamp_to_datetime(message.edit_date),
            edit_hidden=message.edit_hide,
            media_group_id=message.grouped_id,
            photo=photo,
            live_photo=live_photo,
            location=location,
            contact=contact,
            venue=venue,
            audio=audio,
            voice=voice,
            animation=animation,
            game=game,
            giveaway=giveaway,
            giveaway_winners=giveaway_winners,
            invoice=invoice,
            story=story,
            video=video,
            video_processing_pending=message.video_processing_pending,
            video_note=video_note,
            sticker=sticker,
            document=document,
            web_page=web_page,
            link_preview_options=link_preview_options,
            poll=poll,
            dice=dice,
            views=message.views,
            forwards=message.forwards,
            sender_boost_count=message.from_boosts_applied,
            via_bot=(
                types.User._parse(client, users.get(message.via_bot_id))
                if message.via_bot_id is not None
                else None
            ),
            outgoing=message.out,
            business_connection_id=business_connection_id,
            reply_markup=reply_markup,
            reactions=reactions,
            from_offline=message.offline,
            send_paid_messages_stars=message.paid_message_stars,
            unread_media=message.media_unread,
            silent=message.silent,
            pinned=message.pinned,
            restriction_reason=types.List(
                types.RestrictionReason._parse(reason)
                for reason in (getattr(message, "restriction_reason", None) or [])
            )
            or None,
            fact_check=(
                types.FactCheck._parse(client, message.factcheck, users)
                if message.factcheck is not None
                else None
            ),
            suggested_post_info=(
                types.SuggestedPostInfo._parse(message.suggested_post)
                if message.suggested_post is not None
                else None
            ),
            channel_post=message.post,
            repeat_period=message.schedule_repeat_period,
            summary_language_code=message.summary_from_language,
            guest_bot_caller_user=(
                types.User._parse(client, users.get(guest_caller_id))
                if guest_caller_id is not None
                else None
            ),
            guest_bot_caller_chat=(
                types.Chat._parse_chat(client, chats.get(guest_caller_id))
                if guest_caller_id is not None
                else None
            ),
            raw=message,
            client=client,
        )

        if forward_header and forward_header.saved_from_peer and forward_header.saved_from_msg_id:
            saved_from_peer_id = utils.get_raw_peer_id(forward_header.saved_from_peer)
            saved_from_peer_chat = chats.get(saved_from_peer_id)
            if (
                isinstance(saved_from_peer_chat, raw.types.Channel)
                and not saved_from_peer_chat.megagroup
            ):
                parsed_message.automatic_forward = True

        if message.reply_to:
            parsed_message = await types.Message.__parse_reply(
                client=client,
                parsed_message=parsed_message,
                message=message,
                users=users,
                chats=chats,
                replies=replies,
                business_connection_id=business_connection_id,
                raw_reply_to_message=raw_reply_to_message,
            )

        if topics:
            parsed_message.topic = types.ForumTopic._parse(
                client, topics.get(parsed_message.message_thread_id), users=users, chats=chats
            )

            if parsed_message.topic:
                client.topic_cache[(parsed_message.chat.id, parsed_message.topic.id)] = (
                    parsed_message.topic
                )

        if not parsed_message.topic and parsed_message.chat.is_forum:
            parsed_topic = client.topic_cache[
                (parsed_message.chat.id, parsed_message.message_thread_id or 1)
            ]

            if parsed_topic:
                parsed_message.topic = parsed_topic
            elif client.fetch_topics and client.me and not client.me.is_bot:
                try:
                    parsed_message.topic = await client.get_forum_topics_by_id(
                        chat_id=parsed_message.chat.id,
                        topic_ids=parsed_message.message_thread_id or 1,
                    )

                    if parsed_message.topic:
                        client.topic_cache[(parsed_message.chat.id, parsed_message.topic.id)] = (
                            parsed_message.topic
                        )
                except (ChannelPrivate, ChannelForumMissing, RPCError, KeyError):
                    pass

        if chat.is_direct_messages and message.saved_peer_id:
            parsed_message.direct_messages_topic_id = message.saved_peer_id.user_id

            parsed_topic = client.topic_cache[
                (parsed_message.chat.id, parsed_message.direct_messages_topic_id)
            ]

            if parsed_topic:
                parsed_message.topic = parsed_topic
            elif client.fetch_topics and client.me and not client.me.is_bot:
                try:
                    parsed_message.topic = await client.get_direct_messages_topics_by_id(
                        chat_id=parsed_message.chat.id,
                        topic_ids=parsed_message.direct_messages_topic_id,
                    )

                    if parsed_message.topic:
                        client.topic_cache[(parsed_message.chat.id, parsed_message.topic.id)] = (
                            parsed_message.topic
                        )
                except (ChannelPrivate, ChatAdminRequired, RPCError, KeyError):
                    pass

        if not parsed_message.poll:  # Do not cache poll messages
            client.message_cache[(parsed_message.chat.id, parsed_message.id)] = parsed_message

        return parsed_message

    @staticmethod
    async def __parse_reply(
        client: pyrogram.Client,
        parsed_message: Message,
        message: raw.base.Message,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
        replies: int = 1,
        business_connection_id: str | None = None,
        raw_reply_to_message: raw.base.Message | None = None,
    ):
        if isinstance(message.reply_to, raw.types.MessageReplyHeader):
            parsed_message.reply_to_message_id = message.reply_to.reply_to_msg_id
            parsed_message.reply_to_top_message_id = message.reply_to.reply_to_top_id
            parsed_message.reply_to_checklist_task_id = message.reply_to.todo_item_id
            parsed_message.reply_to_poll_option_id = (
                message.reply_to.poll_option.decode("utf-8")
                if message.reply_to.poll_option is not None
                else None
            )

            if replies:
                if message.reply_to.reply_to_peer_id:
                    key = (
                        utils.get_peer_id(message.reply_to.reply_to_peer_id),
                        message.reply_to.reply_to_msg_id,
                    )
                    reply_to_params = {"chat_id": key[0], "message_ids": key[1]}
                else:
                    key = (parsed_message.chat.id, parsed_message.reply_to_message_id)
                    reply_to_params = {"chat_id": key[0], "reply_to_message_ids": message.id}

                parsed_message.reply_to_message = client.message_cache[key]

                if raw_reply_to_message:  # For business bots only
                    parsed_message.reply_to_message = await types.Message._parse(
                        client,
                        raw_reply_to_message,
                        users,
                        chats,
                        business_connection_id=business_connection_id,
                        replies=0,
                    )
                elif client.fetch_replies and not parsed_message.reply_to_message:
                    with contextlib.suppress(ChannelPrivate, ChannelInvalid, MessageIdsEmpty):
                        parsed_message.reply_to_message = await client.get_messages(
                            replies=replies - 1, **reply_to_params
                        )

            if message.reply_to.forum_topic:
                parsed_message.topic_message = True

                if message.reply_to.reply_to_top_id:
                    parsed_message.message_thread_id = message.reply_to.reply_to_top_id
                elif message.reply_to.reply_to_msg_id:
                    parsed_message.message_thread_id = message.reply_to.reply_to_msg_id
                else:
                    parsed_message.message_thread_id = 1

            if message.reply_to.quote:
                parsed_message.quote = types.TextQuote._parse(client, users, message.reply_to)

            if message.reply_to.reply_from:
                parsed_message.external_reply = await types.ExternalReplyInfo._parse(
                    client, message.reply_to, users, chats
                )
        elif isinstance(message.reply_to, raw.types.MessageReplyStoryHeader):
            parsed_message.reply_to_story_id = message.reply_to.story_id
            parsed_message.reply_to_story_user_id = utils.get_peer_id(message.reply_to.peer)

            if client.fetch_stories and client.me and not client.me.is_bot:
                parsed_message.reply_to_story = await client.get_stories(
                    utils.get_peer_id(message.reply_to.peer), message.reply_to.story_id
                )

        return parsed_message

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        message: raw.base.Message,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
        topics: dict[int, raw.base.ForumTopic] | None = None,
        is_scheduled: bool = False,
        replies: int = 1,
        business_connection_id: str | None = None,
        guest_query_id: str | None = None,
        raw_reply_to_message: raw.base.Message | None = None,
    ) -> Message:
        if isinstance(client, pyrogram.Client):
            client.register_min_peers_from_message(message, users, chats)

        if isinstance(message, raw.types.MessageEmpty):
            return Message(
                id=message.id,
                empty=True,
                business_connection_id=business_connection_id,
                raw=message,
                client=client,
            )

        if isinstance(message, raw.types.MessageService):
            return await types.Message._parse_service(
                client=client,
                message=message,
                users=users,
                chats=chats,
                replies=replies,
                business_connection_id=business_connection_id,
                raw_reply_to_message=raw_reply_to_message,
            )

        if isinstance(message, raw.types.Message):
            return await types.Message._parse_message(
                client=client,
                message=message,
                users=users,
                chats=chats,
                topics=topics,
                is_scheduled=is_scheduled,
                replies=replies,
                business_connection_id=business_connection_id,
                guest_query_id=guest_query_id,
                raw_reply_to_message=raw_reply_to_message,
            )

        if isinstance(message, raw.types.EphemeralMessage):
            from_user = types.User._parse(client, users.get(utils.get_raw_peer_id(message.from_id)))
            rich_message = (
                await types.RichMessage._parse(client, message.rich_message, users, chats)
                if message.rich_message
                else None
            )

            if message.peer_id is not None:
                chat = types.Chat._parse(client, message, users, chats, is_chat=True)
            else:
                counterpart = (
                    message.receiver_id if message.out else utils.get_raw_peer_id(message.from_id)
                )
                chat = types.Chat._parse_user_chat(client, users.get(counterpart))

            receiver_user = types.User._parse(client, users.get(message.receiver_id))

            entities = types.List(
                filter(
                    lambda x: x is not None,
                    [
                        types.MessageEntity._parse(client, entity, users)
                        for entity in message.entities or []
                    ],
                )
            )

            reply_markup = _parse_reply_markup(message.reply_markup)

            return Message(
                id=message.id,
                from_user=from_user,
                chat=chat,
                receiver_user=receiver_user,
                ephemeral_message_id=message.id,
                date=utils.timestamp_to_datetime(message.date),
                outgoing=message.out,
                text=types.Str(message.message).init(entities) or None,
                entities=entities or None,
                reply_markup=reply_markup,
                message_thread_id=message.top_msg_id,
                rich_message=rich_message,
                is_welcome_template=message.welcome_template,
                show_caption_above_media=message.invert_media,
                has_protected_content=message.noforwards,
                anchor_message_id=message.anchor_msg_id,
                raw=message,
                client=client,
            )

    @property
    def link(self) -> str:
        if self.chat.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
            return ""

        if self.chat.username:
            if self.message_thread_id:
                return f"https://t.me/{self.chat.username}/{self.message_thread_id}/{self.id}"
            else:
                return f"https://t.me/{self.chat.username}/{self.id}"
        else:
            if self.message_thread_id:
                return f"https://t.me/c/{utils.get_channel_id(self.chat.id)}/{self.message_thread_id}/{self.id}"
            else:
                return f"https://t.me/c/{utils.get_channel_id(self.chat.id)}/{self.id}"

    @property
    def content(self) -> Str:
        return self.text or self.caption or Str("").init([])

    @property
    def md_text(self) -> str:
        return self.content.markdown

    @property
    def html_text(self) -> str:
        return self.content.html

    @property
    def is_topic_message(self) -> bool | None:
        return self.topic_message

    @property
    def forward_from(self) -> types.User | None:
        log.warning(
            "`message.forward_from` is deprecated and will be removed in future updates. Use `message.forward_origin.sender_user` instead."
        )
        return getattr(self.forward_origin, "sender_user", None)

    @property
    def forward_sender_name(self) -> str | None:
        log.warning(
            "`message.forward_sender_name` property is deprecated and will be removed in future updates. Use `message.forward_origin.sender_user_name` instead."
        )
        return getattr(self.forward_origin, "sender_user_name", None)

    @property
    def forward_from_chat(self) -> types.Chat | None:
        log.warning(
            "`message.forward_from_chat` property is deprecated and will be removed in future updates. Use `message.forward_origin.chat.sender_chat` instead."
        )
        return getattr(
            self.forward_origin, "chat", getattr(self.forward_origin, "sender_chat", None)
        )

    @property
    def forward_from_message_id(self) -> int | None:
        log.warning(
            "`message.forward_from_message_id` property is deprecated and will be removed in future updates. Use `message.forward_origin.message_id` instead."
        )
        return getattr(self.forward_origin, "message_id", None)

    @property
    def forward_signature(self) -> str | None:
        log.warning(
            "`message.forward_signature` property is deprecated and will be removed in future updates. Use `message.forward_origin.author_signature` instead."
        )
        return getattr(self.forward_origin, "author_signature", None)

    @property
    def forward_date(self) -> datetime | None:
        log.warning(
            "`message.forward_date` property is deprecated and will be removed in future updates. Use `message.forward_origin.date` instead."
        )
        return getattr(self.forward_origin, "date", None)

    # endregion

    async def reply_animation(
        self,
        animation: str | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        show_caption_above_media: bool | None = None,
        duration: int = 0,
        width: int = 0,
        height: int = 0,
        thumb: str | BinaryIO | None = None,
        file_name: str | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        unsave: bool = False,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_animation` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            animation (``str``):
                Animation to send.
                Pass a file_id as string to send an animation that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get an animation from the Internet, or
                pass a file path as string to upload a new animation that exists on your local machine.

            caption (``str``, *optional*):
                Animation caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the animation needs to be covered with a spoiler animation.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            duration (``int``, *optional*):
                Duration of sent animation in seconds.

            width (``int``, *optional*):
                Animation width.

            height (``int``, *optional*):
                Animation height.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the animation file sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            file_name (``str``, *optional*):
                File name of the animation sent.
                Defaults to file's path basename.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            unsave (``bool``, *optional*):
                By default, the server will save into your own collection any new animation you send.
                Pass True to automatically unsave the sent animation. Defaults to False.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_animation(
            chat_id=self.chat.id,
            animation=animation,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            has_spoiler=has_spoiler,
            show_caption_above_media=show_caption_above_media,
            duration=duration,
            width=width,
            height=height,
            thumb=thumb,
            disable_notification=disable_notification,
            file_name=file_name,
            protect_content=protect_content,
            unsave=unsave,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )

    async def answer_animation(
        self,
        animation: str | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        show_caption_above_media: bool | None = None,
        duration: int = 0,
        width: int = 0,
        height: int = 0,
        thumb: str | BinaryIO | None = None,
        file_name: str | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        unsave: bool = False,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_animation` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            animation (``str``):
                Animation to send.
                Pass a file_id as string to send an animation that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get an animation from the Internet, or
                pass a file path as string to upload a new animation that exists on your local machine.

            caption (``str``, *optional*):
                Animation caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the animation needs to be covered with a spoiler animation.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            duration (``int``, *optional*):
                Duration of sent animation in seconds.

            width (``int``, *optional*):
                Animation width.

            height (``int``, *optional*):
                Animation height.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the animation file sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            file_name (``str``, *optional*):
                File name of the animation sent.
                Defaults to file's path basename.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            unsave (``bool``, *optional*):
                By default, the server will save into your own collection any new animation you send.
                Pass True to automatically unsave the sent animation. Defaults to False.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_animation(
            chat_id=self.chat.id,
            animation=animation,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            has_spoiler=has_spoiler,
            show_caption_above_media=show_caption_above_media,
            duration=duration,
            width=width,
            height=height,
            thumb=thumb,
            disable_notification=disable_notification,
            file_name=file_name,
            protect_content=protect_content,
            unsave=unsave,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_audio(
        self,
        audio: str | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        duration: int = 0,
        performer: str | None = None,
        title: str | None = None,
        thumb: str | BinaryIO | None = None,
        file_name: str | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_audio` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            audio (``str``):
                Audio file to send.
                Pass a file_id as string to send an audio file that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get an audio file from the Internet, or
                pass a file path as string to upload a new audio file that exists on your local machine.

            caption (``str``, *optional*):
                Audio caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            duration (``int``, *optional*):
                Duration of the audio in seconds.

            performer (``str``, *optional*):
                Performer.

            title (``str``, *optional*):
                Track name.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the music file album cover.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            file_name (``str``, *optional*):
                File name of the audio sent.
                Defaults to file's path basename.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_audio(
            chat_id=self.chat.id,
            audio=audio,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            duration=duration,
            performer=performer,
            title=title,
            thumb=thumb,
            disable_notification=disable_notification,
            file_name=file_name,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )

    async def answer_audio(
        self,
        audio: str | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        duration: int = 0,
        performer: str | None = None,
        title: str | None = None,
        thumb: str | BinaryIO | None = None,
        file_name: str | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_audio` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            audio (``str``):
                Audio file to send.
                Pass a file_id as string to send an audio file that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get an audio file from the Internet, or
                pass a file path as string to upload a new audio file that exists on your local machine.

            caption (``str``, *optional*):
                Audio caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            duration (``int``, *optional*):
                Duration of the audio in seconds.

            performer (``str``, *optional*):
                Performer.

            title (``str``, *optional*):
                Track name.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the music file album cover.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            file_name (``str``, *optional*):
                File name of the audio sent.
                Defaults to file's path basename.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_audio(
            chat_id=self.chat.id,
            audio=audio,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            duration=duration,
            performer=performer,
            title=title,
            thumb=thumb,
            disable_notification=disable_notification,
            file_name=file_name,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_contact(
        self,
        phone_number: str,
        first_name: str,
        last_name: str = "",
        vcard: str = "",
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_contact` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            phone_number (``str``):
                Contact's phone number.

            first_name (``str``):
                Contact's first name.

            last_name (``str``, *optional*):
                Contact's last name.

            vcard (``str``, *optional*):
                Additional data about the contact in the form of a vCard, 0-2048 bytes

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_contact(
            chat_id=self.chat.id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            vcard=vcard,
            disable_notification=disable_notification,
            schedule_date=schedule_date,
            protect_content=protect_content,
            suggested_post_parameters=suggested_post_parameters,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )

    async def answer_contact(
        self,
        phone_number: str,
        first_name: str,
        last_name: str = "",
        vcard: str = "",
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_contact` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            phone_number (``str``):
                Contact's phone number.

            first_name (``str``):
                Contact's first name.

            last_name (``str``, *optional*):
                Contact's last name.

            vcard (``str``, *optional*):
                Additional data about the contact in the form of a vCard, 0-2048 bytes

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_contact(
            chat_id=self.chat.id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            vcard=vcard,
            disable_notification=disable_notification,
            schedule_date=schedule_date,
            protect_content=protect_content,
            suggested_post_parameters=suggested_post_parameters,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            reply_markup=reply_markup,
        )

    async def reply_document(
        self,
        document: str | BinaryIO,
        thumb: str | BinaryIO | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        file_name: str | None = None,
        force_document: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_document` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            document (``str``):
                File to send.
                Pass a file_id as string to send a file that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a file from the Internet, or
                pass a file path as string to upload a new file that exists on your local machine.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the file sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            caption (``str``, *optional*):
                Document caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            file_name (``str``, *optional*):
                File name of the document sent.
                Defaults to file's path basename.

            force_document (``bool``, *optional*):
                Pass True to force sending files as document. Useful for video files that need to be sent as
                document messages instead of video messages.
                Defaults to False.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_document(
            chat_id=self.chat.id,
            document=document,
            thumb=thumb,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            file_name=file_name,
            force_document=force_document,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            protect_content=protect_content,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )

    async def answer_document(
        self,
        document: str | BinaryIO,
        thumb: str | BinaryIO | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        file_name: str | None = None,
        force_document: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_document` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            document (``str``):
                File to send.
                Pass a file_id as string to send a file that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a file from the Internet, or
                pass a file path as string to upload a new file that exists on your local machine.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the file sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            caption (``str``, *optional*):
                Document caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            file_name (``str``, *optional*):
                File name of the document sent.
                Defaults to file's path basename.

            force_document (``bool``, *optional*):
                Pass True to force sending files as document. Useful for video files that need to be sent as
                document messages instead of video messages.
                Defaults to False.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_document(
            chat_id=self.chat.id,
            document=document,
            thumb=thumb,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            file_name=file_name,
            force_document=force_document,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            protect_content=protect_content,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_game(
        self,
        game_short_name: str,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_game` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * reply_parameters

        Example:
            .. code-block:: python

                await message.reply_game("lumberjack")

        Parameters:
            game_short_name (``str``):
                Short name of the game, serves as the unique identifier for the game. Set up your games via Botfather.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For supergroups only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An object for an inline keyboard. If empty, one ‘Play game_title’ button will be shown automatically.
                If not empty, the first button must launch the game.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        return await self._client.send_game(
            chat_id=self.chat.id,
            game_short_name=game_short_name,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            allow_paid_broadcast=allow_paid_broadcast,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
        )

    async def answer_game(
        self,
        game_short_name: str,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_game` will automatically fill method attributes:

        * chat_id
        * message_thread_id

        Example:
            .. code-block:: python

                await message.reply_game("lumberjack")

        Parameters:
            game_short_name (``str``):
                Short name of the game, serves as the unique identifier for the game. Set up your games via Botfather.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For supergroups only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An object for an inline keyboard. If empty, one ‘Play game_title’ button will be shown automatically.
                If not empty, the first button must launch the game.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        return await self._client.send_game(
            chat_id=self.chat.id,
            game_short_name=game_short_name,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            allow_paid_broadcast=allow_paid_broadcast,
            reply_markup=reply_markup,
        )

    async def reply_invoice(
        self,
        title: str,
        description: str,
        payload: str | bytes,
        currency: str,
        prices: list[types.LabeledPrice],
        message_thread_id: int | None = None,
        provider_token: str | None = None,
        max_tip_amount: int | None = None,
        suggested_tip_amounts: list[int] | None = None,
        start_parameter: str | None = None,
        provider_data: str | None = None,
        photo_url: str | None = None,
        photo_size: int | None = None,
        photo_width: int | None = None,
        photo_height: int | None = None,
        need_name: bool | None = None,
        need_phone_number: bool | None = None,
        need_email: bool | None = None,
        need_shipping_address: bool | None = None,
        send_phone_number_to_provider: bool | None = None,
        send_email_to_provider: bool | None = None,
        is_flexible: bool | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        allow_paid_broadcast: bool | None = None,
        direct_messages_topic_id: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        subscription_period: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_invoice` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * reply_parameters

        Parameters:
            title (``str``):
                Product name, 1-32 characters.

            description (``str``):
                Product description, 1-255 characters.

            payload (``str`` | ``bytes``):
                Bot-defined invoice payload, 1-128 bytes. This will not be displayed to the user, use for your internal processes.

            currency (``str``):
                Three-letter ISO 4217 currency code, see `more on currencies <https://core.telegram.org/bots/payments#supported-currencies>`_. Pass ``XTR`` for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            prices (List of :obj:`~pyrogram.types.LabeledPrice`):
                Price breakdown, a JSON-serialized list of components (e.g. product price, tax, discount, delivery cost, delivery tax, bonus, etc.). Must contain exactly one item for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            message_thread_id (``int``, *optional*):
                If the message is in a thread, ID of the original message.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            provider_token (``str``, *optional*):
                Payment provider token, obtained via `@BotFather <https://t.me/botfather>`_. Pass an empty string for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            max_tip_amount (``int``, *optional*):
                The maximum accepted amount for tips in the smallest units of the currency (integer, **not** float/double). For example, for a maximum tip of ``US$ 1.45`` pass ``max_tip_amount = 145``. See the exp parameter in `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_, it shows the number of digits past the decimal point for each currency (2 for the majority of currencies). Defaults to 0. Not supported for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            suggested_tip_amounts (List of ``int``, *optional*):
                An array of suggested amounts of tips in the smallest units of the currency (integer, **not** float/double). At most 4 suggested tip amounts can be specified. The suggested tip amounts must be positive, passed in a strictly increased order and must not exceed ``max_tip_amount``.

            start_parameter (``str``, *optional*):
                Unique deep-linking parameter. If left empty, **forwarded copies** of the sent message will have a Pay button, allowing multiple users to pay directly from the forwarded message, using the same invoice. If non-empty, forwarded copies of the sent message will have a URL button with a deep link to the bot (instead of a Pay button), with the value used as the start parameter.

            provider_data (``str``, *optional*):
                JSON-serialized data about the invoice, which will be shared with the payment provider. A detailed description of required fields should be provided by the payment provider.

            photo_url (``str``, *optional*):
                URL of the product photo for the invoice. Can be a photo of the goods or a marketing image for a service. People like it better when they see what they are paying for.

            photo_size (``int``, *optional*):
                Photo size in bytes.

            photo_width (``int``, *optional*):
                Photo width.

            photo_height (``int``, *optional*):
                Photo height.

            need_name (``bool``, *optional*):
                Pass True if you require the user's full name to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            need_phone_number (``bool``, *optional*):
                Pass True if you require the user's phone number to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            need_email (``bool``, *optional*):
                Pass True if you require the user's email address to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            need_shipping_address (``bool``, *optional*):
                Pass True if you require the user's shipping address to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            send_phone_number_to_provider (``bool``, *optional*):
                Pass True if the user's phone number should be sent to the provider. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            send_email_to_provider (``bool``, *optional*):
                Pass True if the user's email address should be sent to the provider. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            is_flexible (``bool``, *optional*):
                Pass True if the final price depends on the shipping method. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            effect_id (``int`` ``64-bit``, *optional*):
                Unique identifier of the message effect to be added to the message; for private chats only.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only only.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            subscription_period (``int``, *optional*):
                Duration of the subscription, in seconds.
                Currently the only allowed subscription period is 30*24*60*60 (1 month).
                For recurring payments only.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            caption (``str``, *optional*):
                Document caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent invoice message is returned.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(message_id=self.id)

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_invoice(
            chat_id=self.chat.id,
            title=title,
            description=description,
            payload=payload,
            currency=currency,
            prices=prices,
            message_thread_id=message_thread_id,
            provider_token=provider_token,
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=suggested_tip_amounts,
            start_parameter=start_parameter,
            provider_data=provider_data,
            photo_url=photo_url,
            photo_size=photo_size,
            photo_width=photo_width,
            photo_height=photo_height,
            need_name=need_name,
            need_phone_number=need_phone_number,
            need_email=need_email,
            need_shipping_address=need_shipping_address,
            send_phone_number_to_provider=send_phone_number_to_provider,
            send_email_to_provider=send_email_to_provider,
            is_flexible=is_flexible,
            disable_notification=disable_notification,
            protect_content=protect_content,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            allow_paid_broadcast=allow_paid_broadcast,
            direct_messages_topic_id=direct_messages_topic_id,
            suggested_post_parameters=suggested_post_parameters,
            subscription_period=subscription_period,
            reply_markup=reply_markup,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )

    async def answer_invoice(
        self,
        title: str,
        description: str,
        payload: str | bytes,
        currency: str,
        prices: list[types.LabeledPrice],
        message_thread_id: int | None = None,
        provider_token: str | None = None,
        max_tip_amount: int | None = None,
        suggested_tip_amounts: list[int] | None = None,
        start_parameter: str | None = None,
        provider_data: str | None = None,
        photo_url: str | None = None,
        photo_size: int | None = None,
        photo_width: int | None = None,
        photo_height: int | None = None,
        need_name: bool | None = None,
        need_phone_number: bool | None = None,
        need_email: bool | None = None,
        need_shipping_address: bool | None = None,
        send_phone_number_to_provider: bool | None = None,
        send_email_to_provider: bool | None = None,
        is_flexible: bool | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        allow_paid_broadcast: bool | None = None,
        direct_messages_topic_id: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        subscription_period: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_invoice` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id

        Parameters:
            title (``str``):
                Product name, 1-32 characters.

            description (``str``):
                Product description, 1-255 characters.

            payload (``str`` | ``bytes``):
                Bot-defined invoice payload, 1-128 bytes. This will not be displayed to the user, use for your internal processes.

            currency (``str``):
                Three-letter ISO 4217 currency code, see `more on currencies <https://core.telegram.org/bots/payments#supported-currencies>`_. Pass ``XTR`` for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            prices (List of :obj:`~pyrogram.types.LabeledPrice`):
                Price breakdown, a JSON-serialized list of components (e.g. product price, tax, discount, delivery cost, delivery tax, bonus, etc.). Must contain exactly one item for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            message_thread_id (``int``, *optional*):
                If the message is in a thread, ID of the original message.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            provider_token (``str``, *optional*):
                Payment provider token, obtained via `@BotFather <https://t.me/botfather>`_. Pass an empty string for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            max_tip_amount (``int``, *optional*):
                The maximum accepted amount for tips in the smallest units of the currency (integer, **not** float/double). For example, for a maximum tip of ``US$ 1.45`` pass ``max_tip_amount = 145``. See the exp parameter in `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_, it shows the number of digits past the decimal point for each currency (2 for the majority of currencies). Defaults to 0. Not supported for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            suggested_tip_amounts (List of ``int``, *optional*):
                An array of suggested amounts of tips in the smallest units of the currency (integer, **not** float/double). At most 4 suggested tip amounts can be specified. The suggested tip amounts must be positive, passed in a strictly increased order and must not exceed ``max_tip_amount``.

            start_parameter (``str``, *optional*):
                Unique deep-linking parameter. If left empty, **forwarded copies** of the sent message will have a Pay button, allowing multiple users to pay directly from the forwarded message, using the same invoice. If non-empty, forwarded copies of the sent message will have a URL button with a deep link to the bot (instead of a Pay button), with the value used as the start parameter.

            provider_data (``str``, *optional*):
                JSON-serialized data about the invoice, which will be shared with the payment provider. A detailed description of required fields should be provided by the payment provider.

            photo_url (``str``, *optional*):
                URL of the product photo for the invoice. Can be a photo of the goods or a marketing image for a service. People like it better when they see what they are paying for.

            photo_size (``int``, *optional*):
                Photo size in bytes.

            photo_width (``int``, *optional*):
                Photo width.

            photo_height (``int``, *optional*):
                Photo height.

            need_name (``bool``, *optional*):
                Pass True if you require the user's full name to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            need_phone_number (``bool``, *optional*):
                Pass True if you require the user's phone number to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            need_email (``bool``, *optional*):
                Pass True if you require the user's email address to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            need_shipping_address (``bool``, *optional*):
                Pass True if you require the user's shipping address to complete the order. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            send_phone_number_to_provider (``bool``, *optional*):
                Pass True if the user's phone number should be sent to the provider. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            send_email_to_provider (``bool``, *optional*):
                Pass True if the user's email address should be sent to the provider. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            is_flexible (``bool``, *optional*):
                Pass True if the final price depends on the shipping method. Ignored for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            effect_id (``int`` ``64-bit``, *optional*):
                Unique identifier of the message effect to be added to the message; for private chats only.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only only.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            subscription_period (``int``, *optional*):
                Duration of the subscription, in seconds.
                Currently the only allowed subscription period is 30*24*60*60 (1 month).
                For recurring payments only.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            caption (``str``, *optional*):
                Document caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent invoice message is returned.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_invoice(
            chat_id=self.chat.id,
            title=title,
            description=description,
            payload=payload,
            currency=currency,
            prices=prices,
            message_thread_id=message_thread_id,
            provider_token=provider_token,
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=suggested_tip_amounts,
            start_parameter=start_parameter,
            provider_data=provider_data,
            photo_url=photo_url,
            photo_size=photo_size,
            photo_width=photo_width,
            photo_height=photo_height,
            need_name=need_name,
            need_phone_number=need_phone_number,
            need_email=need_email,
            need_shipping_address=need_shipping_address,
            send_phone_number_to_provider=send_phone_number_to_provider,
            send_email_to_provider=send_email_to_provider,
            is_flexible=is_flexible,
            disable_notification=disable_notification,
            protect_content=protect_content,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            allow_paid_broadcast=allow_paid_broadcast,
            direct_messages_topic_id=direct_messages_topic_id,
            suggested_post_parameters=suggested_post_parameters,
            subscription_period=subscription_period,
            reply_markup=reply_markup,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )

    async def reply_location(
        self,
        latitude: float,
        longitude: float,
        horizontal_accuracy: float | None = None,
        live_period: int | None = None,
        heading: int | None = None,
        proximity_alert_radius: int | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_location` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            latitude (``float``):
                Latitude of the location.

            longitude (``float``):
                Longitude of the location.

            horizontal_accuracy (``float``, *optional*):
                The radius of uncertainty for the location, measured in meters, 0-1500.

            live_period (``int``, *optional*):
                For live locations, a period for which the location can be updated, in seconds.
                Must be between 60 and 86400 for a temporary live location, 0x7FFFFFFF for permanent live location.

            heading (``int``, *optional*):
                For live locations, a direction in which the user is moving, in degrees.
                Must be between 1 and 360 if specified.

            proximity_alert_radius (``int``, *optional*):
                For live locations, a maximum distance for proximity alerts about approaching another chat member, in meters.
                Must be between 1 and 100000 if specified.
                Can't be enabled in channels and Saved Messages.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_location(
            chat_id=self.chat.id,
            latitude=latitude,
            longitude=longitude,
            horizontal_accuracy=horizontal_accuracy,
            live_period=live_period,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            disable_notification=disable_notification,
            schedule_date=schedule_date,
            protect_content=protect_content,
            suggested_post_parameters=suggested_post_parameters,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )

    async def answer_location(
        self,
        latitude: float,
        longitude: float,
        horizontal_accuracy: float | None = None,
        live_period: int | None = None,
        heading: int | None = None,
        proximity_alert_radius: int | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_location` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            latitude (``float``):
                Latitude of the location.

            longitude (``float``):
                Longitude of the location.

            horizontal_accuracy (``float``, *optional*):
                The radius of uncertainty for the location, measured in meters, 0-1500.

            live_period (``int``, *optional*):
                For live locations, a period for which the location can be updated, in seconds.
                Must be between 60 and 86400 for a temporary live location, 0x7FFFFFFF for permanent live location.

            heading (``int``, *optional*):
                For live locations, a direction in which the user is moving, in degrees.
                Must be between 1 and 360 if specified.

            proximity_alert_radius (``int``, *optional*):
                For live locations, a maximum distance for proximity alerts about approaching another chat member, in meters.
                Must be between 1 and 100000 if specified.
                Can't be enabled in channels and Saved Messages.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_location(
            chat_id=self.chat.id,
            latitude=latitude,
            longitude=longitude,
            horizontal_accuracy=horizontal_accuracy,
            live_period=live_period,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            disable_notification=disable_notification,
            schedule_date=schedule_date,
            protect_content=protect_content,
            suggested_post_parameters=suggested_post_parameters,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            reply_markup=reply_markup,
        )

    async def reply_live_photo(
        self,
        live_photo: str | BinaryIO,
        photo: str | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        width: int = 0,
        height: int = 0,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        show_caption_above_media: bool | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        ephemeral_message_parameters: types.EphemeralMessageParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_live_photo` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            live_photo (``str`` | ``BinaryIO``):
                Video part of the live photo, as a local path or a file-like object.

            photo (``str`` | ``BinaryIO``):
                Still part of the live photo, as a local path or a file-like object.

            caption (``str``, *optional*):
                Caption of the live photo, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the live photo needs to be covered with a spoiler animation.

            width (``int``, *optional*):
                Width of the video part.

            height (``int``, *optional*):
                Height of the video part.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the direct messages topic.

            effect_id (``int``, *optional*):
                Unique identifier of the effect to apply to the message.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                Pay to skip the broadcast flood limit.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the message.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

            ephemeral_message_parameters (:obj:`~pyrogram.types.EphemeralMessageParameters`, *optional*):
                Parameters of the ephemeral message to send.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(message_id=self.id)

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_live_photo(
            chat_id=self.chat.id,
            live_photo=live_photo,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            has_spoiler=has_spoiler,
            width=width,
            height=height,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            show_caption_above_media=show_caption_above_media,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            protect_content=protect_content,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            ephemeral_message_parameters=ephemeral_message_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def answer_live_photo(
        self,
        live_photo: str | BinaryIO,
        photo: str | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        width: int = 0,
        height: int = 0,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        show_caption_above_media: bool | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        ephemeral_message_parameters: types.EphemeralMessageParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_live_photo` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            live_photo (``str`` | ``BinaryIO``):
                Video part of the live photo, as a local path or a file-like object.

            photo (``str`` | ``BinaryIO``):
                Still part of the live photo, as a local path or a file-like object.

            caption (``str``, *optional*):
                Caption of the live photo, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the live photo needs to be covered with a spoiler animation.

            width (``int``, *optional*):
                Width of the video part.

            height (``int``, *optional*):
                Height of the video part.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the direct messages topic.

            effect_id (``int``, *optional*):
                Unique identifier of the effect to apply to the message.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                Pay to skip the broadcast flood limit.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the message.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

            ephemeral_message_parameters (:obj:`~pyrogram.types.EphemeralMessageParameters`, *optional*):
                Parameters of the ephemeral message to send.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_live_photo(
            chat_id=self.chat.id,
            live_photo=live_photo,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            has_spoiler=has_spoiler,
            width=width,
            height=height,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            show_caption_above_media=show_caption_above_media,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            protect_content=protect_content,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            ephemeral_message_parameters=ephemeral_message_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_media_group(
        self,
        media: list[types.InputMediaPhoto | types.InputMediaVideo],
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        show_caption_above_media: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> list[types.Message]:
        """Shortcut for method :obj:`~pyrogram.Client.send_media_group` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            media (``list``):
                A list containing either :obj:`~pyrogram.types.InputMediaPhoto` or
                :obj:`~pyrogram.types.InputMediaVideo` objects
                describing photos and videos to be sent, must include 2–10 items.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

        Returns:
            On success, a list of :obj:`~pyrogram.types.Message` objects is returned containing all the
            single messages sent.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_media_group(
            chat_id=self.chat.id,
            media=media,
            disable_notification=disable_notification,
            schedule_date=schedule_date,
            protect_content=protect_content,
            show_caption_above_media=show_caption_above_media,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            business_connection_id=self.business_connection_id,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )

    async def answer_media_group(
        self,
        media: list[types.InputMediaPhoto | types.InputMediaVideo],
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        show_caption_above_media: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
    ) -> list[types.Message]:
        """Shortcut for method :obj:`~pyrogram.Client.send_media_group` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            media (``list``):
                A list containing either :obj:`~pyrogram.types.InputMediaPhoto` or
                :obj:`~pyrogram.types.InputMediaVideo` objects
                describing photos and videos to be sent, must include 2–10 items.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

        Returns:
            On success, a list of :obj:`~pyrogram.types.Message` objects is returned containing all the
            single messages sent.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_media_group(
            chat_id=self.chat.id,
            media=media,
            disable_notification=disable_notification,
            schedule_date=schedule_date,
            protect_content=protect_content,
            show_caption_above_media=show_caption_above_media,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            business_connection_id=self.business_connection_id,
        )

    async def reply_rich(
        self,
        rich_text: str | types.InputRichMessage,
        parse_mode: enums.ParseMode | None = None,
        media: list[types.InputRichMessageMedia] | None = None,
        disable_web_page_preview: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        show_caption_above_media: bool | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_rich_message` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Example:
            .. code-block:: python

                await message.reply_rich("# Title\n\nSome **rich** text")

        Parameters:
            rich_text (``str`` | :obj:`~pyrogram.types.InputRichMessage`):
                Rich text (Markdown or HTML) to render a styled message, or a whole
                :obj:`~pyrogram.types.InputRichMessage` describing it.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed as Markdown.
                Pass :obj:`~pyrogram.enums.ParseMode.HTML` to parse them as HTML instead;
                the two styles are exclusive and cannot be combined.
                Ignored when *rich_text* is an :obj:`~pyrogram.types.InputRichMessage`.

            media (List of :obj:`~pyrogram.types.InputRichMessageMedia`, *optional*):
                Media the text refers to through ``tg://photo?id=``, ``tg://video?id=``
                or ``tg://audio?id=`` links.
                Ignored when *rich_text* is an :obj:`~pyrogram.types.InputRichMessage`.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            disable_notification (``bool``, *optional*):
                Sends the message silently. Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for a message thread in a forum topic.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the direct messages topic.

            effect_id (``int``, *optional*):
                Unique identifier of the effect to apply to the message.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period in seconds for the message to be sent repeatedly.

            protect_content (``bool``, *optional*):
                Pass True to protect the message content from being forwarded.

            allow_paid_broadcast (``bool``, *optional*):
                Pay to skip the broadcast flood limit.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the message.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(message_id=self.id)

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_rich_message(
            chat_id=self.chat.id,
            rich_text=rich_text,
            parse_mode=parse_mode,
            media=media,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            show_caption_above_media=show_caption_above_media,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            protect_content=protect_content,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
        )

    async def answer_rich(
        self,
        rich_text: str | types.InputRichMessage,
        parse_mode: enums.ParseMode | None = None,
        media: list[types.InputRichMessageMedia] | None = None,
        disable_web_page_preview: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        show_caption_above_media: bool | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_rich_message` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Unlike :meth:`~pyrogram.types.Message.reply_rich`, this method does not reply to
        the message it is bound to.

        Example:
            .. code-block:: python

                await message.answer_rich("# Title\n\nSome **rich** text")

        Parameters:
            rich_text (``str`` | :obj:`~pyrogram.types.InputRichMessage`):
                Rich text (Markdown or HTML) to render a styled message, or a whole
                :obj:`~pyrogram.types.InputRichMessage` describing it.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed as Markdown.
                Pass :obj:`~pyrogram.enums.ParseMode.HTML` to parse them as HTML instead;
                the two styles are exclusive and cannot be combined.
                Ignored when *rich_text* is an :obj:`~pyrogram.types.InputRichMessage`.

            media (List of :obj:`~pyrogram.types.InputRichMessageMedia`, *optional*):
                Media the text refers to through ``tg://photo?id=``, ``tg://video?id=``
                or ``tg://audio?id=`` links.
                Ignored when *rich_text* is an :obj:`~pyrogram.types.InputRichMessage`.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            disable_notification (``bool``, *optional*):
                Sends the message silently. Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for a message thread in a forum topic.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the direct messages topic.

            effect_id (``int``, *optional*):
                Unique identifier of the effect to apply to the message.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period in seconds for the message to be sent repeatedly.

            protect_content (``bool``, *optional*):
                Pass True to protect the message content from being forwarded.

            allow_paid_broadcast (``bool``, *optional*):
                Pay to skip the broadcast flood limit.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the message.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_rich_message(
            chat_id=self.chat.id,
            rich_text=rich_text,
            parse_mode=parse_mode,
            media=media,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            show_caption_above_media=show_caption_above_media,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            protect_content=protect_content,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
        )

    async def reply(
        self,
        text: str,
        parse_mode: enums.ParseMode | None = None,
        entities: list[types.MessageEntity] | None = None,
        link_preview_options: types.LinkPreviewOptions | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        show_caption_above_media: bool | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        quote: bool | None = None,
        disable_web_page_preview: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_message` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            text (``str``):
                Text of the message to be sent.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in message text, which can be specified instead of *parse_mode*.

            link_preview_options (:obj:`~pyrogram.types.LinkPreviewOptions`, *optional*):
                Options used for link preview generation for the message.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_message(
            chat_id=self.chat.id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            link_preview_options=link_preview_options,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            show_caption_above_media=show_caption_above_media,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            protect_content=protect_content,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )

    reply_text = reply

    async def answer(
        self,
        text: str,
        parse_mode: enums.ParseMode | None = None,
        entities: list[types.MessageEntity] | None = None,
        link_preview_options: types.LinkPreviewOptions | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        show_caption_above_media: bool | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_message` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            text (``str``):
                Text of the message to be sent.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in message text, which can be specified instead of *parse_mode*.

            link_preview_options (:obj:`~pyrogram.types.LinkPreviewOptions`, *optional*):
                Options used for link preview generation for the message.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_message(
            chat_id=self.chat.id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            link_preview_options=link_preview_options,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            show_caption_above_media=show_caption_above_media,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            protect_content=protect_content,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
        )

    async def reply_photo(
        self,
        photo: str | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        show_caption_above_media: bool | None = None,
        ttl_seconds: int | None = None,
        view_once: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_photo` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            photo (``str``):
                Photo to send.
                Pass a file_id as string to send a photo that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a photo from the Internet, or
                pass a file path as string to upload a new photo that exists on your local machine.

            caption (``str``, *optional*):
                Photo caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the photo needs to be covered with a spoiler animation.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            ttl_seconds (``int``, *optional*):
                Self-Destruct Timer.
                If you set a timer, the photo will self-destruct in *ttl_seconds*
                seconds after it was viewed.

            view_once (``bool``, *optional*):
                Pass True if the photo must be opened once and disappear afterwards.
                Self-destructing media only works in private chats; a group or a
                channel drops the timer.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_photo(
            chat_id=self.chat.id,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            has_spoiler=has_spoiler,
            show_caption_above_media=show_caption_above_media,
            ttl_seconds=ttl_seconds,
            view_once=view_once,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            protect_content=protect_content,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )

    async def answer_photo(
        self,
        photo: str | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        show_caption_above_media: bool | None = None,
        ttl_seconds: int | None = None,
        view_once: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_photo` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            photo (``str``):
                Photo to send.
                Pass a file_id as string to send a photo that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a photo from the Internet, or
                pass a file path as string to upload a new photo that exists on your local machine.

            caption (``str``, *optional*):
                Photo caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the photo needs to be covered with a spoiler animation.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            ttl_seconds (``int``, *optional*):
                Self-Destruct Timer.
                If you set a timer, the photo will self-destruct in *ttl_seconds*
                seconds after it was viewed.

            view_once (``bool``, *optional*):
                Pass True if the photo must be opened once and disappear afterwards.
                Self-destructing media only works in private chats; a group or a
                channel drops the timer.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_photo(
            chat_id=self.chat.id,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            has_spoiler=has_spoiler,
            show_caption_above_media=show_caption_above_media,
            ttl_seconds=ttl_seconds,
            view_once=view_once,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            protect_content=protect_content,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_poll(
        self,
        question: types.FormattedText,
        options: list[str | types.InputPollOption],
        description: types.FormattedText | None = None,
        description_media: types.InputPollMedia | None = None,
        message_thread_id: int | None = None,
        business_connection_id: str | None = None,
        is_anonymous: bool = True,
        type: enums.PollType = enums.PollType.REGULAR,
        allows_multiple_answers: bool | None = None,
        allows_revoting: bool | None = None,
        members_only: bool | None = None,
        country_codes: list[str] | None = None,
        shuffle_options: bool | None = None,
        allow_adding_options: bool | None = None,
        hide_results_until_closes: bool | None = None,
        correct_option_ids: list[int] | None = None,
        explanation: types.FormattedText | None = None,
        explanation_media: types.InputPollMedia | None = None,
        open_period: int | None = None,
        close_date: datetime | None = None,
        is_closed: bool | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        paid_message_star_count: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_poll` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * business_connection_id
        * reply_parameters

        Example:
            .. code-block:: python

                await message.reply_poll("This is a poll", ["A", "B", "C"])

        Parameters:
            question (``str`` | :obj:`~pyrogram.types.FormattedText`):
                Poll question, 1-255 characters (up to 300 characters for bots).
                Only custom emoji entities are allowed to be added and only by Premium users.

            options (List of :obj:`~pyrogram.types.InputPollOption`):
                List of 1-12 answer options, each 1-100 characters.

            description (``str`` | :obj:`~pyrogram.types.FormattedText`, *optional*):
                Description of the poll to be sent, 0-1024 characters after entities parsing.

            description_media (:obj:`~pyrogram.types.InputPollMedia`, *optional*):
                Media attached to the poll.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For supergroups only.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

            is_anonymous (``bool``, *optional*):
                True, if the poll needs to be anonymous.
                Defaults to True.

            type (:obj`~pyrogram.enums.PollType`, *optional*):
                Poll type, :obj:`~pyrogram.enums.PollType.QUIZ` or :obj:`~pyrogram.enums.PollType.REGULAR`.
                Defaults to :obj:`~pyrogram.enums.PollType.REGULAR`.

            allows_multiple_answers (``bool``, *optional*):
                Pass True, if the poll allows multiple answers.
                Defaults to False.

            allows_revoting (``bool``, *optional*):
                Pass True, if the poll allows to change chosen answer options.
                Defaults to False for quizzes and to True for regular polls.

            members_only (``bool``, *optional*):
                Pass True, if voting is limited to users who have been members of the chat where the poll is being sent for more than 24 hours.
                For channel chats only.

            country_codes (List of ``str``, *optional*):
                The list of 0-12 two-letter ISO 3166-1 alpha-2 country codes indicating the countries from which users can vote in the poll.
                For channel chats only.
                If omitted or empty, then users from any country can participate in the poll.

            shuffle_options (``bool``, *optional*):
                Pass True, if the poll options must be shown in random order.

            allow_adding_options (``bool``, *optional*):
                Pass True, if answer options can be added to the poll after creation, not supported for anonymous polls and quizzes.

            hide_results_until_closes (``bool``, *optional*):
                Pass True, if poll results must be shown only after the poll closes.

            correct_option_ids (List of ``int``, *optional*):
                List of monotonically increasing 0-based identifiers of the correct answer options, required for polls in quiz mode.

            explanation (``str`` | :obj:`~pyrogram.types.FormattedText`, *optional*):
                Text that is shown when a user chooses an incorrect answer or taps on the lamp icon in a quiz-style poll, 0-200 characters with at most 2 line feeds after entities parsing.

            explanation_media (:obj:`~pyrogram.types.InputPollMedia`, *optional*):
                Media attached to the explanation.

            open_period (``int``, *optional*):
                Amount of time in seconds the poll will be active after creation, 5-2628000.
                Can't be used together with *close_date*.

            close_date (:py:obj:`~datetime.datetime`, *optional*):
                Point in time when the poll will be automatically closed.
                Must be at least 5 and no more than 2628000 seconds in the future.
                Can't be used together with *open_period*.

            is_closed (``bool``, *optional*):
                Pass True, if the poll needs to be immediately closed.
                This can be useful for poll preview.
                For bots only.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(message_id=self.id)

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        return await self._client.send_poll(
            chat_id=self.chat.id,
            question=question,
            options=options,
            description=description,
            description_media=description_media,
            message_thread_id=message_thread_id,
            business_connection_id=business_connection_id,
            is_anonymous=is_anonymous,
            type=type,
            allows_multiple_answers=allows_multiple_answers,
            allows_revoting=allows_revoting,
            members_only=members_only,
            country_codes=country_codes,
            shuffle_options=shuffle_options,
            allow_adding_options=allow_adding_options,
            hide_results_until_closes=hide_results_until_closes,
            correct_option_ids=correct_option_ids,
            explanation=explanation,
            explanation_media=explanation_media,
            open_period=open_period,
            close_date=close_date,
            is_closed=is_closed,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            paid_message_star_count=paid_message_star_count,
            reply_markup=reply_markup,
        )

    async def answer_poll(
        self,
        question: types.FormattedText,
        options: list[str | types.InputPollOption],
        description: types.FormattedText | None = None,
        description_media: types.InputPollMedia | None = None,
        message_thread_id: int | None = None,
        business_connection_id: str | None = None,
        is_anonymous: bool = True,
        type: enums.PollType = enums.PollType.REGULAR,
        allows_multiple_answers: bool | None = None,
        allows_revoting: bool | None = None,
        members_only: bool | None = None,
        country_codes: list[str] | None = None,
        shuffle_options: bool | None = None,
        allow_adding_options: bool | None = None,
        hide_results_until_closes: bool | None = None,
        correct_option_ids: list[int] | None = None,
        explanation: types.FormattedText | None = None,
        explanation_media: types.InputPollMedia | None = None,
        open_period: int | None = None,
        close_date: datetime | None = None,
        is_closed: bool | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        paid_message_star_count: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_poll` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * business_connection_id

        Example:
            .. code-block:: python

                await message.answer_poll("This is a poll", ["A", "B", "C"])

        Parameters:
            question (``str`` | :obj:`~pyrogram.types.FormattedText`):
                Poll question, 1-255 characters (up to 300 characters for bots).
                Only custom emoji entities are allowed to be added and only by Premium users.

            options (List of :obj:`~pyrogram.types.InputPollOption`):
                List of 1-12 answer options, each 1-100 characters.

            description (``str`` | :obj:`~pyrogram.types.FormattedText`, *optional*):
                Description of the poll to be sent, 0-1024 characters after entities parsing.

            description_media (:obj:`~pyrogram.types.InputPollMedia`, *optional*):
                Media attached to the poll.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For supergroups only.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

            is_anonymous (``bool``, *optional*):
                True, if the poll needs to be anonymous.
                Defaults to True.

            type (:obj`~pyrogram.enums.PollType`, *optional*):
                Poll type, :obj:`~pyrogram.enums.PollType.QUIZ` or :obj:`~pyrogram.enums.PollType.REGULAR`.
                Defaults to :obj:`~pyrogram.enums.PollType.REGULAR`.

            allows_multiple_answers (``bool``, *optional*):
                Pass True, if the poll allows multiple answers.
                Defaults to False.

            allows_revoting (``bool``, *optional*):
                Pass True, if the poll allows to change chosen answer options.
                Defaults to False for quizzes and to True for regular polls.

            members_only (``bool``, *optional*):
                Pass True, if voting is limited to users who have been members of the chat where the poll is being sent for more than 24 hours.
                For channel chats only.

            country_codes (List of ``str``, *optional*):
                The list of 0-12 two-letter ISO 3166-1 alpha-2 country codes indicating the countries from which users can vote in the poll.
                For channel chats only.
                If omitted or empty, then users from any country can participate in the poll.

            shuffle_options (``bool``, *optional*):
                Pass True, if the poll options must be shown in random order.

            allow_adding_options (``bool``, *optional*):
                Pass True, if answer options can be added to the poll after creation, not supported for anonymous polls and quizzes.

            hide_results_until_closes (``bool``, *optional*):
                Pass True, if poll results must be shown only after the poll closes.

            correct_option_ids (List of ``int``, *optional*):
                List of monotonically increasing 0-based identifiers of the correct answer options, required for polls in quiz mode.

            explanation (``str`` | :obj:`~pyrogram.types.FormattedText`, *optional*):
                Text that is shown when a user chooses an incorrect answer or taps on the lamp icon in a quiz-style poll, 0-200 characters with at most 2 line feeds after entities parsing.

            explanation_media (:obj:`~pyrogram.types.InputPollMedia`, *optional*):
                Media attached to the explanation.

            open_period (``int``, *optional*):
                Amount of time in seconds the poll will be active after creation, 5-2628000.
                Can't be used together with *close_date*.

            close_date (:py:obj:`~datetime.datetime`, *optional*):
                Point in time when the poll will be automatically closed.
                Must be at least 5 and no more than 2628000 seconds in the future.
                Can't be used together with *open_period*.

            is_closed (``bool``, *optional*):
                Pass True, if the poll needs to be immediately closed.
                This can be useful for poll preview.
                For bots only.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        return await self._client.send_poll(
            chat_id=self.chat.id,
            question=question,
            options=options,
            description=description,
            description_media=description_media,
            message_thread_id=message_thread_id,
            business_connection_id=business_connection_id,
            is_anonymous=is_anonymous,
            type=type,
            allows_multiple_answers=allows_multiple_answers,
            allows_revoting=allows_revoting,
            members_only=members_only,
            country_codes=country_codes,
            shuffle_options=shuffle_options,
            allow_adding_options=allow_adding_options,
            hide_results_until_closes=hide_results_until_closes,
            correct_option_ids=correct_option_ids,
            explanation=explanation,
            explanation_media=explanation_media,
            open_period=open_period,
            close_date=close_date,
            is_closed=is_closed,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            paid_message_star_count=paid_message_star_count,
            reply_markup=reply_markup,
        )

    async def reply_dice(
        self,
        emoji: str = "🎲",
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_dice` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            emoji (``str``, *optional*):
                Emoji on which the dice throw animation is based.
                Currently, must be one of "🎲", "🎯", "🏀", "⚽", "🎳", or "🎰".
                Dice can have values 1-6 for "🎲", "🎯" and "🎳", values 1-5 for "🏀" and "⚽", and
                values 1-64 for "🎰".
                Defaults to "🎲".

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For supergroups only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent dice message is returned.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(message_id=self.id)

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        return await self._client.send_dice(
            chat_id=self.chat.id,
            emoji=emoji,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            suggested_post_parameters=suggested_post_parameters,
            schedule_date=schedule_date,
            protect_content=protect_content,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            reply_markup=reply_markup,
        )

    async def answer_dice(
        self,
        emoji: str = "🎲",
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_dice` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            emoji (``str``, *optional*):
                Emoji on which the dice throw animation is based.
                Currently, must be one of "🎲", "🎯", "🏀", "⚽", "🎳", or "🎰".
                Dice can have values 1-6 for "🎲", "🎯" and "🎳", values 1-5 for "🏀" and "⚽", and
                values 1-64 for "🎰".
                Defaults to "🎲".

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For supergroups only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent dice message is returned.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        return await self._client.send_dice(
            chat_id=self.chat.id,
            emoji=emoji,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            suggested_post_parameters=suggested_post_parameters,
            schedule_date=schedule_date,
            protect_content=protect_content,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            reply_markup=reply_markup,
        )

    async def reply_sticker(
        self,
        sticker: str | BinaryIO,
        emoji: str | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_sticker` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            sticker (``str``):
                Sticker to send.
                Pass a file_id as string to send a sticker that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a .webp sticker file from the Internet, or
                pass a file path as string to upload a new sticker that exists on your local machine.


            caption (``str``, *optional*):
                Sticker caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            emoji (``str``, *optional*):
                Emoji the sticker stands for, shown while the sticker is being uploaded.

            caption (``str``, *optional*):
                Caption of the sticker, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_sticker(
            chat_id=self.chat.id,
            sticker=sticker,
            disable_notification=disable_notification,
            emoji=emoji,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )

    async def answer_sticker(
        self,
        sticker: str | BinaryIO,
        emoji: str | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_sticker` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            sticker (``str``):
                Sticker to send.
                Pass a file_id as string to send a sticker that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a .webp sticker file from the Internet, or
                pass a file path as string to upload a new sticker that exists on your local machine.


            caption (``str``, *optional*):
                Sticker caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            emoji (``str``, *optional*):
                Emoji the sticker stands for, shown while the sticker is being uploaded.

            caption (``str``, *optional*):
                Caption of the sticker, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_sticker(
            chat_id=self.chat.id,
            sticker=sticker,
            disable_notification=disable_notification,
            emoji=emoji,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_venue(
        self,
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        foursquare_id: str = "",
        foursquare_type: str = "",
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_venue` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            latitude (``float``):
                Latitude of the venue.

            longitude (``float``):
                Longitude of the venue.

            title (``str``):
                Name of the venue.

            address (``str``):
                Address of the venue.

            foursquare_id (``str``, *optional*):
                Foursquare identifier of the venue.

            foursquare_type (``str``, *optional*):
                Foursquare type of the venue, if known.
                (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or "food/icecream".)

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_venue(
            chat_id=self.chat.id,
            latitude=latitude,
            longitude=longitude,
            title=title,
            address=address,
            foursquare_id=foursquare_id,
            foursquare_type=foursquare_type,
            disable_notification=disable_notification,
            schedule_date=schedule_date,
            protect_content=protect_content,
            suggested_post_parameters=suggested_post_parameters,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )

    async def answer_venue(
        self,
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        foursquare_id: str = "",
        foursquare_type: str = "",
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_venue` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            latitude (``float``):
                Latitude of the venue.

            longitude (``float``):
                Longitude of the venue.

            title (``str``):
                Name of the venue.

            address (``str``):
                Address of the venue.

            foursquare_id (``str``, *optional*):
                Foursquare identifier of the venue.

            foursquare_type (``str``, *optional*):
                Foursquare type of the venue, if known.
                (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or "food/icecream".)

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_venue(
            chat_id=self.chat.id,
            latitude=latitude,
            longitude=longitude,
            title=title,
            address=address,
            foursquare_id=foursquare_id,
            foursquare_type=foursquare_type,
            disable_notification=disable_notification,
            schedule_date=schedule_date,
            protect_content=protect_content,
            suggested_post_parameters=suggested_post_parameters,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            reply_markup=reply_markup,
        )

    async def reply_video(
        self,
        video: str | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        show_caption_above_media: bool | None = None,
        ttl_seconds: int | None = None,
        duration: int = 0,
        width: int = 0,
        height: int = 0,
        video_start_timestamp: int | None = None,
        video_cover: str | BinaryIO | None = None,
        thumb: str | BinaryIO | None = None,
        file_name: str | None = None,
        supports_streaming: bool = True,
        view_once: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        no_sound: bool | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_video` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            video (``str``):
                Video to send.
                Pass a file_id as string to send a video that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a video from the Internet, or
                pass a file path as string to upload a new video that exists on your local machine.

            caption (``str``, *optional*):
                Video caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the video needs to be covered with a spoiler animation.

            show_caption_above_media (``bool``, *optional*):
                Pass True to show the video caption above the video.

            ttl_seconds (``int``, *optional*):
                Self-Destruct Timer.
                If you set a timer, the video will self-destruct in *ttl_seconds*
                seconds after it was viewed.

            duration (``int``, *optional*):
                Duration of sent video in seconds.

            width (``int``, *optional*):
                Video width.

            height (``int``, *optional*):
                Video height.

            video_start_timestamp (``int``, *optional*):
                Video startpoint, in seconds.

            video_cover (``str`` | ``BinaryIO``, *optional*):
                Video cover.
                Pass a file_id as string to attach a photo that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a photo from the Internet,
                pass a file path as string to upload a new photo that exists on your local machine, or
                pass a binary file-like object with its attribute ".name" set for in-memory uploads.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the video sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            file_name (``str``, *optional*):
                File name of the video sent.
                Defaults to file's path basename.

            supports_streaming (``bool``, *optional*):
                Pass True, if the uploaded video is suitable for streaming.

            view_once (``bool``, *optional*):
                Pass True if the video must be opened once and disappear afterwards.
                Self-destructing media only works in private chats; a group or a
                channel drops the timer.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            no_sound (``bool``, *optional*):
                Pass True, if the uploaded video is a video message with no sound.
                Doesn't work for external links.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If ``False``, the message will be sent without reply.
                If unspecified, the message will be sent as a reply only if the replied message is in a private chat.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            quote_text (``str``, *optional*):
                Text of the quote to be sent.

            quote_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                Special entities like usernames, URLs, bot commands, etc. that appear in the quote text.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Example:
            .. code-block:: python

                await message.reply_video("video.mp4", caption="video caption")

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_video(
            chat_id=self.chat.id,
            video=video,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            has_spoiler=has_spoiler,
            show_caption_above_media=show_caption_above_media,
            ttl_seconds=ttl_seconds,
            view_once=view_once,
            duration=duration,
            width=width,
            height=height,
            video_start_timestamp=video_start_timestamp,
            video_cover=video_cover,
            thumb=thumb,
            supports_streaming=supports_streaming,
            disable_notification=disable_notification,
            file_name=file_name,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            no_sound=no_sound,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )

    async def answer_video(
        self,
        video: str | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        show_caption_above_media: bool | None = None,
        ttl_seconds: int | None = None,
        duration: int = 0,
        width: int = 0,
        height: int = 0,
        video_start_timestamp: int | None = None,
        video_cover: str | BinaryIO | None = None,
        thumb: str | BinaryIO | None = None,
        file_name: str | None = None,
        supports_streaming: bool = True,
        view_once: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        no_sound: bool | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_video` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            video (``str``):
                Video to send.
                Pass a file_id as string to send a video that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a video from the Internet, or
                pass a file path as string to upload a new video that exists on your local machine.

            caption (``str``, *optional*):
                Video caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the video needs to be covered with a spoiler animation.

            show_caption_above_media (``bool``, *optional*):
                Pass True to show the video caption above the video.

            ttl_seconds (``int``, *optional*):
                Self-Destruct Timer.
                If you set a timer, the video will self-destruct in *ttl_seconds*
                seconds after it was viewed.


            duration (``int``, *optional*):
                Duration of sent video in seconds.

            width (``int``, *optional*):
                Video width.

            height (``int``, *optional*):
                Video height.

            video_start_timestamp (``int``, *optional*):
                Video startpoint, in seconds.

            video_cover (``str`` | ``BinaryIO``, *optional*):
                Video cover.
                Pass a file_id as string to attach a photo that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a photo from the Internet,
                pass a file path as string to upload a new photo that exists on your local machine, or
                pass a binary file-like object with its attribute ".name" set for in-memory uploads.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the video sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            file_name (``str``, *optional*):
                File name of the video sent.
                Defaults to file's path basename.

            supports_streaming (``bool``, *optional*):
                Pass True, if the uploaded video is suitable for streaming.

            view_once (``bool``, *optional*):
                Pass True if the video must be opened once and disappear afterwards.
                Self-destructing media only works in private chats; a group or a
                channel drops the timer.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            no_sound (``bool``, *optional*):
                Pass True, if the uploaded video is a video message with no sound.
                Doesn't work for external links.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Example:
            .. code-block:: python

                await message.answer_video("video.mp4", caption="video caption")

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_video(
            chat_id=self.chat.id,
            video=video,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            has_spoiler=has_spoiler,
            show_caption_above_media=show_caption_above_media,
            ttl_seconds=ttl_seconds,
            view_once=view_once,
            duration=duration,
            width=width,
            height=height,
            video_start_timestamp=video_start_timestamp,
            video_cover=video_cover,
            thumb=thumb,
            supports_streaming=supports_streaming,
            disable_notification=disable_notification,
            file_name=file_name,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            no_sound=no_sound,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_video_note(
        self,
        video_note: str | BinaryIO,
        duration: int = 0,
        length: int = 1,
        thumb: str | BinaryIO | None = None,
        view_once: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        parse_mode: enums.ParseMode | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_video_note` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            video_note (``str``):
                Video note to send.
                Pass a file_id as string to send a video note that exists on the Telegram servers, or
                pass a file path as string to upload a new video note that exists on your local machine.
                Sending video notes by a URL is currently unsupported.

            duration (``int``, *optional*):
                Duration of sent video in seconds.

            length (``int``, *optional*):
                Video width and height.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the video sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            view_once (``bool``, *optional*):
                Pass True if the video note must be opened once and disappear afterwards.
                Self-destructing media only works in private chats; a group or a
                channel drops the timer.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.


            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_video_note(
            chat_id=self.chat.id,
            video_note=video_note,
            duration=duration,
            length=length,
            thumb=thumb,
            disable_notification=disable_notification,
            view_once=view_once,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            protect_content=protect_content,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )

    async def answer_video_note(
        self,
        video_note: str | BinaryIO,
        duration: int = 0,
        length: int = 1,
        thumb: str | BinaryIO | None = None,
        view_once: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_video_note` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            video_note (``str``):
                Video note to send.
                Pass a file_id as string to send a video note that exists on the Telegram servers, or
                pass a file path as string to upload a new video note that exists on your local machine.
                Sending video notes by a URL is currently unsupported.

            duration (``int``, *optional*):
                Duration of sent video in seconds.

            length (``int``, *optional*):
                Video width and height.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the video sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            view_once (``bool``, *optional*):
                Pass True if the video note must be opened once and disappear afterwards.
                Self-destructing media only works in private chats; a group or a
                channel drops the timer.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.


            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_video_note(
            chat_id=self.chat.id,
            video_note=video_note,
            duration=duration,
            length=length,
            thumb=thumb,
            disable_notification=disable_notification,
            view_once=view_once,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            protect_content=protect_content,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_voice(
        self,
        voice: str | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        duration: int = 0,
        waveform: bytes | None = None,
        view_once: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_voice` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            voice (``str``):
                Audio file to send.
                Pass a file_id as string to send an audio that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get an audio from the Internet, or
                pass a file path as string to upload a new audio that exists on your local machine.

            caption (``str``, *optional*):
                Voice message caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            duration (``int``, *optional*):
                Duration of the voice message in seconds.

            waveform (``bytes``, *optional*):
                The waveform of the voice note, as a 5-bit byte string.

            view_once (``bool``, *optional*):
                Pass True if the voice note must be opened once and disappear afterwards.
                Self-destructing media only works in private chats; a group or a
                channel drops the timer.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.


            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_voice(
            chat_id=self.chat.id,
            voice=voice,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            duration=duration,
            disable_notification=disable_notification,
            waveform=waveform,
            view_once=view_once,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )

    async def answer_voice(
        self,
        voice: str | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        duration: int = 0,
        waveform: bytes | None = None,
        view_once: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_voice` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            voice (``str``):
                Audio file to send.
                Pass a file_id as string to send an audio that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get an audio from the Internet, or
                pass a file path as string to upload a new audio that exists on your local machine.

            caption (``str``, *optional*):
                Voice message caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            duration (``int``, *optional*):
                Duration of the voice message in seconds.

            waveform (``bytes``, *optional*):
                The waveform of the voice note, as a 5-bit byte string.

            view_once (``bool``, *optional*):
                Pass True if the voice note must be opened once and disappear afterwards.
                Self-destructing media only works in private chats; a group or a
                channel drops the timer.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.


            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.
            In case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned
            instead.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_voice(
            chat_id=self.chat.id,
            voice=voice,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            duration=duration,
            disable_notification=disable_notification,
            waveform=waveform,
            view_once=view_once,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            progress=progress,
            progress_args=progress_args,
        )

    async def reply_paid_media(
        self,
        stars_amount: int,
        media: list[types.InputMediaPhoto | types.InputMediaVideo],
        caption: str = "",
        payload: str | None = None,
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        disable_notification: bool | None = None,
        direct_messages_topic_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        show_caption_above_media: bool | None = None,
    ) -> list[types.Message]:
        """Shortcut for method :obj:`~pyrogram.Client.send_paid_media` will automatically fill method attributes:

        * chat_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            stars_amount (``int``):
                The number of Telegram Stars that must be paid to buy access to the media.

            media (List of :obj:`~pyrogram.types.InputMediaPhoto`, :obj:`~pyrogram.types.InputMediaVideo`):
                A list describing photos and videos to be sent, must include 1–10 items.

            caption (``str``, *optional*):
                Media caption, 0-1024 characters after entities parsing.

            payload (``str``):
                Bot-defined payload, 1-128 bytes. This will not be displayed to the user, use for your internal processes.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

        Returns:
            List of :obj:`~pyrogram.types.Message`: On success, a list of messages is returned.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(message_id=self.id)

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_paid_media(
            chat_id=self.chat.id,
            stars_amount=stars_amount,
            media=media,
            caption=caption,
            payload=payload,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            direct_messages_topic_id=direct_messages_topic_id,
            reply_parameters=reply_parameters,
            suggested_post_parameters=suggested_post_parameters,
            schedule_date=schedule_date,
            protect_content=protect_content,
            show_caption_above_media=show_caption_above_media,
            business_connection_id=self.business_connection_id,
        )

    async def answer_paid_media(
        self,
        stars_amount: int,
        media: list[types.InputMediaPhoto | types.InputMediaVideo],
        caption: str = "",
        payload: str | None = None,
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        disable_notification: bool | None = None,
        direct_messages_topic_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        show_caption_above_media: bool | None = None,
    ) -> list[types.Message]:
        """Shortcut for method :obj:`~pyrogram.Client.send_paid_media` will automatically fill method attributes:

        * chat_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            stars_amount (``int``):
                The number of Telegram Stars that must be paid to buy access to the media.

            media (List of :obj:`~pyrogram.types.InputMediaPhoto`, :obj:`~pyrogram.types.InputMediaVideo`):
                A list describing photos and videos to be sent, must include 1–10 items.

            caption (``str``, *optional*):
                Media caption, 0-1024 characters after entities parsing.

            payload (``str``):
                Bot-defined payload, 1-128 bytes. This will not be displayed to the user, use for your internal processes.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

        Returns:
            List of :obj:`~pyrogram.types.Message`: On success, a list of messages is returned.
        """
        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_paid_media(
            chat_id=self.chat.id,
            stars_amount=stars_amount,
            media=media,
            caption=caption,
            payload=payload,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            direct_messages_topic_id=direct_messages_topic_id,
            reply_parameters=reply_parameters,
            suggested_post_parameters=suggested_post_parameters,
            schedule_date=schedule_date,
            protect_content=protect_content,
            show_caption_above_media=show_caption_above_media,
            business_connection_id=self.business_connection_id,
        )

    async def reply_cached_media(
        self,
        file_id: str,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        show_caption_above_media: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_cached_media` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id
        * reply_parameters

        Parameters:
            file_id (``str``):
                Media to send.
                Pass a file_id as string to send a media that exists on the Telegram servers.

            caption (``bool``, *optional*):
                Media caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the message needs to be covered with a spoiler animation.

            show_caption_above_media (``bool``, *optional*):
                Pass True to show the caption above the media.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the effect to apply to the message.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_cached_media(
            chat_id=self.chat.id,
            file_id=file_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            has_spoiler=has_spoiler,
            show_caption_above_media=show_caption_above_media,
            effect_id=effect_id,
            schedule_date=schedule_date,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            reply_parameters=reply_parameters,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )

    async def answer_cached_media(
        self,
        file_id: str,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        show_caption_above_media: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_cached_media` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * direct_messages_topic_id
        * business_connection_id

        Parameters:
            file_id (``str``):
                Media to send.
                Pass a file_id as string to send a media that exists on the Telegram servers.

            caption (``bool``, *optional*):
                Media caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the message needs to be covered with a spoiler animation.

            show_caption_above_media (``bool``, *optional*):
                Pass True to show the caption above the media.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            effect_id (``int``, *optional*):
                Unique identifier of the effect to apply to the message.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_cached_media(
            chat_id=self.chat.id,
            file_id=file_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            has_spoiler=has_spoiler,
            show_caption_above_media=show_caption_above_media,
            effect_id=effect_id,
            schedule_date=schedule_date,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            reply_parameters=reply_parameters,
            business_connection_id=self.business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            suggested_post_parameters=suggested_post_parameters,
            reply_markup=reply_markup,
        )

    async def get_media_group(self) -> list[types.Message]:
        """Shortcut for method :obj:`~pyrogram.Client.get_media_group` will automatically fill method attributes:

        * chat_id
        * message_id

        Returns:
            List of :obj:`~pyrogram.types.Message`: On success, a list of messages of the media group is returned.

        Raises:
            ValueError: In case the passed message id doesn't belong to a media group.
        """
        return await self._client.get_media_group(chat_id=self.chat.id, message_id=self.id)

    async def reply_chat_action(self, action: enums.ChatAction) -> bool:
        """Shortcut for method :obj:`~pyrogram.Client.send_chat_action` will automatically fill method attributes:

        * chat_id
        * business_connection_id

        Parameters:
            action (:obj:`~pyrogram.enums.ChatAction`):
                Type of action to broadcast.

        Returns:
            ``bool``: On success, True is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
            ValueError: In case the provided string is not a valid chat action.
        """
        return await self._client.send_chat_action(
            chat_id=self.chat.id, action=action, business_connection_id=self.business_connection_id
        )

    async def reply_inline_bot_result(
        self,
        query_id: int,
        result_id: str,
        disable_notification: bool | None = None,
        message_thread_id: bool | None = None,
        direct_messages_topic_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        paid_message_star_count: int | None = None,
        quote: bool | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        parse_mode: enums.ParseMode | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_inline_bot_result` will automatically fill method attributes:

        * chat_id
        * direct_messages_topic_id
        * message_thread_id
        * reply_parameters

        Parameters:
            query_id (``int``):
                Unique identifier for the answered query.

            result_id (``str``):
                Unique identifier for the result that was chosen.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id if reply_to_message_id is not None else self.id,
                quote=quote_text,
                quote_entities=quote_entities,
            )

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_inline_bot_result(
            chat_id=self.chat.id,
            query_id=query_id,
            result_id=result_id,
            disable_notification=disable_notification,
            schedule_date=schedule_date,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            reply_parameters=reply_parameters,
            paid_message_star_count=paid_message_star_count,
            reply_to_message_id=reply_to_message_id,
        )

    async def answer_inline_bot_result(
        self,
        query_id: int,
        result_id: str,
        disable_notification: bool | None = None,
        message_thread_id: bool | None = None,
        direct_messages_topic_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        paid_message_star_count: int | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_inline_bot_result` will automatically fill method attributes:

        * chat_id
        * direct_messages_topic_id
        * message_thread_id

        Parameters:
            query_id (``int``):
                Unique identifier for the answered query.

            result_id (``str``):
                Unique identifier for the result that was chosen.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        if direct_messages_topic_id is None:
            direct_messages_topic_id = self.direct_messages_topic_id

        return await self._client.send_inline_bot_result(
            chat_id=self.chat.id,
            query_id=query_id,
            result_id=result_id,
            disable_notification=disable_notification,
            schedule_date=schedule_date,
            message_thread_id=message_thread_id,
            direct_messages_topic_id=direct_messages_topic_id,
            reply_parameters=reply_parameters,
            paid_message_star_count=paid_message_star_count,
        )

    async def reply_checklist(
        self,
        checklist: types.InputChecklist,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        message_thread_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        paid_message_star_count: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        quote: bool | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_checklist` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * business_connection_id
        * reply_parameters

        Example:
            .. code-block:: python

                await message.reply_checklist("To do", [
                    types.InputChecklistTask(id=1, text="Task 1"),
                    types.InputChecklistTask(id=2, text="Task 2")
                ])

        Parameters:
            checklist (:obj:`~pyrogram.types.InputChecklist`):
                Checklist to send.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For supergroups only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if reply_parameters is None:
            reply_parameters = types.ReplyParameters(message_id=self.id)

        if quote is not None:
            log.warning("`quote` parameter is deprecated and will be removed in future updates.")

            if not quote:
                reply_parameters = None

        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        return await self._client.send_checklist(
            chat_id=self.chat.id,
            checklist=checklist,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            business_connection_id=self.business_connection_id,
            paid_message_star_count=paid_message_star_count,
            reply_markup=reply_markup,
        )

    async def answer_checklist(
        self,
        checklist: types.InputChecklist,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        message_thread_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        paid_message_star_count: int | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.send_checklist` will automatically fill method attributes:

        * chat_id
        * message_thread_id
        * business_connection_id

        Example:
            .. code-block:: python

                await message.reply_checklist("To do", [
                    types.InputChecklistTask(id=1, text="Task 1"),
                    types.InputChecklistTask(id=2, text="Task 2")
                ])

        Parameters:
            checklist (:obj:`~pyrogram.types.InputChecklist`):
                Checklist to send.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For supergroups only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if message_thread_id is None:
            message_thread_id = self.message_thread_id

        return await self._client.send_checklist(
            chat_id=self.chat.id,
            checklist=checklist,
            disable_notification=disable_notification,
            protect_content=protect_content,
            message_thread_id=message_thread_id,
            effect_id=effect_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            repeat_period=repeat_period,
            business_connection_id=self.business_connection_id,
            paid_message_star_count=paid_message_star_count,
            reply_markup=reply_markup,
        )

    @property
    def is_ephemeral(self) -> bool:
        """True, if this is an ephemeral message.

        An ephemeral message is not in the chat's history and is edited and deleted
        through its own methods, which name the receiver again because the message only
        ever existed for them.
        """

        return self.ephemeral_message_id is not None

    def _ephemeral_target(self) -> int:
        if not self.is_ephemeral:
            raise ValueError(
                "this is not an ephemeral message; use the ordinary edit and delete methods for it"
            )

        if self.receiver_user is None:
            raise ValueError(
                "the ephemeral message carries no receiver, so there is nobody to "
                "address the edit to"
            )

        return self.receiver_user.id

    async def edit_ephemeral_text(
        self,
        text: str | None = None,
        parse_mode: enums.ParseMode | None = None,
        entities: list[types.MessageEntity] | None = None,
        rich_text: str | types.InputRichMessage | None = None,
        rich_text_parse_mode: enums.ParseMode = enums.ParseMode.MARKDOWN,
        rich_text_media: list[types.InputRichMessageMedia] | None = None,
        rich_message: types.InputRichMessage | None = None,
        reply_markup: types.InlineKeyboardMarkup | None = None,
        welcome: bool | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.edit_ephemeral_message_text` will automatically fill method attributes:

        * chat_id
        * receiver_id
        * message_id

        Example:
            .. code-block:: python

                await message.edit_ephemeral_text("hello")

        Parameters:
            text (``str``, *optional*):
                New text of the message. Required if *rich_text* is not given.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in message text, which can be specified instead of *parse_mode*.

            rich_text (``str`` | :obj:`~pyrogram.types.InputRichMessage`, *optional*):
                Rich content to send, as Markdown or HTML text or as a whole
                :obj:`~pyrogram.types.InputRichMessage`.

            rich_text_parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                Parse mode for *rich_text*. Defaults to Markdown.
                Ignored when *rich_text* is an :obj:`~pyrogram.types.InputRichMessage`.

            rich_text_media (List of :obj:`~pyrogram.types.InputRichMessageMedia`, *optional*):
                Media *rich_text* refers to through ``tg://photo?id=``, ``tg://video?id=``
                or ``tg://audio?id=`` links.
                Ignored when *rich_text* is an :obj:`~pyrogram.types.InputRichMessage`.

            rich_message (:obj:`~pyrogram.types.InputRichMessage`, *optional*):
                Deprecated alias of *rich_text*.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

            welcome (``bool``, *optional*):
                Pass True when editing a stored welcome message rather than one that was delivered once.

        Returns:
            On success, the edited :obj:`~pyrogram.types.Message` is returned.

        Raises:
            ValueError: In case the message is not an ephemeral one.
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.edit_ephemeral_message_text(
            chat_id=self.chat.id,
            receiver_id=self._ephemeral_target(),
            message_id=self.ephemeral_message_id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            rich_text=rich_text,
            rich_text_parse_mode=rich_text_parse_mode,
            rich_text_media=rich_text_media,
            rich_message=rich_message,
            reply_markup=reply_markup,
            welcome=welcome,
        )

    edit_ephemeral = edit_ephemeral_text

    async def edit_ephemeral_caption(
        self,
        caption: str,
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        show_caption_above_media: bool | None = None,
        reply_markup: types.InlineKeyboardMarkup | None = None,
        welcome: bool | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.edit_ephemeral_message_caption` will automatically fill method attributes:

        * chat_id
        * receiver_id
        * message_id

        Example:
            .. code-block:: python

                await message.edit_ephemeral_caption("new caption")

        Parameters:
            caption (``str``):
                New caption of the message.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            show_caption_above_media (``bool``, *optional*):
                Pass True if the caption must be shown above the message media.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

            welcome (``bool``, *optional*):
                Pass True when editing a stored welcome message rather than one that was delivered once.

        Returns:
            On success, the edited :obj:`~pyrogram.types.Message` is returned.

        Raises:
            ValueError: In case the message is not an ephemeral one.
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.edit_ephemeral_message_caption(
            chat_id=self.chat.id,
            receiver_id=self._ephemeral_target(),
            message_id=self.ephemeral_message_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            show_caption_above_media=show_caption_above_media,
            reply_markup=reply_markup,
            welcome=welcome,
        )

    async def edit_ephemeral_media(
        self,
        media: types.InputMedia,
        reply_markup: types.InlineKeyboardMarkup | None = None,
        welcome: bool | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.edit_ephemeral_message_media` will automatically fill method attributes:

        * chat_id
        * receiver_id
        * message_id

        Example:
            .. code-block:: python

                from pyrogram.types import InputMediaPhoto

                await message.edit_ephemeral_media(InputMediaPhoto("new.jpg"))

        Parameters:
            media (:obj:`~pyrogram.types.InputMedia`):
                The new media. A local file is uploaded first.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

            welcome (``bool``, *optional*):
                Pass True when editing a stored welcome message rather than one that was delivered once.

        Returns:
            On success, the edited :obj:`~pyrogram.types.Message` is returned.

        Raises:
            ValueError: In case the message is not an ephemeral one.
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.edit_ephemeral_message_media(
            chat_id=self.chat.id,
            receiver_id=self._ephemeral_target(),
            message_id=self.ephemeral_message_id,
            media=media,
            reply_markup=reply_markup,
            welcome=welcome,
        )

    async def edit_ephemeral_reply_markup(
        self,
        reply_markup: types.InlineKeyboardMarkup | None = None,
        welcome: bool | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.edit_ephemeral_message_reply_markup` will automatically fill method attributes:

        * chat_id
        * receiver_id
        * message_id

        Example:
            .. code-block:: python

                from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

                await message.edit_ephemeral_reply_markup(
                    InlineKeyboardMarkup([[InlineKeyboardButton("Done", "done")]])
                )

        Parameters:
            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object. Pass nothing to remove the current one.

            welcome (``bool``, *optional*):
                Pass True when editing a stored welcome message rather than one that was delivered once.

        Returns:
            On success, the edited :obj:`~pyrogram.types.Message` is returned.

        Raises:
            ValueError: In case the message is not an ephemeral one.
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.edit_ephemeral_message_reply_markup(
            chat_id=self.chat.id,
            receiver_id=self._ephemeral_target(),
            message_id=self.ephemeral_message_id,
            reply_markup=reply_markup,
            welcome=welcome,
        )

    async def delete_ephemeral(self) -> bool:
        """Shortcut for method :obj:`~pyrogram.Client.delete_ephemeral_message` will automatically fill method attributes:

        * chat_id
        * receiver_id
        * message_id

        Example:
            .. code-block:: python

                await message.delete_ephemeral()

        Returns:
            ``bool``: True on success.

        Raises:
            ValueError: In case the message is not an ephemeral one.
            RPCError: In case of a Telegram RPC error.
        """
        return bool(
            await self._client.delete_ephemeral_message(
                chat_id=self.chat.id,
                receiver_id=self._ephemeral_target(),
                message_id=self.ephemeral_message_id,
            )
        )

    async def reply_ephemeral_text(
        self,
        text: str,
        receiver_id: int | str | None = None,
        parse_mode: enums.ParseMode | None = None,
        entities: list[types.MessageEntity] | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = None,
        query_id: int | None = None,
        rich_text: str | types.InputRichMessage | None = None,
        rich_text_parse_mode: enums.ParseMode = enums.ParseMode.MARKDOWN,
        rich_text_media: list[types.InputRichMessageMedia] | None = None,
        welcome: bool | None = None,
        anchor: bool | None = None,
        show_caption_above_media: bool | None = None,
        protect_content: bool | None = None,
    ) -> Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.send_ephemeral_message` will automatically fill method attributes:

        * chat_id
        * receiver_id
        * reply_parameters

        The reply goes to whoever sent this message unless *receiver_id* names someone
        else, and it is visible only to them.

        Example:
            .. code-block:: python

                await message.reply_ephemeral_text("Only you can see this")

        Parameters:
            text (``str``):
                Text of the message to be sent.

            receiver_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the user who will receive the
                message. Defaults to the sender of this message.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in message text, which can be specified instead of *parse_mode*.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options.

            query_id (``int``, *optional*):
                Identifier of the guest query to respond to, if this message is a reply to a guest bot query.

            rich_text (``str`` | :obj:`~pyrogram.types.InputRichMessage`, *optional*):
                Rich text (Markdown or HTML) to render a styled message. Overrides *text*.

            rich_text_parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                Parse mode for *rich_text*. Defaults to Markdown.

            rich_text_media (List of :obj:`~pyrogram.types.InputRichMessageMedia`, *optional*):
                Media *rich_text* refers to through ``tg://photo?id=``, ``tg://video?id=`` or ``tg://audio?id=`` links.

            welcome (``bool``, *optional*):
                Pass True to store the message as a welcome message for the chat rather than deliver it once.

            anchor (``bool``, *optional*):
                Pass True to anchor the message to the message it replies to.

            show_caption_above_media (``bool``, *optional*):
                Pass True if the caption must be shown above the message media.

            protect_content (``bool``, *optional*):
                Pass True to protect the content of the message from forwarding and saving.

        Returns:
            On success, the sent :obj:`~pyrogram.types.Message` is returned.

        Raises:
            ValueError: In case there is nobody to address the message to.
            RPCError: In case of a Telegram RPC error.
        """
        if receiver_id is None:
            if self.from_user is None:
                raise ValueError(
                    "the message has no sender, so there is nobody to address the "
                    "ephemeral reply to; pass receiver_id"
                )

            receiver_id = self.from_user.id

        return await self._client.send_ephemeral_message(
            chat_id=self.chat.id,
            receiver_id=receiver_id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            reply_parameters=types.ReplyParameters(message_id=self.id),
            reply_markup=reply_markup,
            query_id=query_id,
            rich_text=rich_text,
            rich_text_parse_mode=rich_text_parse_mode,
            rich_text_media=rich_text_media,
            welcome=welcome,
            anchor=anchor,
            show_caption_above_media=show_caption_above_media,
            protect_content=protect_content,
        )

    reply_ephemeral = reply_ephemeral_text

    async def edit_text(
        self,
        text: str | None = None,
        parse_mode: enums.ParseMode | None = None,
        entities: list[types.MessageEntity] | None = None,
        link_preview_options: types.LinkPreviewOptions | None = None,
        rich_text: str | types.InputRichMessage | None = None,
        rich_text_parse_mode: enums.ParseMode = enums.ParseMode.MARKDOWN,
        rich_text_media: list[types.InputRichMessageMedia] | None = None,
        reply_markup: types.InlineKeyboardMarkup | None = None,
        show_caption_above_media: bool | None = None,
        disable_web_page_preview: bool | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.edit_message_text` will automatically fill method attributes:

        * chat_id
        * message_id
        * business_connection_id

        Example:
            .. code-block:: python

                await message.edit_text("hello")

        Parameters:
            text (``str``):
                New text of the message.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in message text, which can be specified instead of *parse_mode*.

            link_preview_options (:obj:`~pyrogram.types.LinkPreviewOptions`, *optional*):
                Options used for link preview generation for the message.

            rich_text (``str`` | :obj:`~pyrogram.types.InputRichMessage`, *optional*):
                Rich content to send, as Markdown or HTML text or as a whole
                :obj:`~pyrogram.types.InputRichMessage`.

            rich_text_parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                Parse mode for *rich_text*. Defaults to Markdown.
                Ignored when *rich_text* is an :obj:`~pyrogram.types.InputRichMessage`.

            rich_text_media (List of :obj:`~pyrogram.types.InputRichMessageMedia`, *optional*):
                Media *rich_text* refers to through ``tg://photo?id=``, ``tg://video?id=``
                or ``tg://audio?id=`` links.
                Ignored when *rich_text* is an :obj:`~pyrogram.types.InputRichMessage`.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            On success, the edited :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.edit_message_text(
            chat_id=self.chat.id,
            message_id=self.id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            link_preview_options=link_preview_options,
            business_connection_id=self.business_connection_id,
            rich_text=rich_text,
            rich_text_parse_mode=rich_text_parse_mode,
            rich_text_media=rich_text_media,
            reply_markup=reply_markup,
            show_caption_above_media=show_caption_above_media,
            disable_web_page_preview=disable_web_page_preview,
        )

    edit = edit_text

    async def edit_caption(
        self,
        caption: str,
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        reply_markup: types.InlineKeyboardMarkup | None = None,
        show_caption_above_media: bool | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.edit_message_caption` will automatically fill method attributes:

        * chat_id
        * message_id
        * business_connection_id

        Parameters:
            caption (``str``):
                New caption of the message.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.
                Supported only for animation, photo and video messages.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            On success, the edited :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.edit_message_caption(
            chat_id=self.chat.id,
            message_id=self.id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            business_connection_id=self.business_connection_id,
            show_caption_above_media=show_caption_above_media,
            reply_markup=reply_markup,
        )

    async def edit_media(
        self, media: types.InputMedia, reply_markup: types.InlineKeyboardMarkup | None = None
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.edit_message_media` will automatically fill method attributes:

        * chat_id
        * message_id
        * business_connection_id

        Example:
            .. code-block:: python

                await message.edit_media(media)

        Parameters:
            media (:obj:`~pyrogram.types.InputMedia`):
                One of the InputMedia objects describing an animation, audio, document, photo or video.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            On success, the edited :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.edit_message_media(
            chat_id=self.chat.id,
            message_id=self.id,
            media=media,
            business_connection_id=self.business_connection_id,
            reply_markup=reply_markup,
        )

    async def edit_checklist(
        self,
        checklist: types.InputChecklist,
        reply_markup: types.InlineKeyboardMarkup | None = None,
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.edit_message_checklist` will automatically fill method attributes:

        * chat_id
        * message_id
        * business_connection_id

        Parameters:
            checklist (:obj:`~pyrogram.types.InputChecklist`):
                New checklist.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            On success, the edited :obj:`~pyrogram.types.Message` is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.edit_message_checklist(
            chat_id=self.chat.id,
            message_id=self.id,
            checklist=checklist,
            business_connection_id=self.business_connection_id,
            reply_markup=reply_markup,
        )

    async def edit_reply_markup(
        self, reply_markup: types.InlineKeyboardMarkup | None = None
    ) -> Message:
        """Shortcut for method :obj:`~pyrogram.Client.edit_message_reply_markup` will automatically fill method attributes:

        * chat_id
        * message_id

        Parameters:
            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`):
                An InlineKeyboardMarkup object.

        Returns:
            On success, if edited message is sent by the bot, the edited
            :obj:`~pyrogram.types.Message` is returned, otherwise True is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.edit_message_reply_markup(
            chat_id=self.chat.id, message_id=self.id, reply_markup=reply_markup
        )

    async def edit_live_location(
        self,
        latitude: float,
        longitude: float,
        horizontal_accuracy: float | None = None,
        live_period: int | None = None,
        heading: int | None = None,
        proximity_alert_radius: int | None = None,
    ) -> Message:
        """Use this method to edit live location messages.

        Parameters:
            latitude (``float``):
                Latitude of the location.

            longitude (``float``):
                Longitude of the location.

            horizontal_accuracy (``float``, *optional*):
                The radius of uncertainty for the location, measured in meters, 0-1500.

            live_period (``int``, *optional*):
                New period in seconds during which the location can be updated, starting from the message send date.
                If 0x7FFFFFFF is specified, then the location can be updated forever.
                Otherwise, the new value must not exceed the current ``live_period`` by more than a day,
                and the live location expiration date must remain within the next 90 days.
                If not specified, then ``live_period`` remains unchanged.

            heading (``int``, *optional*):
                For live locations, a direction in which the user is moving, in degrees.
                Must be between 1 and 360 if specified.

            proximity_alert_radius (``int``, *optional*):
                For live locations, a maximum distance for proximity alerts about approaching another chat member, in meters.
                Must be between 1 and 100000 if specified.
                Can't be enabled in channels and Saved Messages.

        Returns:
            On success, the edited :obj:`~pyrogram.types.Message` is returned.
        """
        r = await self._client.invoke(
            raw.functions.messages.EditMessage(
                peer=await self._client.resolve_peer(self.chat.id),
                id=self.id,
                media=raw.types.InputMediaGeoLive(
                    geo_point=raw.types.InputGeoPoint(
                        lat=latitude, long=longitude, accuracy_radius=horizontal_accuracy
                    ),
                    heading=heading,
                    period=live_period,
                    proximity_notification_radius=proximity_alert_radius,
                ),
            )
        )

        return next(iter(await utils.parse_messages(client=self._client, messages=r)), None)

    async def stop_live_location(self) -> Message:
        """Use this method to stop updating a live location message before live_period expires.

        Returns:
            On success, the edited :obj:`~pyrogram.types.Message` is returned.
        """
        r = await self._client.invoke(
            raw.functions.messages.EditMessage(
                peer=await self._client.resolve_peer(self.chat.id),
                id=self.id,
                media=raw.types.InputMediaGeoLive(
                    geo_point=raw.types.InputGeoPointEmpty(), stopped=True
                ),
            )
        )

        return next(iter(await utils.parse_messages(client=self._client, messages=r)), None)

    async def forward(
        self,
        chat_id: int | str,
        message_thread_id: int | None = None,
        disable_notification: bool | None = None,
        hide_sender_name: bool | None = None,
        hide_captions: bool | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        repeat_period: int | None = None,
        allow_paid_broadcast: bool | None = None,
        video_start_timestamp: int | None = None,
        paid_message_star_count: int | None = None,
        effect_id: int | None = None,
    ) -> types.Message | list[types.Message]:
        """Shortcut for method :obj:`~pyrogram.Client.forward_messages` will automatically fill method attributes:

        * from_chat_id
        * message_id

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_thread_id (``int``, *optional*):
                Unique identifier of a message thread to which the message belongs.
                For supergroups only.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            hide_sender_name (``bool``, *optional*):
                If True, the original author of the message will not be shown.

            hide_captions (``bool``, *optional*):
                If True, the original media captions will be removed.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            video_start_timestamp (``int``, *optional*):
                Video startpoint, in seconds.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            effect_id (``int``, *optional*):
                Unique identifier of the effect to apply to the message.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the forwarded message is returned.

        Example:
            .. code-block:: python

                await message.forward(chat_id)

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.forward_messages(
            chat_id=chat_id,
            from_chat_id=self.chat.id,
            message_ids=self.id,
            message_thread_id=message_thread_id,
            disable_notification=disable_notification,
            schedule_date=schedule_date,
            protect_content=protect_content,
            schedule_repeat_period=repeat_period,
            hide_sender_name=hide_sender_name,
            hide_captions=hide_captions,
            allow_paid_broadcast=allow_paid_broadcast,
            video_start_timestamp=video_start_timestamp,
            paid_message_star_count=paid_message_star_count,
            effect=effect_id,
        )

    async def copy(
        self,
        chat_id: int | str,
        caption: str | None = None,
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        video_cover: str | BinaryIO | None = None,
        video_start_timestamp: int | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        protect_content: bool | None = None,
        has_spoiler: bool | None = None,
        show_caption_above_media: bool | None = None,
        business_connection_id: str | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: types.InlineKeyboardMarkup
        | types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.ForceReply
        | None = object,
        reply_to_chat_id: int | str | None = None,
        reply_to_message_id: int | None = None,
        quote_text: str | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
    ) -> types.Message:
        """Shortcut for method :obj:`~pyrogram.Client.copy_message` will automatically fill method attributes:

        * from_chat_id
        * message_id

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            caption (``str``, *optional*):
                New caption for media, 0-1024 characters after entities parsing.
                If not specified, the original caption is kept.
                Pass "" (empty string) to remove the caption.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the new caption, which can be specified instead of *parse_mode*.

            video_cover (``str`` | ``BinaryIO``, *optional*):
                New cover for the copied video in the message. Pass None to skip cover uploading and use the existing cover.

            video_start_timestamp (``int``, *optional*):
                New start timestamp, from which the video playing must start, in seconds for the copied video in the message.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For supergroups only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
                If not specified, the original reply markup is kept.
                Pass None to remove the reply markup.

            has_spoiler (``bool``, *optional*):
                Pass True if the copied media needs to be covered with a spoiler animation.

            reply_to_chat_id (``int`` | ``str``, *optional*):
                Unique identifier of the original message chat for reply.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            quote_text (``str``, *optional*):
                Text of the quote to be sent.

            quote_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                Special entities like usernames, URLs, bot commands, etc. that appear in the quote text.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the direct messages topic to copy into.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect to add to the message.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the copied message is returned.

        Example:
            .. code-block:: python

                await message.copy(chat_id)

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if self.service:
            log.warning(
                "Service messages cannot be copied. chat_id: %s, message_id: %s",
                self.chat.id,
                self.id,
            )
        elif self.game and not await self._client.storage.is_bot():
            log.warning(
                "Users cannot send messages with Game media type. chat_id: %s, message_id: %s",
                self.chat.id,
                self.id,
            )
        elif self.empty:
            log.warning("Empty messages cannot be copied.")
        elif self.rich_message:
            if reply_parameters is None and reply_to_message_id is not None:
                reply_parameters = types.ReplyParameters(
                    message_id=reply_to_message_id,
                    chat_id=reply_to_chat_id,
                    quote=quote_text,
                    quote_entities=quote_entities,
                )

            return await self._client.send_rich_message(
                chat_id=chat_id,
                rich_text=self.rich_message,
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
                reply_parameters=reply_parameters,
                schedule_date=schedule_date,
                protect_content=self.has_protected_content
                if protect_content is None
                else protect_content,
                effect_id=effect_id,
                reply_markup=self.reply_markup if reply_markup is object else reply_markup,
                business_connection_id=business_connection_id,
                allow_paid_broadcast=allow_paid_broadcast,
                paid_message_star_count=paid_message_star_count,
                direct_messages_topic_id=direct_messages_topic_id,
                suggested_post_parameters=suggested_post_parameters,
            )
        elif self.text:
            return await self._client.send_message(
                chat_id,
                text=self.text,
                entities=self.entities,
                parse_mode=enums.ParseMode.DISABLED,
                link_preview_options=types.LinkPreviewOptions(is_disabled=not self.web_page),
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
                reply_parameters=reply_parameters,
                reply_to_chat_id=reply_to_chat_id,
                reply_to_message_id=reply_to_message_id,
                quote_text=quote_text,
                quote_entities=quote_entities,
                schedule_date=schedule_date,
                protect_content=protect_content,
                business_connection_id=business_connection_id,
                allow_paid_broadcast=allow_paid_broadcast,
                paid_message_star_count=paid_message_star_count,
                direct_messages_topic_id=direct_messages_topic_id,
                effect_id=effect_id,
                suggested_post_parameters=suggested_post_parameters,
                reply_markup=self.reply_markup if reply_markup is object else reply_markup,
            )
        elif self.media:
            send_media = partial(
                self._client.send_cached_media,
                chat_id=chat_id,
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
                reply_parameters=reply_parameters,
                reply_to_message_id=reply_to_message_id,
                reply_to_chat_id=reply_to_chat_id,
                quote_text=quote_text,
                quote_entities=quote_entities,
                schedule_date=schedule_date,
                protect_content=protect_content,
                effect_id=effect_id,
                has_spoiler=self.has_media_spoiler if has_spoiler is None else has_spoiler,
                show_caption_above_media=self.show_caption_above_media
                if show_caption_above_media is None
                else show_caption_above_media,
                business_connection_id=business_connection_id,
                allow_paid_broadcast=allow_paid_broadcast,
                paid_message_star_count=paid_message_star_count,
                direct_messages_topic_id=direct_messages_topic_id,
                suggested_post_parameters=suggested_post_parameters,
                reply_markup=self.reply_markup if reply_markup is object else reply_markup,
            )

            if self.photo:
                file_id = self.photo.file_id
            elif self.audio:
                file_id = self.audio.file_id
            elif self.document:
                file_id = self.document.file_id
            elif self.video:
                if caption is None:
                    caption = self.caption or ""
                    caption_entities = self.caption_entities

                return await self._client.send_video(
                    chat_id,
                    video=self.video.file_id,
                    caption=caption,
                    parse_mode=parse_mode,
                    caption_entities=caption_entities,
                    has_spoiler=self.has_media_spoiler if has_spoiler is None else has_spoiler,
                    show_caption_above_media=self.show_caption_above_media
                    if show_caption_above_media is None
                    else show_caption_above_media,
                    disable_notification=disable_notification,
                    message_thread_id=self.message_thread_id
                    if message_thread_id is None
                    else message_thread_id,
                    business_connection_id=self.business_connection_id
                    if business_connection_id is None
                    else business_connection_id,
                    schedule_date=schedule_date,
                    protect_content=self.has_protected_content
                    if protect_content is None
                    else protect_content,
                    allow_paid_broadcast=allow_paid_broadcast,
                    paid_message_star_count=paid_message_star_count,
                    direct_messages_topic_id=direct_messages_topic_id,
                    suggested_post_parameters=suggested_post_parameters,
                    reply_parameters=reply_parameters,
                    reply_markup=self.reply_markup if reply_markup is object else reply_markup,
                    video_cover=video_cover
                    if video_cover is not None
                    else self.video.video_cover.file_id
                    if self.video.video_cover
                    else None,
                    video_start_timestamp=video_start_timestamp
                    if video_start_timestamp is not None
                    else self.video.video_start_timestamp,
                    effect_id=effect_id,
                )
            elif self.animation:
                file_id = self.animation.file_id
            elif self.voice:
                file_id = self.voice.file_id
            elif self.sticker:
                file_id = self.sticker.file_id
            elif self.video_note:
                file_id = self.video_note.file_id
            elif self.contact:
                return await self._client.send_contact(
                    chat_id,
                    phone_number=self.contact.phone_number,
                    first_name=self.contact.first_name,
                    last_name=self.contact.last_name,
                    vcard=self.contact.vcard,
                    disable_notification=disable_notification,
                    reply_parameters=reply_parameters,
                    message_thread_id=message_thread_id,
                    schedule_date=schedule_date,
                    allow_paid_broadcast=allow_paid_broadcast,
                    paid_message_star_count=paid_message_star_count,
                    direct_messages_topic_id=direct_messages_topic_id,
                    effect_id=effect_id,
                    suggested_post_parameters=suggested_post_parameters,
                    business_connection_id=business_connection_id,
                )
            elif self.location:
                return await self._client.send_location(
                    chat_id,
                    latitude=self.location.latitude,
                    longitude=self.location.longitude,
                    disable_notification=disable_notification,
                    message_thread_id=message_thread_id,
                    reply_parameters=reply_parameters,
                    schedule_date=schedule_date,
                    allow_paid_broadcast=allow_paid_broadcast,
                    paid_message_star_count=paid_message_star_count,
                    direct_messages_topic_id=direct_messages_topic_id,
                    effect_id=effect_id,
                    suggested_post_parameters=suggested_post_parameters,
                    business_connection_id=business_connection_id,
                )
            elif self.venue:
                return await self._client.send_venue(
                    chat_id,
                    latitude=self.venue.location.latitude,
                    longitude=self.venue.location.longitude,
                    title=self.venue.title,
                    address=self.venue.address,
                    foursquare_id=self.venue.foursquare_id,
                    foursquare_type=self.venue.foursquare_type,
                    disable_notification=disable_notification,
                    message_thread_id=message_thread_id,
                    reply_parameters=reply_parameters,
                    schedule_date=schedule_date,
                    allow_paid_broadcast=allow_paid_broadcast,
                    paid_message_star_count=paid_message_star_count,
                    direct_messages_topic_id=direct_messages_topic_id,
                    effect_id=effect_id,
                    suggested_post_parameters=suggested_post_parameters,
                    business_connection_id=business_connection_id,
                )
            elif self.poll:
                if self.poll.type == enums.PollType.QUIZ and not self.poll.correct_option_ids:
                    raise ValueError(
                        "You can copy quiz polls which are closed or were sent (not forwarded) by the bot or to the private chat with the bot."
                    )

                return await self._client.send_poll(
                    chat_id,
                    question=self.poll.question,
                    options=[types.InputPollOption(text=opt.text) for opt in self.poll.options],
                    message_thread_id=message_thread_id,
                    business_connection_id=business_connection_id,
                    is_anonymous=self.poll.is_anonymous,
                    type=self.poll.type,
                    allows_multiple_answers=self.poll.allows_multiple_answers,
                    allows_revoting=self.poll.allows_revoting,
                    correct_option_ids=self.poll.correct_option_ids,
                    explanation=self.poll.explanation,
                    open_period=self.poll.open_period,
                    description=self.poll.description,
                    disable_notification=disable_notification,
                    reply_parameters=reply_parameters,
                    schedule_date=schedule_date,
                    allow_paid_broadcast=allow_paid_broadcast,
                    paid_message_star_count=paid_message_star_count,
                    direct_messages_topic_id=direct_messages_topic_id,
                    effect_id=effect_id,
                    suggested_post_parameters=suggested_post_parameters,
                )
            elif self.game:
                return await self._client.send_game(
                    chat_id,
                    game_short_name=self.game.short_name,
                    disable_notification=disable_notification,
                    allow_paid_broadcast=allow_paid_broadcast,
                    message_thread_id=message_thread_id,
                )
            elif self.dice:
                return await self._client.send_dice(
                    chat_id,
                    emoji=self.dice.emoji,
                    disable_notification=disable_notification,
                    message_thread_id=message_thread_id,
                    reply_parameters=reply_parameters,
                    schedule_date=schedule_date,
                    protect_content=protect_content,
                    allow_paid_broadcast=allow_paid_broadcast,
                    paid_message_star_count=paid_message_star_count,
                    direct_messages_topic_id=direct_messages_topic_id,
                    effect_id=effect_id,
                    suggested_post_parameters=suggested_post_parameters,
                    business_connection_id=business_connection_id,
                )
            else:
                raise ValueError(f"Unable to copy a {self.media} message")

            if caption is None:
                caption = self.caption or ""
                caption_entities = self.caption_entities

            return await send_media(
                file_id=file_id,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                message_thread_id=message_thread_id,
            )
        else:
            raise ValueError("Can't copy this message")

    async def copy_media_group(
        self,
        chat_id: int | str,
        captions: list[str] | str | None = None,
        has_spoilers: list[bool] | bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        show_caption_above_media: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        reply_to_message_id: int | None = None,
        reply_to_chat_id: int | str | None = None,
        reply_to_story_id: int | None = None,
        quote_text: str | None = None,
        parse_mode: enums.ParseMode | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
        quote_offset: int | None = None,
    ) -> list[types.Message]:
        """Shortcut for method :obj:`~pyrogram.Client.copy_media_group` will automatically fill method attributes:

        * from_chat_id
        * message_id

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            captions (``str`` | List of ``str`` , *optional*):
                New caption for media, 0-1024 characters after entities parsing for each media.
                If not specified, the original caption is kept.
                Pass "" (empty string) to remove the caption.

                If a ``str`` is passed, it becomes a caption only for the first media.
                If a list of ``str`` passed, each element becomes caption for each media element.
                You can pass ``None`` in list to keep the original caption.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For supergroups only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

        Returns:
            List of :obj:`~pyrogram.types.Message`: On success, a list of copied messages is returned.
        """
        return await self._client.copy_media_group(
            chat_id=chat_id,
            from_chat_id=self.chat.id,
            message_id=self.id,
            captions=captions,
            has_spoilers=has_spoilers,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            show_caption_above_media=show_caption_above_media,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            reply_to_message_id=reply_to_message_id,
        )

    async def delete(self, revoke: bool = True):
        """Shortcut for method :obj:`~pyrogram.Client.delete_messages` will automatically fill method attributes:

        * chat_id
        * message_ids

        Parameters:
            revoke (``bool``, *optional*):
                Deletes messages on both parts.
                This is only for private cloud chats and normal groups, messages on
                channels and supergroups are always revoked (i.e.: deleted for everyone).
                Defaults to True.

        Returns:
            ``bool``: True on success, False otherwise.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        r = await self._client.delete_messages(
            chat_id=self.chat.id, message_ids=self.id, revoke=revoke
        )

        return bool(r)

    async def delete_fact_check(self) -> types.Message:
        """Bound method *delete_fact_check* of :obj:`~pyrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.delete_fact_check(
                chat_id=message.chat.id,
                message_id=message.id
            )

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the updated message is returned.
        """
        return await self._client.delete_fact_check(
            chat_id=self.chat.id,
            message_id=self.id,
        )

    async def edit_fact_check(
        self,
        text_with_entities: raw.types.TextWithEntities | None = None,
    ) -> types.Message:
        """Bound method *edit_fact_check* of :obj:`~pyrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.edit_fact_check(
                peer=message.chat.id,
                msg_id=message.id,
                text_with_entities=text_with_entities
            )

        Parameters:
            text_with_entities (:obj:`~pyrogram.raw.types.TextWithEntities`, *optional*):
                Fact-check content as TextWithEntities.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the updated message is returned.
        """
        return await self._client.edit_fact_check(
            peer=self.chat.id,
            msg_id=self.id,
            text_with_entities=text_with_entities,
        )

    async def click(
        self,
        x: int | str = 0,
        y: int | None = None,
        quote: bool | None = None,
        timeout: int = 10,
        password: str | None = None,
    ):
        """Bound method *click* of :obj:`~pyrogram.types.Message`.

        Use as a shortcut for clicking a button attached to the message instead of:

        - Clicking inline buttons:

        .. code-block:: python

            await client.request_callback_answer(
                chat_id=message.chat.id,
                message_id=message.id,
                callback_data=message.reply_markup[i][j].callback_data
            )

        - Clicking normal buttons:

        .. code-block:: python

            await client.send_message(
                chat_id=message.chat.id,
                text=message.reply_markup[i][j].text
            )

        Example:
            This method can be used in three different ways:

            1.  Pass one integer argument only (e.g.: ``.click(2)``, to click a button at index 2).
                Buttons are counted left to right, starting from the top.

            2.  Pass two integer arguments (e.g.: ``.click(1, 0)``, to click a button at position (1, 0)).
                The origin (0, 0) is top-left.

            3.  Pass one string argument only (e.g.: ``.click("Settings")``, to click a button by using its label).
                Only the first matching button will be pressed.

        Parameters:
            x (``int`` | ``str``):
                Used as integer index, integer abscissa (in pair with y) or as string label.
                Defaults to 0 (first button).

            y (``int``, *optional*):
                Used as ordinate only (in pair with x).

            quote (``bool``, *optional*):
                Useful for normal buttons only, where pressing it will result in a new message sent.
                If ``True``, the message will be sent as a reply to this message.

            timeout (``int``, *optional*):
                Timeout in seconds.

            password (``str``, *optional*):
                When clicking certain buttons (such as BotFather's confirmation button to transfer ownership), if your account has 2FA enabled, you need to provide your account's password.
                The 2-step verification password for the current user. Only applicable, if the :obj:`~pyrogram.types.InlineKeyboardButton` contains ``requires_password``.

        Returns:
            -   The result of :meth:`~pyrogram.Client.request_callback_answer` in case of inline callback button clicks.
            -   The result of :meth:`~Message.reply()` or :meth:`~Message.answer()` in case of normal button clicks.
            -   A string in case the inline button is a URL, a *switch_inline_query*,
                *switch_inline_query_current_chat* or a *copy_text* button.
            -   A string URL with the user details, in case of a WebApp button.
            -   A :obj:`~pyrogram.types.Chat` object in case of a ``KeyboardButtonUserProfile`` button.

        Raises:
            RPCError: In case of a Telegram RPC error.
            ValueError: In case the provided index or position is out of range or the button label was not found.
            TimeoutError: In case, after clicking an inline button, the bot fails to answer within the timeout.
        """

        if isinstance(self.reply_markup, types.ReplyKeyboardMarkup):
            keyboard = self.reply_markup.keyboard
            is_inline = False
        elif isinstance(self.reply_markup, types.InlineKeyboardMarkup):
            keyboard = self.reply_markup.inline_keyboard
            is_inline = True
        else:
            raise ValueError("The message doesn't contain any keyboard")

        if isinstance(x, int) and y is None:
            try:
                button = [button for row in keyboard for button in row][x]
            except IndexError:
                raise ValueError(f"The button at index {x} doesn't exist")
        elif isinstance(x, int) and isinstance(y, int):
            try:
                button = keyboard[y][x]
            except IndexError:
                raise ValueError(f"The button at position ({x}, {y}) doesn't exist")
        elif isinstance(x, str) and y is None:
            label = x.encode("utf-16", "surrogatepass").decode("utf-16")

            try:
                button = [button for row in keyboard for button in row if label == button.text][0]
            except IndexError:
                raise ValueError(f"The button with label '{x}' doesn't exists")
        else:
            raise ValueError("Invalid arguments")

        if is_inline:
            if button.callback_data:
                if button.requires_password and password is None:
                    raise ValueError("This button requires a password")

                return await self._client.request_callback_answer(
                    chat_id=self.chat.id,
                    message_id=self.id,
                    callback_data=button.callback_data,
                    password=password,
                    timeout=timeout,
                )
            elif button.url:
                return button.url
            elif button.web_app:
                web_app = button.web_app

                bot_peer_id = (
                    (self.via_bot and self.via_bot.id)
                    or (self.from_user and self.from_user.is_bot and self.from_user.id)
                    or None
                )

                if not bot_peer_id:
                    raise ValueError("This button requires a bot as the sender")

                return await self._client.open_web_app(
                    chat_id=self.chat.id,
                    bot_user_id=bot_peer_id,
                    url=web_app.url,
                    message_thread_id=self.message_thread_id,
                    direct_messages_topic_id=self.direct_messages_topic_id,
                )
            elif button.user_id:
                return await self._client.get_chat(button.user_id)
            elif button.switch_inline_query:
                return button.switch_inline_query
            elif button.switch_inline_query_current_chat:
                return button.switch_inline_query_current_chat
            elif button.copy_text:
                return button.copy_text
            else:
                raise ValueError("This button is not supported yet")
        else:
            if quote:
                await self.reply(text=button)
            else:
                await self.answer(text=button)

    async def react(
        self, emoji: int | str | list[int | str] | None = None, big: bool = False
    ) -> bool:
        """Shortcut for method :obj:`~pyrogram.Client.send_reaction` will automatically fill method attributes:

        * chat_id
        * message_id
        * business_connection_id

        Example:
            .. code-block:: python

                await message.react(emoji="🔥")

        Parameters:
            emoji (``int`` | ``str`` | List of ``int`` | ``str``, *optional*):
                Reaction emoji.
                Pass None as emoji (default) to retract the reaction.
                Pass list of int or str to react multiple emojis.

            big (``bool``, *optional*):
                Pass True to show a bigger and longer reaction.
                Defaults to False.

        Returns:
            ``bool``: On success, True is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        return await self._client.send_reaction(
            chat_id=self.chat.id,
            message_id=self.id,
            emoji=emoji,
            big=big,
            business_connection_id=self.business_connection_id,
        )

    async def retract_vote(
        self,
    ) -> types.Poll:
        """Shortcut for method :obj:`~pyrogram.Client.retract_vote` will automatically fill method attributes:

        * chat_id
        * message_id

        Returns:
            :obj:`~pyrogram.types.Poll`: On success, the poll with the retracted vote is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        return await self._client.retract_vote(chat_id=self.chat.id, message_id=self.id)

    async def download(
        self,
        file_name: str = "",
        in_memory: bool = False,
        block: bool = True,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> str:
        """Shortcut for method :obj:`~pyrogram.Client.download_media` will automatically fill method attributes:

        * message

        Parameters:
            file_name (``str``, *optional*):
                A custom *file_name* to be used instead of the one provided by Telegram.
                By default, all files are downloaded in the *downloads* folder in your working directory.
                You can also specify a path for downloading files in a custom location: paths that end with "/"
                are considered directories. All non-existent folders will be created automatically.

            in_memory (``bool``, *optional*):
                Pass True to download the media in-memory.
                A binary file-like object with its attribute ".name" set will be returned.
                Defaults to False.

            block (``bool``, *optional*):
                Blocks the code execution until the file has been downloaded.
                Defaults to True.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            On success, the absolute path of the downloaded file as string is returned, None otherwise.

        Raises:
            RPCError: In case of a Telegram RPC error.
            ``ValueError``: If the message doesn't contain any downloadable media
        """
        return await self._client.download_media(
            message=self,
            file_name=file_name,
            in_memory=in_memory,
            block=block,
            progress=progress,
            progress_args=progress_args,
        )

    async def vote(self, option: int | list[int]) -> types.Poll:
        """Shortcut for method :obj:`~pyrogram.Client.vote_poll` will automatically fill method attributes:

        * chat_id
        * message_id

        Parameters:
            option (``int`` | List of ``int``):
                Index or list of indexes (for multiple answers) of the poll option(s) you want to vote for (0 to 11).

        Returns:
            :obj:`~pyrogram.types.Poll`: On success, the poll with the chosen option is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        return await self._client.vote_poll(
            chat_id=self.chat.id, message_id=self.id, options=option
        )

    async def pin(
        self, disable_notification: bool = False, both_sides: bool = False
    ) -> types.Message | None:
        """Shortcut for method :obj:`~pyrogram.Client.pin_chat_message` will automatically fill method attributes:

        * chat_id
        * message_id

        Parameters:
            disable_notification (``bool``):
                Pass True, if it is not necessary to send a notification to all chat members about the new pinned
                message. Notifications are always disabled in channels.

            both_sides (``bool``, *optional*):
                Pass True to pin the message for both sides (you and recipient).
                Applicable to private chats only. Defaults to False.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the service message is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.pin_chat_message(
            chat_id=self.chat.id,
            message_id=self.id,
            disable_notification=disable_notification,
            both_sides=both_sides,
        )

    async def unpin(self) -> bool:
        """Shortcut for method :obj:`~pyrogram.Client.unpin_chat_message` will automatically fill method attributes:

        * chat_id
        * message_id

        Returns:
            True on success.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.unpin_chat_message(chat_id=self.chat.id, message_id=self.id)

    async def read(self) -> bool:
        """Shortcut for method :obj:`~pyrogram.Client.read_chat_history` will automatically fill method attributes:

        * chat_id
        * max_id

        Returns:
            True on success.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.read_chat_history(chat_id=self.chat.id, max_id=self.id)

    async def view(self) -> bool:
        """Shortcut for method :obj:`~pyrogram.Client.view_messages` will automatically fill method attributes:

        * chat_id
        * message_id

        Returns:
            True on success.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self._client.view_messages(chat_id=self.chat.id, message_id=self.id)

    async def pay(self) -> types.PaymentResult:
        """Bound method *pay* of :obj:`~pyrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            invoice = types.InputInvoiceMessage(
                    chat_id=chat_id,
                    message_id=123
                )

            form = await app.get_payment_form(invoice)

            await app.send_payment_form(
                payment_form_id=form.id,
                input_invoice=invoice
            )

        Example:
            .. code-block:: python

                await message.pay()

        Returns:
            :obj:`~pyrogram.types.PaymentResult`: On success, the payment result is returned.
        """
        invoice = types.InputInvoiceMessage(chat_id=self.chat.id, message_id=self.id)

        form = await self._client.get_payment_form(invoice)

        return await self._client.send_payment_form(payment_form_id=form.id, input_invoice=invoice)

    async def accept_gift_purchase_offer(self) -> types.Message:
        """Shortcut for method :obj:`~pyrogram.Client.process_gift_purchase_offer` will automatically fill method attributes:

        * message_id

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.
        """
        return await self._client.process_gift_purchase_offer(message_id=self.id, accept=True)

    async def reject_gift_purchase_offer(self) -> types.Message:
        """Shortcut for method :obj:`~pyrogram.Client.process_gift_purchase_offer` will automatically fill method attributes:

        * message_id

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.
        """
        return await self._client.process_gift_purchase_offer(message_id=self.id, accept=False)

    async def summarize(self, translate_to_language_code: str | None = None) -> types.FormattedText:
        """Shortcut for method :obj:`~pyrogram.Client.summarize_text` will automatically fill method attributes:

        * peer
        * id
        * to_lang

        Parameters:
            translate_to_language_code (``str``, *optional*):
                Language code of the language to which the message is translated.
                Must be one of "af", "sq", "am", "ar", "hy", "az", "eu", "be", "bn", "bs", "bg", "ca", "ceb", "zh-CN", "zh", "zh-Hans", "zh-TW", "zh-Hant", "co", "hr", "cs", "da", "nl", "en", "eo", "et",
                "fi", "fr", "fy", "gl", "ka", "de", "el", "gu", "ht", "ha", "haw", "he", "iw", "hi", "hmn", "hu", "is", "ig", "id", "in", "ga", "it", "ja", "jv", "kn", "kk", "km", "rw", "ko",
                "ku", "ky", "lo", "la", "lv", "lt", "lb", "mk", "mg", "ms", "ml", "mt", "mi", "mr", "mn", "my", "ne", "no", "ny", "or", "ps", "fa", "pl", "pt", "pa", "ro", "ru", "sm", "gd", "sr",
                "st", "sn", "sd", "si", "sk", "sl", "so", "es", "su", "sw", "sv", "tl", "tg", "ta", "tt", "te", "th", "tr", "tk", "uk", "ur", "ug", "uz", "vi", "cy", "xh", "yi", "ji", "yo", "zu"
                Defaults to the client's language code.

        Returns:
            :obj:`~pyrogram.types.FormattedText`: On success, information about the summarized text is returned.

        Raises:
            ValueError: In case of this message can't be summarized.
        """
        if not self.summary_language_code:
            raise ValueError("This message can't be summarized.")

        if translate_to_language_code is None:
            translate_to_language_code = self._client.lang_code

        return await self._client.summarize_text(
            peer=self.chat.id, id=self.id, to_lang=translate_to_language_code
        )

    async def wait_for_click(self, user_id=None, timeout=UNSET, filters=None, alert=True):
        """Bound method *wait_for_click* of :obj:`~pyrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            await client.listen(
                listener_type=enums.ListenerTypes.CALLBACK_QUERY,
                chat_id=message.chat.id,
                message_id=message.id
            )

        Example:
            .. code-block:: python

                sent = await message.reply("Pick one", reply_markup=keyboard)
                query = await sent.wait_for_click(timeout=60)

        Parameters:
            user_id (``int`` | ``str`` | List of ``int`` | ``str``, *optional*):
                Only accept a click from this user.

            timeout (``float``, *optional*):
                Seconds to wait before raising ``ListenerTimeout``. Defaults to
                the client's ``listener_timeout``.

            filters (:obj:`~pyrogram.filters.Filter`, *optional*):
                Extra filter the callback query has to pass.

            alert (``bool`` | ``str``, *optional*):
                Answer clicks coming from a user this listener does not expect.
                Pass a string to set the text.

        Returns:
            :obj:`~pyrogram.types.CallbackQuery`: The matching callback query.

        Raises:
            ListenerTimeout: In case nobody clicked in time.
        """
        return await self._client.listen(
            filters=filters,
            listener_type=enums.ListenerTypes.CALLBACK_QUERY,
            timeout=timeout,
            unallowed_click_alert=alert,
            chat_id=self.chat.id,
            user_id=user_id,
            message_id=self.id,
        )

    async def report(
        self,
        reason: enums.ReportReason | raw.base.ReportReason | str = enums.ReportReason.SPAM,
        message: str = "",
        option: bytes = b"",
    ) -> bool:
        """Bound method *report* of :obj:`~pyrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            client.report_messages(chat_id, message_id, reason, message, option)

        Parameters:
            reason (:obj:`~pyrogram.enums.ReportReason` | ``str``, *optional*):
                The reason for reporting. Defaults to :obj:`~pyrogram.enums.ReportReason.SPAM`.

            message (``str``, *optional*):
                Additional explanatory text or details about the report. Defaults to "".

            option (``bytes``, *optional*):
                Specific report option bytes. Defaults to b"".

        Example:
            .. code-block:: python

                await message.report(enums.ReportReason.SPAM)

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self._client.report_messages(
            chat_id=self.chat.id,
            message_ids=self.id,
            reason=reason,
            message=message,
            option=option,
        )

    async def transcribe(self) -> types.TranscribedAudio:
        """Bound method *transcribe* of :obj:`~pyrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            client.transcribe_audio(
                chat_id=message.chat.id,
                message_id=message.id
            )

        Example:
            .. code-block:: python

                transcription = await message.transcribe()
                print(transcription.text)

        Returns:
            :obj:`~pyrogram.types.TranscribedAudio`: On success, the transcribed audio object is returned.
        """
        return await self._client.transcribe_audio(
            chat_id=self.chat.id,
            message_id=self.id,
        )

    def get_reactions(
        self,
        reaction: raw.base.Reaction | types.Reaction | str | int | None = None,
        limit: int = 0,
    ) -> AsyncGenerator[types.MessagePeerReaction, None] | None:
        """Bound method *get_reactions* of :obj:`~pyrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            client.get_message_reactions(
                chat_id=message.chat.id,
                message_id=message.id
            )

        Parameters:
            reaction (``str`` | ``int`` | :obj:`~pyrogram.types.Reaction`, *optional*):
                Target reaction to filter by. Defaults to None (returns all reactions).

            limit (``int``, *optional*):
                Limits the number of reactions to be retrieved.
                By default, no limit is applied and all reactions are returned.

        Example:
            .. code-block:: python

                async for reaction in message.get_reactions():
                    print(reaction.user.first_name, reaction.reaction)

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.MessagePeerReaction` objects.
        """
        return self._client.get_message_reactions(
            chat_id=self.chat.id,
            message_id=self.id,
            reaction=reaction,
            limit=limit,
        )

    async def get_read_participants(self) -> list[types.ReadParticipantDate]:
        """Bound method *get_read_participants* of :obj:`~pyrogram.types.Message`.

        Use as a shortcut for:

        .. code-block:: python

            client.get_message_read_participants(
                chat_id=message.chat.id,
                message_id=message.id
            )

        Example:
            .. code-block:: python

                readers = await message.get_read_participants()
                for reader in readers:
                    print(reader.user_id, reader.date)

        Returns:
            List of :obj:`~pyrogram.types.ReadParticipantDate`: On success, a list of participants and read dates is returned.
        """
        return await self._client.get_message_read_participants(
            chat_id=self.chat.id,
            message_id=self.id,
        )
