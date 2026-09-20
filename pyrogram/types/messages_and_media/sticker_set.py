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


class StickerSet(Object):
    """A sticker set.

    Parameters:
        id (``int``):
            Identifier of the sticker set.

        access_hash (``int``):
            Access hash of the sticker set.

        title (``str``):
            Title of the sticker set.

        short_name (``str``):
            Short name of the sticker set.

        count (``int``):
            Total number of stickers in this sticker set.

        stickers (List of :obj:`~pyrogram.types.Sticker`):
            List of stickers in this sticker set.

        is_animated (``bool``):
            True, if the sticker set is animated (TGS format).

        is_video (``bool``):
            True, if the sticker set is video (WebM format).

        is_emojis (``bool``):
            True, if this is a custom emoji sticker set.

        is_masks (``bool``):
            True, if this is a mask sticker set.

        is_archived (``bool``):
            True, if this sticker set has been archived.

        is_official (``bool``):
            True, if this sticker set is official (created by Telegram).

        thumbnail (:obj:`~pyrogram.types.Thumbnail`, *optional*):
            Sticker set thumbnail, if any.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        id: int,
        access_hash: int,
        title: str,
        short_name: str,
        count: int,
        stickers: list[types.Sticker] | None = None,
        is_animated: bool = False,
        is_video: bool = False,
        is_emojis: bool = False,
        is_masks: bool = False,
        is_archived: bool = False,
        is_official: bool = False,
        thumbnail: types.Thumbnail | None = None,
    ) -> None:
        super().__init__(client)

        self.id = id
        self.access_hash = access_hash
        self.title = title
        self.short_name = short_name
        self.count = count
        self.stickers = stickers or []
        self.is_animated = is_animated
        self.is_video = is_video
        self.is_emojis = is_emojis
        self.is_masks = is_masks
        self.is_archived = is_archived
        self.is_official = is_official
        self.thumbnail = thumbnail

    @classmethod
    async def _parse(
        cls,
        client: pyrogram.Client,
        sticker_set: raw.base.messages.StickerSet,
    ) -> StickerSet:
        if isinstance(sticker_set, raw.types.messages.StickerSetNotModified):
            return None

        raw_set = sticker_set.set
        documents = getattr(sticker_set, "documents", None)
        if documents is None:
            if hasattr(sticker_set, "covers"):
                documents = sticker_set.covers
            elif hasattr(sticker_set, "cover"):
                documents = [sticker_set.cover]
            else:
                documents = []

        stickers = types.List(
            [
                await types.Sticker._parse(client, doc, {type(a): a for a in doc.attributes})
                for doc in documents
            ]
        )

        thumbnail = None
        if getattr(raw_set, "thumbs", None):
            thumbnail = types.Thumbnail._parse(client, raw_set.thumbs)

        return cls(
            client=client,
            id=raw_set.id,
            access_hash=raw_set.access_hash,
            title=raw_set.title,
            short_name=raw_set.short_name,
            count=getattr(raw_set, "count", len(stickers)),
            stickers=stickers,
            is_animated=getattr(raw_set, "animated", False)
            or any(getattr(s, "is_animated", False) for s in stickers),
            is_video=getattr(raw_set, "videos", False)
            or any(getattr(s, "is_video", False) for s in stickers),
            is_emojis=getattr(raw_set, "emojis", False),
            is_masks=getattr(raw_set, "masks", False),
            is_archived=getattr(raw_set, "archived", False),
            is_official=getattr(raw_set, "official", False),
            thumbnail=thumbnail,
        )
