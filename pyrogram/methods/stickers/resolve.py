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

import os
import re
from typing import BinaryIO

import pyrogram
from pyrogram import raw, types, utils
from pyrogram.file_id import FileId


async def resolve_sticker_doc(
    client: pyrogram.Client,
    media: str | BinaryIO | types.Sticker | raw.base.InputDocument,
    emoji: str = "😀",
) -> raw.base.InputDocument:
    if isinstance(media, raw.base.InputDocument):
        return media

    if isinstance(media, types.Sticker):
        media = media.file_id

    if isinstance(media, str):
        if (
            not os.path.exists(media)
            and not re.match(r"^https?://", media)
            and "/" not in media
            and "\\" not in media
        ):
            try:
                decoded = FileId.decode(media)
                return raw.types.InputDocument(
                    id=decoded.media_id,
                    access_hash=decoded.access_hash,
                    file_reference=decoded.file_reference or b"",
                )
            except Exception:
                pass

    uploaded_file = await client.save_file(media)
    file_name = utils.get_file_name(media, fallback="sticker.webp")
    lower = file_name.lower()
    if lower.endswith(".tgs"):
        mime_type = "application/x-tgsticker"
    elif lower.endswith(".webm"):
        mime_type = "video/webm"
    elif lower.endswith(".png"):
        mime_type = "image/png"
    else:
        mime_type = client.guess_mime_type(file_name) or "image/webp"

    attributes = [
        raw.types.DocumentAttributeFilename(file_name=file_name),
        raw.types.DocumentAttributeSticker(
            alt=emoji or "",
            stickerset=raw.types.InputStickerSetEmpty(),
        ),
    ]

    uploaded = await client.invoke(
        raw.functions.messages.UploadMedia(
            peer=raw.types.InputPeerSelf(),
            media=raw.types.InputMediaUploadedDocument(
                file=uploaded_file,
                mime_type=mime_type,
                attributes=attributes,
            ),
        )
    )

    return raw.types.InputDocument(
        id=uploaded.document.id,
        access_hash=uploaded.document.access_hash,
        file_reference=uploaded.document.file_reference,
    )


async def resolve_sticker_item(
    client: pyrogram.Client,
    sticker: types.InputSticker | str | BinaryIO | types.Sticker | raw.base.InputDocument,
    default_emoji: str = "😀",
) -> raw.types.InputStickerSetItem:
    if isinstance(sticker, types.InputSticker):
        media = sticker.sticker
        emoji = sticker.emoji or default_emoji
        keywords = sticker.keywords
        mask_coords = sticker.mask_coords
    else:
        media = sticker
        emoji = getattr(sticker, "emoji", None) or default_emoji
        keywords = None
        mask_coords = None

    if isinstance(mask_coords, types.MaskPosition):
        point_val = (
            mask_coords.point.value
            if hasattr(mask_coords.point, "value")
            else int(mask_coords.point)
        )
        mask_coords = raw.types.MaskCoords(
            n=point_val,
            x=mask_coords.x_shift,
            y=mask_coords.y_shift,
            zoom=mask_coords.scale,
        )

    doc = await resolve_sticker_doc(client, media, emoji=emoji)
    return raw.types.InputStickerSetItem(
        document=doc,
        emoji=emoji,
        keywords=keywords,
        mask_coords=mask_coords,
    )


def resolve_stickerset(
    stickerset: str | types.StickerSet | raw.base.InputStickerSet,
) -> raw.base.InputStickerSet:
    if isinstance(stickerset, raw.base.InputStickerSet):
        return stickerset

    if isinstance(stickerset, types.StickerSet):
        return raw.types.InputStickerSetID(id=stickerset.id, access_hash=stickerset.access_hash)

    if isinstance(stickerset, str):
        return raw.types.InputStickerSetShortName(short_name=stickerset)

    raise ValueError(f"Invalid sticker set identifier: {stickerset!r}")


async def resolve_thumb_doc(
    client: pyrogram.Client,
    thumb: str | BinaryIO | raw.base.InputDocument | None,
) -> raw.base.InputDocument | None:
    if thumb is None:
        return None

    if isinstance(thumb, raw.base.InputDocument):
        return thumb

    if (
        isinstance(thumb, str)
        and not os.path.exists(thumb)
        and "/" not in thumb
        and "\\" not in thumb
    ):
        try:
            decoded = FileId.decode(thumb)
            return raw.types.InputDocument(
                id=decoded.media_id,
                access_hash=decoded.access_hash,
                file_reference=decoded.file_reference or b"",
            )
        except Exception:
            pass

    uploaded_file = await client.save_file(thumb)
    file_name = utils.get_file_name(thumb, fallback="thumb.webp")
    uploaded = await client.invoke(
        raw.functions.messages.UploadMedia(
            peer=raw.types.InputPeerSelf(),
            media=raw.types.InputMediaUploadedDocument(
                file=uploaded_file,
                mime_type=client.guess_mime_type(file_name) or "image/webp",
                attributes=[raw.types.DocumentAttributeFilename(file_name=file_name)],
            ),
        )
    )

    return raw.types.InputDocument(
        id=uploaded.document.id,
        access_hash=uploaded.document.access_hash,
        file_reference=uploaded.document.file_reference,
    )
