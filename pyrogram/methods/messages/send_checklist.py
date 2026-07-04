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
        disable_notification: bool = None,
        protect_content: bool = None,
        message_thread_id: int = None,
        effect_id: int = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        schedule_date: datetime = None,
        repeat_period: int = None,
        business_connection_id: str = None,
        paid_message_star_count: int = None,
        show_caption_above_media: bool = None,
        allow_paid_broadcast: bool = None,
        suggested_post_parameters: Optional["types.SuggestedPostParameters"] = None,
        background: Optional[bool] = None,
        clear_draft: Optional[bool] = None,
        update_stickersets_order: Optional[bool] = None,
        send_as: Union[int, str] = None,
        quick_reply_shortcut: int = None,
        reply_markup: Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ] = None,
    ) -> "types.Message":
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
                silent=disable_notification or None,
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
                allow_paid_stars=paid_message_star_count,
                invert_media=show_caption_above_media or None,
                allow_paid_floodskip=allow_paid_broadcast,
                suggested_post=suggested_post_parameters.write() if suggested_post_parameters else None,
                background=background,
                clear_draft=clear_draft,
                update_stickersets_order=update_stickersets_order,
                send_as=await self.resolve_peer(send_as) if send_as is not None else None,
                quick_reply_shortcut=raw.types.InputQuickReplyShortcut(shortcut_id=quick_reply_shortcut) if quick_reply_shortcut is not None else None,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                message="",
                entities=entities,
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
