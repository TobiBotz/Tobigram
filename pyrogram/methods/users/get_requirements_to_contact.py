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

from collections.abc import Iterable
import pyrogram
from pyrogram import raw, utils


class GetRequirementsToContact:
    async def get_requirements_to_contact(
        self: pyrogram.Client,
        user_ids: int | str | Iterable[int | str],
    ) -> list[raw.base.RequirementToContact]:
        """Check whether we can write to the specified users.

        Used to implement bulk checks for Premium-only messages and paid messages.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_ids (``int`` | ``str`` | Iterable of ``int`` or ``str``):
                A list of User identifiers (id or username) or a single user id/username.

        Returns:
            List of :obj:`~pyrogram.raw.base.RequirementToContact`: List of requirements to contact.

        Example:
            .. code-block:: python

                requirements = await app.get_requirements_to_contact(user_id)
        """
        is_iterable = not isinstance(user_ids, (int, str))
        ids = list(user_ids) if is_iterable else [user_ids]
        input_users = [utils.get_input_user(await self.resolve_peer(u)) for u in ids]
        return await self.invoke(
            raw.functions.users.GetRequirementsToContact(
                id=input_users,
            )
        )
