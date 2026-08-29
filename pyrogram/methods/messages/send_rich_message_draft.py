from typing import Union, Optional

import pyrogram
from pyrogram import raw, types


class SendRichMessageDraft:
    async def send_rich_message_draft(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        draft_id: int,
        rich_message: "types.InputRichMessage",
        message_thread_id: Optional[int] = None,
        can_stop: Optional[bool] = None,
        keep_on_stop: Optional[bool] = None,
    ) -> bool:
        """Send a rich message draft action, allowing bots to stream partial rich messages.

        When generating a rich message progressively (e.g. during AI response streaming),
        this method shows the user a typing indicator with the partial rich message content.
        The block :obj:`~pyrogram.types.InputRichBlockThinking` — or, in the *html* and
        *markdown* forms, the custom tag ``<tg-thinking>Thinking...</tg-thinking>`` it
        corresponds to — may be used as a placeholder while waiting for content to be
        generated. Both are accepted only here, so they can't be received in messages.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target **private** chat.
                Drafts are streamed as a typing action and a group or channel refuses one
                with ``TEXTDRAFT_PEER_INVALID``.

            draft_id (``int``):
                Unique identifier of the draft; must be non-zero.
                Keep it constant for the whole generation, updates sharing an identifier are animated by clients.
                A different identifier does not restart the draft, it adds a second concurrent draft,
                and some clients collapse them into one.

            rich_message (:obj:`~pyrogram.types.InputRichMessage`):
                The partial rich message to stream.
                Use :obj:`~pyrogram.types.InputRichBlockThinking`, or the
                ``<tg-thinking>Thinking...</tg-thinking>`` tag in *html* and *markdown*,
                as a placeholder for content still being generated.

            message_thread_id (``int``, *optional*):
                Unique identifier for a forum topic thread.

            can_stop (``bool``, *optional*):
                Pass True to show the user a button to stop further drafts. The bot then
                receives a :obj:`~pyrogram.types.MessageGenerationStopped` update when the
                user presses it.

            keep_on_stop (``bool``, *optional*):
                Pass True to keep the draft in the chat when the button is pressed. The draft
                still disappears after a short time or as soon as the bot sends a message, so
                call :meth:`~pyrogram.Client.send_rich_message` to preserve it.

        Returns:
            ``bool``: On success, True is returned.

        .. note::

            The draft is ephemeral: clients drop it after ``message_typing_draft_ttl`` seconds
            (30 by default, server-configured) or as soon as a real message arrives, so call
            :meth:`~pyrogram.Client.send_rich_message` to persist the result. Throttle the stream:
            setTyping is rate-limited to 20 calls per 5s and 40 per 30s per peer.

        Example:
            .. code-block:: python

                draft_id = app.rnd_id()

                for i, word in enumerate(words):
                    await app.send_rich_message_draft(
                        chat_id, draft_id,
                        types.InputRichMessage(html=" ".join(words[:i + 1])),
                    )
                    await asyncio.sleep(0.33)

                await app.send_rich_message(chat_id, text)
        """
        return await self.invoke(
            raw.functions.messages.SetTyping(
                peer=await self.resolve_peer(chat_id),
                action=raw.types.InputSendMessageRichMessageDraftAction(
                    random_id=draft_id,
                    rich_message=rich_message.write(),
                    can_stop=can_stop,
                    keep_on_stop=keep_on_stop,
                ),
                top_msg_id=message_thread_id,
            )
        )
