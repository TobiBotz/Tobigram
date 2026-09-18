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

import logging
import os
import re
from collections.abc import Callable
from datetime import datetime
from typing import BinaryIO

log = logging.getLogger(__name__)

import pyrogram
from pyrogram import types, utils
from pyrogram.file_id import PHOTO_TYPES, FileId, FileType

DEFAULT_DOWNLOAD_DIR = "downloads/"
STORY_MEDIA = ("photo", "video")


def safe_file_name(file_name: str) -> str:
    if not file_name:
        return ""

    file_name = os.path.basename(file_name.replace("\\", "/")).replace("\x00", "")

    if file_name in (".", ".."):
        return ""

    return file_name


def story_media(story: types.Story):
    media_type = getattr(story, "media", None)
    kind = getattr(media_type, "value", media_type)

    if isinstance(kind, str):
        media = getattr(story, kind, None)

        if media is not None:
            return media

    for kind in STORY_MEDIA:
        media = getattr(story, kind, None)

        if media is not None:
            return media

    return None


def purchased_paid_media(paid_media_info: types.PaidMediaInfo) -> list | None:
    media = getattr(paid_media_info, "media", None)

    if not media or isinstance(media[0], types.PaidMediaPreview):
        return None

    return media


def save_inline_thumbnail(
    client: pyrogram.Client,
    message: types.StrippedThumbnail | types.PaidMediaPreview,
    file_name: str,
    in_memory: bool,
) -> str | BinaryIO:
    if isinstance(message, types.StrippedThumbnail):
        data = message.data
    else:
        data = getattr(getattr(message, "thumbnail", None), "data", None)

    if not data:
        raise ValueError("This message doesn't contain any downloadable media")

    thumbnail = utils.from_inline_bytes(utils.expand_inline_bytes(data))

    if in_memory:
        return thumbnail

    directory, name = os.path.split(file_name)
    name = safe_file_name(name) or thumbnail.name

    if not os.path.isabs(directory):
        directory = client.workdir / (directory or DEFAULT_DOWNLOAD_DIR)

    os.makedirs(directory, exist_ok=True)
    file_path = os.path.abspath(re.sub(r"\\", "/", os.path.join(directory, name)))

    with open(file_path, "wb") as file:
        file.write(thumbnail.getbuffer())

    return file_path


async def download_paid_media(
    client: pyrogram.Client,
    media: list,
    file_name: str,
    in_memory: bool,
    block: bool,
    progress: Callable | None,
    progress_args: tuple,
) -> list[str | BinaryIO] | None:
    directory, name = os.path.split(file_name)
    results = []

    for index, item in enumerate(media):
        item_name = name

        if name and len(media) > 1:
            stem, extension = os.path.splitext(name)
            item_name = f"{stem}_{index + 1}{extension}"

        result = await client.download_media(
            item,
            file_name=os.path.join(directory, item_name),
            in_memory=in_memory,
            block=block,
            progress=progress,
            progress_args=progress_args,
        )

        if result is not None:
            results.append(result)

    return results or None


class DownloadMedia:
    async def download_media(
        self: pyrogram.Client,
        message: types.Message | str,
        file_name: str = DEFAULT_DOWNLOAD_DIR,
        in_memory: bool = False,
        block: bool = True,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> str | BinaryIO | None:
        """Download the media from a message.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            message (:obj:`~pyrogram.types.Message` | ``str``):
                Pass a Message containing the media, the media itself (message.audio, message.video, ...) or a file id
                as string.

            file_name (``str``, *optional*):
                A custom *file_name* to be used instead of the one provided by Telegram.
                By default, all files are downloaded in the *downloads* folder in your working directory.
                You can also specify a path for downloading files in a custom location: paths that end with "/"
                are considered directories. All non-existent folders will be created automatically.

            in_memory (``bool``, *optional*):
                Pass True to download the media in-memory.
                A binary file-like object with its attribute ".name" set will be returned.
                Defaults to False.

            block (``bool``, *optional*):
                Blocks the code execution until the file has been downloaded.
                Defaults to True.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            ``str`` | ``None`` | ``BinaryIO``: On success, the absolute path of the downloaded file is returned,
            otherwise, in case the download failed or was deliberately stopped with
            :meth:`~pyrogram.Client.stop_transmission`, None is returned.
            Otherwise, in case ``in_memory=True``, a binary file-like object with its attribute ".name" set is returned.

        Raises:
            ValueError: if the message doesn't contain any downloadable media

        Example:
            Download media to file

            .. code-block:: python

                # Download from Message
                await app.download_media(message)

                # Download from file id
                await app.download_media(message.photo.file_id)

                # Keep track of the progress while downloading
                async def progress(current, total):
                    print(f"{current * 100 / total:.1f}%")

                await app.download_media(message, progress=progress)

            Download media in-memory

            .. code-block:: python

                file = await app.download_media(message, in_memory=True)

                file_name = file.name
                file_bytes = bytes(file.getbuffer())
        """
        available_media = (
            "audio",
            "document",
            "photo",
            "sticker",
            "animation",
            "video",
            "voice",
            "video_note",
            "new_chat_photo",
            "paid_media",
        )

        media = None
        paid_media = None

        if isinstance(message, types.Message):
            story = getattr(message, "story", None) or getattr(message, "reply_to_story", None)

            if story is not None:
                media = story_media(story)
            else:
                for kind in available_media:
                    value = getattr(message, kind, None)

                    if value is None:
                        continue

                    if kind == "paid_media":
                        paid_media = purchased_paid_media(value)
                    else:
                        media = value

                    break
        elif isinstance(message, types.Story):
            media = story_media(message)
        elif isinstance(message, types.PaidMediaInfo):
            paid_media = purchased_paid_media(message)
        elif isinstance(message, (types.StrippedThumbnail, types.PaidMediaPreview)):
            return save_inline_thumbnail(self, message, file_name, in_memory)
        elif isinstance(message, types.ChatPhoto):
            media = message.big_file_id
        else:
            media = message

        if paid_media is not None:
            return await download_paid_media(
                self, paid_media, file_name, in_memory, block, progress, progress_args
            )

        if media is None:
            raise ValueError("This message doesn't contain any downloadable media")

        if isinstance(media, str):
            file_id_str = media
        else:
            file_id_str = media.file_id

        file_id_obj = FileId.decode(file_id_str)

        file_type = file_id_obj.file_type
        media_file_name = getattr(media, "file_name", "")
        file_size = getattr(media, "file_size", 0)
        mime_type = getattr(media, "mime_type", "")
        date = getattr(media, "date", None)

        directory, file_name = os.path.split(file_name)
        file_name = safe_file_name(file_name) or safe_file_name(media_file_name) or ""

        if not os.path.isabs(directory):
            directory = self.workdir / (directory or DEFAULT_DOWNLOAD_DIR)

        if not file_name:
            guessed_extension = self.guess_extension(mime_type)

            if file_type in PHOTO_TYPES:
                extension = ".jpg"
            elif file_type == FileType.VOICE:
                extension = guessed_extension or ".ogg"
            elif file_type in (FileType.VIDEO, FileType.ANIMATION, FileType.VIDEO_NOTE):
                extension = guessed_extension or ".mp4"
            elif file_type == FileType.DOCUMENT:
                extension = guessed_extension or ".zip"
            elif file_type == FileType.STICKER:
                extension = guessed_extension or ".webp"
            elif file_type == FileType.AUDIO:
                extension = guessed_extension or ".mp3"
            else:
                extension = ".unknown"

            file_name = "{}_{}_{}{}".format(
                FileType(file_id_obj.file_type).name.lower(),
                (date or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S"),
                self.rnd_id(),
                extension,
            )

        downloader = self.handle_download(
            (file_id_obj, directory, file_name, in_memory, file_size, progress, progress_args)
        )

        if block:
            return await downloader
        else:

            async def _run_download():
                try:
                    return await downloader
                except Exception as e:
                    log.exception("Background download failed: %s", e)

            utils.run_in_background(_run_download())
