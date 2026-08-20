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

import re
from typing import List, Optional, Union

from pyrogram import raw, utils

from ..object import Object

ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class InputRichMessageMedia(Object):
    """Describes media referenced in a rich message.

    There are two ways a rich message refers to media, and this object covers both.

    **By identifier**, for *html* and *markdown* content: set *id* and *media*, and refer
    to it from the text as ``tg://photo?id=<id>``, ``tg://video?id=<id>`` or
    ``tg://audio?id=<id>``.

    **By position**, for *blocks* content: set *photos*, *documents* and *users*, which
    the block objects index into (the ``photo_id`` of an
    :class:`~pyrogram.types.InputRichBlockPhoto` must match the ``id`` attribute of the
    corresponding :class:`~pyrogram.raw.types.InputPhoto`). MTProto has no identifiers on
    this side, which is why the two shapes differ.

    Parameters:
        id (``str``, *optional*):
            Unique identifier of the media used in a ``tg://photo?id=``, ``tg://video?id=``
            or ``tg://audio?id=`` link. 1-64 characters, only ``A-Z``, ``a-z``, ``0-9``,
            ``_`` and ``-`` are allowed.

        media (``str`` | :obj:`~pyrogram.raw.base.InputPhoto` | :obj:`~pyrogram.raw.base.InputDocument`, *optional*):
            The media the identifier refers to, as a file identifier of an already uploaded
            file or as an input photo or document. A rich message can only refer to media
            that already exists on Telegram, so a local path or an HTTP URL has to be
            uploaded first.

        photos (List of :obj:`~pyrogram.raw.base.InputPhoto`, *optional*):
            Photos referenced by blocks.

        documents (List of :obj:`~pyrogram.raw.base.InputDocument`, *optional*):
            Documents referenced by blocks.

        users (List of :obj:`~pyrogram.raw.base.InputUser`, *optional*):
            Users referenced by blocks.
    """

    def __init__(
        self,
        id: Optional[str] = None,
        media: Optional[Union[str, "raw.base.InputPhoto", "raw.base.InputDocument"]] = None,
        photos: Optional[List["raw.base.InputPhoto"]] = None,
        documents: Optional[List["raw.base.InputDocument"]] = None,
        users: Optional[List["raw.base.InputUser"]] = None,
    ):
        super().__init__()

        self.id = id
        self.media = media
        self.photos = photos
        self.documents = documents
        self.users = users

    def write(self) -> tuple:
        """Return the *(photos, documents, users)* vectors a block rich message carries."""
        photos = list(self.photos) if self.photos else []
        documents = list(self.documents) if self.documents else []

        if self.id is not None:
            file = self.write_file()

            if isinstance(file, raw.types.InputRichFilePhoto):
                photos.append(file.photo)
            else:
                documents.append(file.document)

        return (
            photos or self.photos,
            documents or self.documents,
            self.users,
        )

    def write_file(self) -> "raw.base.InputRichFile":
        """Return the ``InputRichFile`` an html or markdown rich message carries."""
        if not self.id:
            raise ValueError(
                "A media referenced from html or markdown needs an id to be "
                "referenced by: tg://photo?id=<id>"
            )

        if not ID_PATTERN.match(self.id):
            raise ValueError(
                f'Invalid media id "{self.id}": 1-64 characters of A-Z, a-z, 0-9, _ and - only'
            )

        media = self.media

        if isinstance(media, str):
            media = utils.get_input_media_from_file_id(media)

        if isinstance(media, (raw.types.InputMediaPhoto, raw.types.InputMediaDocument)):
            media = media.id

        if isinstance(media, raw.types.InputPhoto):
            return raw.types.InputRichFilePhoto(id=self.id, photo=media)

        if isinstance(media, raw.types.InputDocument):
            return raw.types.InputRichFileDocument(id=self.id, document=media)

        raise ValueError(
            "A rich message can only refer to media that already exists on Telegram. "
            f'Pass a file identifier, an InputPhoto or an InputDocument, not "{type(media).__name__}"'
        )
