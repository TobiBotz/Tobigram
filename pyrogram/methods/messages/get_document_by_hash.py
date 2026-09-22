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
from pyrogram import raw


class GetDocumentByHash:
    async def get_document_by_hash(
        self: pyrogram.Client,
        sha256: bytes,
        size: int,
        mime_type: str,
    ) -> raw.base.Document:
        """Get a document by its SHA256 hash.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            sha256 (``bytes``):
                The SHA256 hash of the document.

            size (``int``):
                The size of the document in bytes.

            mime_type (``str``):
                The MIME type of the document.

        Returns:
            :obj:`~pyrogram.raw.base.Document`: The document.

        Example:
            .. code-block:: python

                doc = await app.get_document_by_hash(sha256=b"...", size=12345, mime_type="image/png")
        """
        return await self.invoke(
            raw.functions.messages.GetDocumentByHash(
                sha256=sha256,
                size=size,
                mime_type=mime_type,
            )
        )
