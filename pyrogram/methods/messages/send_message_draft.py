from typing import List, Union, Optional

import pyrogram
from pyrogram import enums, raw, types, utils


class SendMessageDraft:
    async def send_message_draft(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        draft_id: int,
        text: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: Optional[List["types.MessageEntity"]] = None,
        message_thread_id: Optional[int] = None,
        can_stop: Optional[bool] = None,
        keep_on_stop: Optional[bool] = None,
    ) -> bool:
        """Send a text draft action, allowing bots to stream a partial message.

        When generating a message progressively (e.g. during AI response streaming),
        this method shows the user a typing indicator with the partial text.
        Pass an empty *text* to show a "Thinking..." placeholder while waiting for
        content to be generated.

        See :meth:`~pyrogram.Client.send_rich_message_draft` to stream a rich message
        instead of plain text.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            draft_id (``int``):
                Unique identifier of the draft; must be non-zero.
                Keep it constant for the whole generation, updates sharing an identifier are animated by clients.
                A different identifier does not restart the draft, it adds a second concurrent draft,
                and some clients collapse them into one.

            text (``str``, *optional*):
                The partial text to stream, 0-4096 characters after entities parsing.
                Defaults to an empty string, which shows a "Thinking..." placeholder.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in the text, which can be specified instead of *parse_mode*.

            message_thread_id (``int``, *optional*):
                Unique identifier for a forum topic thread.

            can_stop (``bool``, *optional*):
                Pass True to show the user a button to stop further drafts. The bot then
                receives a :obj:`~pyrogram.types.MessageGenerationStopped` update when the
                user presses it.

            keep_on_stop (``bool``, *optional*):
                Pass True to keep the draft in the chat when the button is pressed. The draft
                still disappears after a short time or as soon as the bot sends a message, so
                call :meth:`~pyrogram.Client.send_message` to preserve it.

        Returns:
            ``bool``: On success, True is returned.

        .. note::

            The draft is ephemeral: clients drop it after ``message_typing_draft_ttl`` seconds
            (30 by default, server-configured) or as soon as a real message arrives, so call
            :meth:`~pyrogram.Client.send_message` to persist the result. Throttle the stream:
            setTyping is rate-limited to 20 calls per 5s and 40 per 30s per peer.

        Example:
            .. code-block:: python

                draft_id = app.rnd_id()

                for i, word in enumerate(words):
                    await app.send_message_draft(chat_id, draft_id, " ".join(words[:i + 1]))
                    await asyncio.sleep(0.33)

                await app.send_message(chat_id, text)
        """
        message, message_entities = (
            await utils.parse_text_entities(self, text, parse_mode, entities)
        ).values()

        return await self.invoke(
            raw.functions.messages.SetTyping(
                peer=await self.resolve_peer(chat_id),
                action=raw.types.SendMessageTextDraftAction(
                    random_id=draft_id,
                    text=raw.types.TextWithEntities(
                        text=message,
                        entities=message_entities or [],
                    ),
                    can_stop=can_stop,
                    keep_on_stop=keep_on_stop,
                ),
                top_msg_id=message_thread_id,
            )
        )
