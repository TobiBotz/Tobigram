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

import pyrogram
from pyrogram import raw, types

from ..object import Object


def _sanitize_rich_text(rt: raw.base.RichText | None) -> raw.base.RichText | None:
    if rt is None:
        return None

    # Unwrap server-only auto-detected entity tags to their inner RichText
    if isinstance(
        rt,
        (
            raw.types.TextHashtag,
            raw.types.TextMention,
            raw.types.TextBotCommand,
            raw.types.TextCashtag,
            raw.types.TextAutoUrl,
            raw.types.TextAutoEmail,
            raw.types.TextAutoPhone,
            raw.types.TextBankCard,
        ),
    ):
        return _sanitize_rich_text(rt.text)

    if isinstance(rt, raw.types.TextConcat):
        return raw.types.TextConcat(texts=[_sanitize_rich_text(t) for t in rt.texts])

    if isinstance(
        rt,
        (
            raw.types.TextBold,
            raw.types.TextItalic,
            raw.types.TextUnderline,
            raw.types.TextStrike,
            raw.types.TextFixed,
            raw.types.TextSubscript,
            raw.types.TextSuperscript,
            raw.types.TextMarked,
            raw.types.TextSpoiler,
        ),
    ):
        rt_type = type(rt)
        return rt_type(text=_sanitize_rich_text(rt.text))

    if isinstance(rt, raw.types.TextUrl):
        return raw.types.TextUrl(
            text=_sanitize_rich_text(rt.text),
            url=rt.url,
            webpage_id=rt.webpage_id,
        )

    if isinstance(rt, raw.types.TextButton):
        return raw.types.TextButton(
            text=_sanitize_rich_text(rt.text),
            type=rt.type,
            style=rt.style,
        )

    if isinstance(rt, raw.types.TextAnchor):
        return raw.types.TextAnchor(
            text=_sanitize_rich_text(rt.text),
            name=rt.name,
        )

    if isinstance(rt, raw.types.TextEmail):
        return raw.types.TextEmail(
            text=_sanitize_rich_text(rt.text),
            email=rt.email,
        )

    if isinstance(rt, raw.types.TextPhone):
        return raw.types.TextPhone(
            text=_sanitize_rich_text(rt.text),
            phone=rt.phone,
        )

    return rt


def _sanitize_caption(cap: raw.types.PageCaption | None) -> raw.types.PageCaption | None:
    if cap is None:
        return None
    if isinstance(cap, raw.types.PageCaption):
        return raw.types.PageCaption(
            text=_sanitize_rich_text(cap.text) or raw.types.TextEmpty(),
            credit=_sanitize_rich_text(cap.credit) or raw.types.TextEmpty(),
        )
    return cap


def _sanitize_list_item(item: raw.base.PageListItem) -> raw.base.PageListItem:
    if isinstance(item, raw.types.PageListItemText):
        return raw.types.PageListItemText(
            text=_sanitize_rich_text(item.text) or raw.types.TextEmpty()
        )
    if isinstance(item, raw.types.PageListItemBlocks):
        return raw.types.PageListItemBlocks(blocks=[_sanitize_block(b) for b in item.blocks])
    return item


def _sanitize_ordered_list_item(
    item: raw.base.PageListOrderedItem,
) -> raw.base.PageListOrderedItem:
    if isinstance(item, raw.types.PageListOrderedItemText):
        return raw.types.PageListOrderedItemText(
            num=item.num,
            text=_sanitize_rich_text(item.text) or raw.types.TextEmpty(),
        )
    if isinstance(item, raw.types.PageListOrderedItemBlocks):
        return raw.types.PageListOrderedItemBlocks(
            num=item.num,
            blocks=[_sanitize_block(b) for b in item.blocks],
        )
    return item


def _sanitize_block(block: raw.base.PageBlock) -> raw.base.PageBlock:
    if isinstance(block, raw.types.PageBlockParagraph):
        return raw.types.PageBlockParagraph(
            text=_sanitize_rich_text(block.text) or raw.types.TextEmpty()
        )

    if isinstance(
        block,
        (
            raw.types.PageBlockHeading1,
            raw.types.PageBlockHeading2,
            raw.types.PageBlockHeading3,
            raw.types.PageBlockHeading4,
            raw.types.PageBlockHeading5,
            raw.types.PageBlockHeading6,
            raw.types.PageBlockTitle,
            raw.types.PageBlockSubtitle,
            raw.types.PageBlockHeader,
            raw.types.PageBlockSubheader,
            raw.types.PageBlockFooter,
            raw.types.PageBlockPreformatted,
            raw.types.PageBlockKicker,
            raw.types.PageBlockThinking,
        ),
    ):
        b_type = type(block)
        return b_type(text=_sanitize_rich_text(block.text) or raw.types.TextEmpty())

    if isinstance(block, raw.types.PageBlockBlockquote):
        return raw.types.PageBlockBlockquote(
            text=_sanitize_rich_text(block.text) or raw.types.TextEmpty(),
            caption=_sanitize_rich_text(block.caption) or raw.types.TextEmpty(),
            collapsed=block.collapsed,
        )

    if isinstance(block, raw.types.PageBlockPullquote):
        return raw.types.PageBlockPullquote(
            text=_sanitize_rich_text(block.text) or raw.types.TextEmpty(),
            caption=_sanitize_rich_text(block.caption) or raw.types.TextEmpty(),
        )

    if isinstance(block, raw.types.PageBlockPhoto):
        return raw.types.PageBlockPhoto(
            photo_id=block.photo_id,
            caption=_sanitize_caption(block.caption),
            url=getattr(block, "url", None),
            webpage_id=getattr(block, "webpage_id", None),
            spoiler=block.spoiler,
        )

    if isinstance(block, raw.types.PageBlockVideo):
        return raw.types.PageBlockVideo(
            video_id=block.video_id,
            caption=_sanitize_caption(block.caption),
            autoplay=block.autoplay,
            loop=block.loop,
            spoiler=block.spoiler,
        )

    if isinstance(block, raw.types.PageBlockAudio):
        return raw.types.PageBlockAudio(
            audio_id=block.audio_id,
            caption=_sanitize_caption(block.caption),
        )

    if isinstance(block, raw.types.PageBlockDocument):
        return raw.types.PageBlockDocument(
            document_id=block.document_id,
            caption=_sanitize_caption(block.caption),
        )

    if isinstance(block, raw.types.PageBlockCollage):
        return raw.types.PageBlockCollage(
            items=[_sanitize_block(item) for item in block.items],
            caption=_sanitize_caption(block.caption),
        )

    if isinstance(block, raw.types.PageBlockSlideshow):
        return raw.types.PageBlockSlideshow(
            items=[_sanitize_block(item) for item in block.items],
            caption=_sanitize_caption(block.caption),
        )

    if isinstance(block, raw.types.PageBlockCover):
        return raw.types.PageBlockCover(cover=_sanitize_block(block.cover))

    if isinstance(block, raw.types.PageBlockBlockquoteBlocks):
        return raw.types.PageBlockBlockquoteBlocks(
            blocks=[_sanitize_block(b) for b in block.blocks],
            caption=_sanitize_rich_text(block.caption) or raw.types.TextEmpty(),
        )

    if isinstance(block, raw.types.PageBlockAuthorDate):
        return raw.types.PageBlockAuthorDate(
            author=_sanitize_rich_text(block.author) or raw.types.TextEmpty(),
            published_date=block.published_date,
        )

    if isinstance(block, raw.types.PageBlockList):
        return raw.types.PageBlockList(
            items=[_sanitize_list_item(item) for item in block.items],
        )

    if isinstance(block, raw.types.PageBlockOrderedList):
        return raw.types.PageBlockOrderedList(
            items=[_sanitize_ordered_list_item(item) for item in block.items],
            reversed=block.reversed,
            start=block.start,
            type=block.type,
        )

    if isinstance(block, raw.types.PageBlockDetails):
        return raw.types.PageBlockDetails(
            blocks=[_sanitize_block(b) for b in block.blocks],
            title=_sanitize_rich_text(block.title) or raw.types.TextEmpty(),
            open=block.open,
        )

    return block


class RichMessage(Object):
    """Rich formatted message.

    Parameters:
        blocks (List of :obj:`~pyrogram.types.RichBlock`):
            Content of the message.

        is_rtl (``bool``, *optional*):
            True, if the rich message must be shown right-to-left.

        is_partial (``bool``, *optional*):
            True, if these blocks are only the beginning of the message: a rich message too
            large to travel inline arrives truncated, and
            :meth:`~pyrogram.Client.get_rich_message` fetches the whole of it.
    """

    def __init__(
        self,
        *,
        blocks: list[types.RichBlock],
        is_rtl: bool | None = None,
        is_partial: bool | None = None,
    ):
        super().__init__()

        self.blocks = blocks
        self.is_rtl = is_rtl
        self.is_partial = is_partial
        self._raw: raw.types.RichMessage | None = None

    def to_input_rich_message(self) -> raw.base.InputRichMessage:
        """Convert this RichMessage into an InputRichMessage suitable for sending."""
        if hasattr(self, "_raw") and isinstance(self._raw, raw.types.RichMessage):
            photos = []
            if self._raw.photos:
                for p in self._raw.photos:
                    if isinstance(p, raw.types.Photo):
                        photos.append(
                            raw.types.InputPhoto(
                                id=p.id,
                                access_hash=p.access_hash,
                                file_reference=p.file_reference,
                            )
                        )
                    elif isinstance(p, raw.types.PhotoEmpty):
                        photos.append(raw.types.InputPhotoEmpty())

            documents = []
            if self._raw.documents:
                for d in self._raw.documents:
                    if isinstance(d, raw.types.Document):
                        documents.append(
                            raw.types.InputDocument(
                                id=d.id,
                                access_hash=d.access_hash,
                                file_reference=d.file_reference,
                            )
                        )
                    elif isinstance(d, raw.types.DocumentEmpty):
                        documents.append(raw.types.InputDocumentEmpty())

            cleaned_blocks = [_sanitize_block(b) for b in self._raw.blocks]

            return raw.types.InputRichMessage(
                blocks=cleaned_blocks,
                rtl=self._raw.rtl,
                photos=photos or None,
                documents=documents or None,
            )

        raise ValueError(
            "Cannot convert RichMessage without raw backing data into InputRichMessage"
        )

    def write(self) -> raw.base.InputRichMessage:
        return self.to_input_rich_message()

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        rich_message: raw.types.RichMessage,
        users: dict[int, raw.base.User] = {},
        chats: dict[int, raw.base.Chat] = {},
    ) -> RichMessage:
        if isinstance(rich_message, raw.types.RichMessage):
            photos = {photo.id: photo for photo in rich_message.photos}
            documents = {document.id: document for document in rich_message.documents}

            parsed = RichMessage(
                blocks=types.List(
                    [
                        await types.RichBlock._parse(
                            client,
                            block,
                            photos,
                            documents,
                            users,
                            chats,
                        )
                        for block in rich_message.blocks
                    ]
                ),
                is_rtl=rich_message.rtl,
                is_partial=rich_message.part,
            )
            parsed._raw = rich_message
            return parsed
