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

from typing import Any

import pyrogram
from pyrogram import enums, raw, utils
from pyrogram.file_id import FileType


class ReportProfilePhoto:
    async def report_profile_photo(
        self: pyrogram.Client,
        chat_id: int | str,
        photo: Any,
        reason: enums.ReportReason | raw.base.ReportReason | str = enums.ReportReason.SPAM,
        message: str = "",
    ) -> bool:
        """Report a profile photo of a user or channel for rule violations.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat/user.

            photo (``str`` | :obj:`~pyrogram.types.Photo` | :obj:`~pyrogram.types.ChatPhoto` | :obj:`~pyrogram.raw.base.InputPhoto`):
                Target profile photo, file identifier as string, Photo object, or raw InputPhoto.

            reason (:obj:`~pyrogram.enums.ReportReason` | ``str``, *optional*):
                The reason for reporting. Defaults to :obj:`~pyrogram.enums.ReportReason.SPAM`.

            message (``str``, *optional*):
                Additional explanatory text or details about the report. Defaults to "" (empty string).

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                from pyrogram.enums import ReportReason

                # Report a user's inappropriate profile photo
                await app.report_profile_photo(user_id, photo, ReportReason.PORNOGRAPHY)
        """
        peer = await self.resolve_peer(chat_id)
        parsed_reason = utils.parse_report_reason(reason)

        if isinstance(photo, (raw.types.InputPhoto, raw.types.InputPhotoEmpty)):
            input_photo = photo
        elif isinstance(photo, str):
            input_photo = utils.get_input_media_from_file_id(photo, FileType.PHOTO).id
        elif hasattr(photo, "file_id"):
            input_photo = utils.get_input_media_from_file_id(photo.file_id, FileType.PHOTO).id
        elif isinstance(photo, int):
            input_photo = raw.types.InputPhoto(id=photo, access_hash=0, file_reference=b"")
        else:
            raise ValueError(f"Invalid photo parameter: {photo!r}")

        return bool(
            await self.invoke(
                raw.functions.account.ReportProfilePhoto(
                    peer=peer,
                    photo_id=input_photo,
                    reason=parsed_reason,
                    message=message,
                )
            )
        )
