from typing import Union, Optional

import pyrogram
from pyrogram import raw


class SendRichMessageDraft:
    async def send_rich_message_draft(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        rich_message: "raw.types.RichMessage",
    ) -> bool:
        """Send a rich message draft action, allowing bots to stream partial rich messages.

        When generating a rich message progressively (e.g. during AI response streaming),
        this method shows the user a typing indicator with the partial rich message content.
        The block :obj:`~pyrogram.types.RichBlockThinking` may be used as a placeholder
        while waiting for content to be generated.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            rich_message (:obj:`~pyrogram.raw.types.RichMessage`):
                The partial rich message to show as a draft action.
                Must contain the blocks generated so far.
                Use :obj:`~pyrogram.types.RichBlockThinking` as a placeholder
                for blocks that are still being generated.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                from pyrogram.raw.types import (
                    RichMessage, PageBlockParagraph, TextBold, TextPlain
                )

                # Send a partial rich message draft
                await app.send_rich_message_draft(
                    chat_id,
                    RichMessage(
                        blocks=[
                            PageBlockParagraph(
                                text=TextBold(text="Hello ")
                            ),
                        ],
                        photos=[],
                        documents=[],
                        part=1,
                    )
                )
        """
        return await self.invoke(
            raw.functions.messages.SetTyping(
                peer=await self.resolve_peer(chat_id),
                action=raw.types.SendMessageRichMessageDraftAction(
                    random_id=self.rnd_id(),
                    rich_message=rich_message,
                ),
            )
        )