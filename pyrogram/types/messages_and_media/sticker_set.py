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

import inspect
from typing import Union

import pyrogram
from pyrogram import enums, raw, types

from ..object import Object


class StickerSet(Object):
    """This object represents a sticker set.

    Parameters:
        id (``int``):
            Unique identifier for this sticker set.

        name (``str``):
            Short name of the sticker set, used in t.me/addstickers/ links.

        title (``str``):
            Title of the sticker set.

        sticker_type (:obj:`~pyrogram.enums.StickerType`):
            Type of stickers in the set.

        stickers (List of :obj:`~pyrogram.types.Sticker`, *optional*):
            List of all set stickers.

        thumbs (List of :obj:`~pyrogram.types.Thumbnail`, *optional*):
            Sticker set thumbnail in the .WEBP, .TGS, or .WEBM format.

        is_owned (``bool``, *optional*):
            True, if the user is the owner of the sticker set.

        is_installed (``bool``, *optional*):
            True, if the sticker set is installed.

        is_archived (``bool``, *optional*):
            True, if the sticker set has been archived.

        is_official (``bool``, *optional*):
            True, if the sticker set is official.

        is_allowed_as_chat_emoji_status (``bool``, *optional*):
            True, if the sticker set is allowed to be used as chat emoji status.

        needs_repainting (``bool``, *optional*):
            True, if the sticker set needs to be repainted.

        raw (:obj:`~pyrogram.raw.base.StickerSet` | :obj:`~pyrogram.raw.base.messages.StickerSet`, *optional*):
            The raw object.
    """

    def __init__(
        self,
        *,
        id: int,
        name: str,
        title: str,
        sticker_type: "enums.StickerType",
        stickers: list["types.Sticker"] | None = None,
        thumbs: list["types.Thumbnail"] | None = None,
        is_owned: bool | None = None,
        is_installed: bool | None = None,
        is_archived: bool | None = None,
        is_official: bool | None = None,
        is_allowed_as_chat_emoji_status: bool | None = None,
        needs_repainting: bool | None = None,
        raw: Union["raw.types.StickerSet", "raw.types.messages.StickerSet"] | None = None,
    ):
        super().__init__()

        self.id = id
        self.name = name
        self.title = title
        self.sticker_type = sticker_type
        self.stickers = stickers
        self.thumbs = thumbs
        self.is_owned = is_owned
        self.is_installed = is_installed
        self.is_archived = is_archived
        self.is_official = is_official
        self.is_allowed_as_chat_emoji_status = is_allowed_as_chat_emoji_status
        self.needs_repainting = needs_repainting
        self.raw = raw

    @property
    def link(self) -> str:
        return f"https://t.me/addstickers/{self.name}"

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        sticker_set: Union["raw.types.StickerSet", "raw.types.messages.StickerSet"],
    ) -> "StickerSet":
        documents = None

        if isinstance(sticker_set, raw.types.messages.StickerSet):
            documents = sticker_set.documents
            _set = sticker_set.set
        elif isinstance(
            sticker_set,
            (
                raw.types.StickerSetCovered,
                raw.types.StickerSetMultiCovered,
                raw.types.StickerSetFullCovered,
            ),
        ):
            documents = (
                getattr(sticker_set, "documents", None)
                or getattr(sticker_set, "covers", None)
                or ([sticker_set.cover] if getattr(sticker_set, "cover", None) else None)
            )
            _set = sticker_set.set
        else:
            _set = sticker_set

        if _set.masks:
            sticker_type = enums.StickerType.MASK
        elif _set.emojis:
            sticker_type = enums.StickerType.CUSTOM_EMOJI
        else:
            sticker_type = enums.StickerType.REGULAR

        types.Sticker.cache[(_set.id, _set.access_hash)] = _set.short_name

        cache = getattr(client, "sticker_set_name_cache", None)
        if cache is not None:
            res = cache.set((_set.id, _set.access_hash), _set.short_name)
            if inspect.isawaitable(res):
                await res

        stickers = None
        thumbs = None

        if documents is not None:
            parsed_stickers = []
            for doc in documents:
                if isinstance(doc, raw.types.Document):
                    s = await types.Sticker._parse(
                        client, doc, {type(a): a for a in doc.attributes}
                    )
                    if s is not None:
                        parsed_stickers.append(s)
            stickers = types.List(parsed_stickers)

            thumb = next(
                (
                    d
                    for d in documents
                    if isinstance(d, raw.types.Document) and d.id == _set.thumb_document_id
                ),
                None,
            )

            if thumb is None and _set.thumb_document_id:
                r = await client.invoke(
                    raw.functions.messages.GetCustomEmojiDocuments(
                        document_id=[_set.thumb_document_id]
                    )
                )
                thumb = r[0] if r else None

            if thumb is None and documents:
                first_doc = next((d for d in documents if isinstance(d, raw.types.Document)), None)
                if first_doc is not None:
                    thumb = first_doc

            if thumb is not None:
                thumbs = types.Thumbnail._parse(client, thumb)

        return StickerSet(
            id=_set.id,
            name=_set.short_name,
            title=_set.title,
            sticker_type=sticker_type,
            stickers=stickers,
            thumbs=thumbs,
            is_owned=_set.creator,
            is_installed=bool(_set.installed_date),
            is_archived=_set.archived,
            is_official=_set.official,
            is_allowed_as_chat_emoji_status=_set.channel_emoji_status,
            needs_repainting=_set.text_color,
            raw=sticker_set,
        )
