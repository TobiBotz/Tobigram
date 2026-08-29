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

from typing import List, Optional, Union, TYPE_CHECKING

from pyrogram import raw

from ..object import Object

if TYPE_CHECKING:
    from .input_rich_block import InputRichBlock
    from .input_rich_message_media import InputRichMessageMedia


class InputRichMessage(Object):
    """Describes a rich message to create.

    Exactly one of *html*, *markdown* or *blocks* must be provided: if more than one is set,
    the first one in that order is used and the others are ignored, and if none is set a
    ``ValueError`` is raised when the message is sent.

    Parameters:
        html (``str``, *optional*):
            Content of the rich message to send described using HTML formatting.
            See `rich message formatting options <https://core.telegram.org/bots/api#rich-message-formatting-options>`__ for more details.

        markdown (``str``, *optional*):
            Content of the rich message to send described using Markdown formatting.
            See `rich message formatting options <https://core.telegram.org/bots/api#rich-message-formatting-options>`__ for more details.

        is_rtl (``bool``, *optional*):
            Pass *True* if the rich message must be shown right-to-left.

        skip_entity_detection (``bool``, *optional*):
            Pass *True* to skip automatic detection of entities
            (e.g., URLs, email addresses, username mentions, hashtags, cashtags, bot commands, or phone numbers) in the text.

        blocks (List of :obj:`~pyrogram.types.InputRichBlock`, *optional*):
            List of blocks that define the rich message content.
            See `rich message formatting options <https://core.telegram.org/bots/api#rich-message-formatting-options>`__ for more details.

        media (:obj:`~pyrogram.types.InputRichMessageMedia` | List of :obj:`~pyrogram.types.InputRichMessageMedia`, *optional*):
            Media the message refers to. With *html* or *markdown*, each entry needs an
            ``id`` and is referred to from the text as ``tg://photo?id=``,
            ``tg://video?id=``, ``tg://document?id=`` or ``tg://audio?id=``. With *blocks*, the entries carry the
            photo, document and user vectors the blocks index into.
    """

    def __init__(
        self,
        html: Optional[str] = None,
        markdown: Optional[str] = None,
        is_rtl: Optional[bool] = None,
        skip_entity_detection: Optional[bool] = None,
        blocks: Optional[List["InputRichBlock"]] = None,
        media: Optional[Union["InputRichMessageMedia", List["InputRichMessageMedia"]]] = None,
    ):
        super().__init__()

        self.html = html
        self.markdown = markdown
        self.is_rtl = is_rtl
        self.skip_entity_detection = skip_entity_detection
        self.blocks = blocks
        self.media = media

    @property
    def _media_list(self) -> List["InputRichMessageMedia"]:
        if self.media is None:
            return []

        return list(self.media) if isinstance(self.media, (list, tuple)) else [self.media]

    def write_files(self) -> Optional[List["raw.base.InputRichFile"]]:
        """Return the ``files`` vector html and markdown rich messages carry."""
        files = [media.write_file() for media in self._media_list if media.id is not None]

        return files or None

    def write(self) -> "raw.base.InputRichMessage":
        if self.html:
            input_rich_message = raw.types.InputRichMessageHTML(
                html=self.html,
                rtl=self.is_rtl,
                noautolink=self.skip_entity_detection,
                files=self.write_files()
            )
        elif self.markdown:
            input_rich_message = raw.types.InputRichMessageMarkdown(
                markdown=self.markdown,
                rtl=self.is_rtl,
                noautolink=self.skip_entity_detection,
                files=self.write_files()
            )
        elif self.blocks:
            photos, documents, users = [], [], []

            for media in self._media_list:
                entry_photos, entry_documents, entry_users = media.write()

                photos.extend(entry_photos or ())
                documents.extend(entry_documents or ())
                users.extend(entry_users or ())

            input_rich_message = raw.types.InputRichMessage(
                blocks=[block.write() for block in self.blocks],
                rtl=self.is_rtl,
                noautolink=self.skip_entity_detection,
                photos=photos or None,
                documents=documents or None,
                users=users or None,
            )
        else:
            raise ValueError(
                "You must provide html, markdown or blocks in the rich message"
            )

        return input_rich_message

