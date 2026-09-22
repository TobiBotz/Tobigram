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


class ExportLoginToken:
    async def export_login_token(
        self: pyrogram.Client,
        except_ids: list[int] | None = None,
        api_id: int | None = None,
        api_hash: str | None = None,
    ) -> raw.base.auth.LoginToken:
        """Generate a login token for login via QR code.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            except_ids (List of ``int``, *optional*):
                List of already logged-in user IDs.

            api_id (``int``, *optional*):
                Application identifier. Defaults to the client's api_id.

            api_hash (``str``, *optional*):
                Application identifier hash. Defaults to the client's api_hash.

        Returns:
            :obj:`~pyrogram.raw.base.auth.LoginToken`: The login token object.

        Example:
            .. code-block:: python

                token = await app.export_login_token()
        """
        return await self.invoke(
            raw.functions.auth.ExportLoginToken(
                api_id=api_id or self.api_id,
                api_hash=api_hash or self.api_hash,
                except_ids=except_ids or [],
            )
        )
