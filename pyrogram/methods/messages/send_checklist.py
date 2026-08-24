from datetime import datetime
from typing import Union, List, Optional

import pyrogram
from pyrogram import raw, utils
from pyrogram import types


class SendChecklist:
    async def send_checklist(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        checklist: "types.InputChecklist",
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        message_thread_id: Optional[int] = None,
        effect_id: Optional[int] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        schedule_date: Optional[datetime] = None,
        repeat_period: Optional[int] = None,
        business_connection_id: Optional[str] = None,
        paid_message_star_count: Optional[int] = None,
        show_caption_above_media: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        suggested_post_parameters: Optional["types.SuggestedPostParameters"] = None,
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
        ]] = None,
    ) -> "types.Message":
        """Send a checklist (todo list).

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            checklist (:obj:`~pyrogram.types.InputChecklist`):
                The checklist to send, containing a title and list of tasks.

            disable_notification (``bool``, *optional*):
                Sends the message silently. Users will receive a notification with no sound.

            protect_content (``bool``, *optional*):
                Pass True to protect the message content from being forwarded.

            message_thread_id (``int``, *optional*):
                Unique identifier for a message thread in a forum topic.

            effect_id (``int``, *optional*):
                Unique identifier of the effect to apply to the message.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Description of the reply-to message.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period in seconds after which the message will be automatically repeated.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection.

            paid_message_star_count (``int``, *optional*):
                Number of Telegram Stars to require for access to the paid message.

            show_caption_above_media (``bool``, *optional*):
                Pass True to show the caption above the media.

            allow_paid_broadcast (``bool``, *optional*):
                Pass True to allow sending paid broadcast messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Parameters for creating a suggested channel post.

            background (``bool``, *optional*):
                Pass True to send the message as a background message.

            clear_draft (``bool``, *optional*):
                Pass True to clear the draft in the chat.

            update_stickersets_order (``bool``, *optional*):
                Pass True to update the stickersets order.

            send_as (``int`` | ``str``, *optional*):
                Unique identifier of the chat or user to send the message on behalf of.

            quick_reply_shortcut (``int``, *optional*):
                Shortcut ID for quick reply.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent checklist message is returned.

        Example:
            .. code-block:: python

                from wzgram.types import InputChecklist, InputChecklistTask

                checklist = InputChecklist(
                    title="Shopping List",
                    tasks=[
                        InputChecklistTask(text="Milk", checked=False),
                        InputChecklistTask(text="Eggs", checked=True),
                    ]
                )
                await app.send_checklist(chat_id, checklist)
        """
        title, entities = (await utils.parse_text_entities(
            self, checklist.title, checklist.parse_mode, checklist.entities
        )).values()

        r = await self.invoke(
            raw.functions.messages.SendMedia(
                peer=await self.resolve_peer(chat_id),
                media=raw.types.InputMediaTodo(
                    todo=raw.types.TodoList(
                        title=raw.types.TextWithEntities(
                            text=title,
                            entities=entities or []
                        ),
                        list=[await task.write(self) for task in checklist.tasks],
                        others_can_append=checklist.others_can_add_tasks,
                        others_can_complete=checklist.others_can_mark_tasks_as_done
                    )
                ),
                silent=disable_notification if disable_notification is not None else None,
                reply_to=await utils.get_reply_to(
                    self,
                    reply_parameters,
                    message_thread_id,
                ),
                random_id=self.rnd_id(),
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                noforwards=protect_content,
                effect=effect_id,
                schedule_repeat_period=repeat_period,
                allow_paid_stars=paid_message_star_count if paid_message_star_count is not None else None,
                invert_media=show_caption_above_media if show_caption_above_media is not None else None,
                allow_paid_floodskip=allow_paid_broadcast if allow_paid_broadcast is not None else None,
                suggested_post=suggested_post_parameters.write() if suggested_post_parameters else None,
                background=background,
                clear_draft=clear_draft,
                update_stickersets_order=update_stickersets_order,
                send_as=await self.resolve_peer(send_as) if send_as is not None else None,
                quick_reply_shortcut=raw.types.InputQuickReplyShortcutId(shortcut_id=quick_reply_shortcut) if quick_reply_shortcut is not None else None,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                entities=None,
                message="",
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
