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

from datetime import datetime
from typing import Union, List, Optional

import pyrogram
from pyrogram import raw, utils
from pyrogram import types, enums


class SendPoll:
    async def send_poll(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        question: Union[str, "types.FormattedText"],
        options: List[Union[str, "types.InputPollOption"]],
        is_anonymous: bool = True,
        type: "enums.PollType" = enums.PollType.REGULAR,
        allows_multiple_answers: Optional[bool] = None,
        correct_option_id: Optional[int] = None,
        correct_option_ids: Optional[List[int]] = None,
        explanation: Optional[Union[str, "types.FormattedText"]] = None,
        explanation_parse_mode: Optional["enums.ParseMode"] = None,
        explanation_entities: Optional[List["types.MessageEntity"]] = None,
        explanation_media: Optional["types.InputPollMedia"] = None,
        description: Optional["types.FormattedText"] = None,
        description_media: Optional["types.InputPollMedia"] = None,
        allows_revoting: Optional[bool] = None,
        members_only: Optional[bool] = None,
        country_codes: Optional[List[str]] = None,
        shuffle_options: Optional[bool] = None,
        allow_adding_options: Optional[bool] = None,
        hide_results_until_closes: Optional[bool] = None,
        open_period: Optional[int] = None,
        close_date: Optional[datetime] = None,
        is_closed: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_to_chat_id: Optional[Union[int, str]] = None,
        schedule_date: Optional[datetime] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        message_thread_id: Optional[int] = None,
        allow_paid_broadcast: Optional[bool] = None,
        paid_message_star_count: Optional[int] = None,
        business_connection_id: Optional[str] = None,
        quote_text: Optional[str] = None,
        quote_entities: Optional[List["types.MessageEntity"]] = None,
        effect_id: Optional[int] = None,
        show_caption_above_media: Optional[bool] = None,
        repeat_period: Optional[int] = None,
        suggested_post_parameters: Optional["types.SuggestedPostParameters"] = None,
        direct_messages_topic_id: Optional[int] = None,
        background: Optional[bool] = None,
        clear_draft: Optional[bool] = None,
        update_stickersets_order: Optional[bool] = None,
        send_as: Optional[Union[int, str]] = None,
        quick_reply_shortcut: Optional[int] = None,
        reply_markup: Optional[Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ]] = None
    ) -> "types.Message":
        """Send a new poll.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            question (``str`` | :obj:`~pyrogram.types.FormattedText`):
                Poll question, 1-255 characters.

            options (List of ``str`` | :obj:`~pyrogram.types.InputPollOption`):
                List of answer options, 2-10 strings 1-100 characters each.

            is_anonymous (``bool``, *optional*):
                True, if the poll needs to be anonymous.
                Defaults to True.

            type (:obj`~pyrogram.enums.PollType`, *optional*):
                Poll type, :obj:`~pyrogram.enums.PollType.QUIZ` or :obj:`~pyrogram.enums.PollType.REGULAR`.
                Defaults to :obj:`~pyrogram.enums.PollType.REGULAR`.

            allows_multiple_answers (``bool``, *optional*):
                True, if the poll allows multiple answers, ignored for polls in quiz mode.
                Defaults to False.

            correct_option_id (``int``, *optional*):
                0-based identifier of the correct answer option, required for polls in quiz mode.

            correct_option_ids (List of ``int``, *optional*):
                List of 0-based identifiers of the correct answer options, required for polls in quiz mode
                with multiple correct answers.

            explanation (``str`` | :obj:`~pyrogram.types.FormattedText`, *optional*):
                Text that is shown when a user chooses an incorrect answer or taps on the lamp icon in a quiz-style
                poll, 0-200 characters with at most 2 line feeds after entities parsing.

            explanation_parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            explanation_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the poll explanation, which can be specified instead of
                *parse_mode*.

            explanation_media (:obj:`~pyrogram.types.InputPollMedia`, *optional*):
                Media to display as part of the explanation.

            description (:obj:`~pyrogram.types.FormattedText`, *optional*):
                Poll description.

            description_media (:obj:`~pyrogram.types.InputPollMedia`, *optional*):
                Media to display as part of the description.

            allows_revoting (``bool``, *optional*):
                True, if the poll allows changing the vote.

            members_only (``bool``, *optional*):
                True, if only members of the chat can vote.

            country_codes (List of ``str``, *optional*):
                List of country ISO2 codes for country-specific polls.

            shuffle_options (``bool``, *optional*):
                True, if the poll options should be shuffled.

            allow_adding_options (``bool``, *optional*):
                True, if users can add options to the poll.

            hide_results_until_closes (``bool``, *optional*):
                True, if the poll results are hidden until the poll closes.

            open_period (``int``, *optional*):
                Amount of time in seconds the poll will be active after creation, 5-600.
                Can't be used together with *close_date*.

            close_date (:py:obj:`~datetime.datetime`, *optional*):
                Point in time when the poll will be automatically closed.
                Must be at least 5 and no more than 600 seconds in the future.
                Can't be used together with *open_period*.

            is_closed (``bool``, *optional*):
                Pass True, if the poll needs to be immediately closed.
                This can be useful for poll preview.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            reply_to_chat_id (``int`` | ``str``, *optional*):
                Unique identifier for the chat to which the replied message belongs.
                Only applicable in combination with *reply_to_message_id*.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            message_thread_id (``int``, *optional*):
                Unique identifier for a message thread in a forum topic.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection.

            quote_text (``str``, *optional*):
                Text of the quote to reply to.

            quote_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in *quote_text*, which can be specified instead of *parse_mode*.

            effect_id (``int``, *optional*):
                Unique identifier of the effect to apply to the message.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            repeat_period (``int``, *optional*):
                New period in seconds for the message to be sent repeatedly.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters of the suggested post.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only only.

            background (``bool``, *optional*):
                Send the message in background.

            clear_draft (``bool``, *optional*):
                Clear the draft of the chat.

            update_stickersets_order (``bool``, *optional*):
                Move the sticker set to the top of the list.

            send_as (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the chat or channel to send the message as.

            quick_reply_shortcut (``int``, *optional*):
                Unique identifier of the quick reply shortcut the message belongs to.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent poll message is returned.

        Example:
            .. code-block:: python

                await app.send_poll(chat_id, "Is this a poll question?", ["Yes", "No", "Maybe"])
        """

        if reply_parameters is None:
            if reply_to_message_id is not None:
                reply_parameters = types.ReplyParameters(
                    message_id=reply_to_message_id,
                    chat_id=reply_to_chat_id,
                    quote=quote_text,
                    quote_entities=quote_entities,
                )
            elif quote_text is not None:
                reply_parameters = types.ReplyParameters(
                    message_id=None,
                    chat_id=reply_to_chat_id,
                    quote=quote_text,
                    quote_entities=quote_entities,
                )

        if isinstance(question, types.FormattedText):
            question_text = question.text
            question_entities = question.entities or []
        else:
            question_text = question
            question_entities = []

        if isinstance(explanation, types.FormattedText):
            solution_text = explanation.text
            solution_entities = explanation.entities or []
        elif explanation is not None:
            solution_text, solution_entities = (await utils.parse_text_entities(
                self, explanation, explanation_parse_mode, explanation_entities
            )).values()
        else:
            solution_text = None
            solution_entities = []

        if isinstance(description, types.FormattedText):
            description_text = description.text
            description_entities = description.entities or []
        else:
            description_text = description
            description_entities = []

        parsed_options = []
        for opt in options:
            if isinstance(opt, types.InputPollOption):
                parsed_options.append(await opt.write(self))
            else:
                parsed_options.append(
                    raw.types.InputPollAnswer(
                        text=raw.types.TextWithEntities(text=opt, entities=[])
                    )
                )

        correct = None
        if correct_option_ids is not None:
            correct = list(correct_option_ids)
        elif correct_option_id is not None:
            correct = [correct_option_id]

        solution_media = (
            await explanation_media.write(client=self, chat_id=chat_id)
            if explanation_media is not None
            else None
        )

        attached_media = (
            await description_media.write(client=self, chat_id=chat_id)
            if description_media is not None
            else None
        )

        r = await self.invoke(
            raw.functions.messages.SendMedia(
                peer=await self.resolve_peer(chat_id),
                media=raw.types.InputMediaPoll(
                    poll=raw.types.Poll(
                        id=self.rnd_id(),
                        question=raw.types.TextWithEntities(text=question_text, entities=question_entities),
                        answers=parsed_options,
                        hash=self.rnd_id(),
                        closed=is_closed,
                        public_voters=not is_anonymous,
                        multiple_choice=allows_multiple_answers,
                        quiz=type == enums.PollType.QUIZ or False,
                        close_period=open_period,
                        close_date=utils.datetime_to_timestamp(close_date),
                        open_answers=allow_adding_options,
                        revoting_disabled=not allows_revoting if allows_revoting is not None else None,
                        shuffle_answers=shuffle_options,
                        hide_results_until_close=hide_results_until_closes,
                        subscribers_only=members_only,
                        countries_iso2=country_codes,
                    ),
                    correct_answers=correct,
                    solution=solution_text,
                    solution_entities=solution_entities or [],
                    solution_media=solution_media,
                    attached_media=attached_media,
                ),
                message=description_text or "",
                silent=disable_notification if disable_notification is not None else None,
                reply_to=await utils.get_reply_to(
                    self,
                    reply_parameters,
                    message_thread_id,
                    direct_messages_topic_id=direct_messages_topic_id,
                ),
                random_id=self.rnd_id(),
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                noforwards=protect_content,
                allow_paid_floodskip=allow_paid_broadcast if allow_paid_broadcast is not None else None,
                allow_paid_stars=paid_message_star_count if paid_message_star_count is not None else None,
                effect=effect_id,
                invert_media=show_caption_above_media if show_caption_above_media is not None else None,
                schedule_repeat_period=repeat_period,
                suggested_post=suggested_post_parameters.write() if suggested_post_parameters else None,
                background=background,
                clear_draft=clear_draft,
                update_stickersets_order=update_stickersets_order,
                send_as=await self.resolve_peer(send_as) if send_as is not None else None,
                quick_reply_shortcut=raw.types.InputQuickReplyShortcutId(shortcut_id=quick_reply_shortcut) if quick_reply_shortcut is not None else None,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                entities=description_entities or None,
            ),
            sleep_threshold=60,
            business_connection_id=business_connection_id
        )

        for i in r.updates:
            if isinstance(i, (raw.types.UpdateNewMessage,
                              raw.types.UpdateNewChannelMessage,
                              raw.types.UpdateNewScheduledMessage)):
                return await types.Message._parse(
                    self, i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats},
                    is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage)
                )
