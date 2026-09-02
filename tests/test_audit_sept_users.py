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
from types import SimpleNamespace

import pytest

from pyrogram import raw, types


def _user(user_id):
    return raw.types.User(
        id=user_id, first_name="U", usernames=[], restriction_reason=[], access_hash=1
    )


async def test_get_users_refuses_a_peer_that_is_not_a_user():
    from pyrogram.methods.users.get_users import GetUsers

    class _Client(GetUsers):
        async def resolve_peer(self, peer_id):
            if peer_id == "channel":
                return raw.types.InputPeerChannel(channel_id=1, access_hash=1)

            return raw.types.InputPeerUser(user_id=2, access_hash=1)

        async def invoke(self, query, *args, **kwargs):
            return [_user(p.user_id) for p in query.id]

    client = _Client()

    with pytest.raises(ValueError, match="channel"):
        await client.get_users("channel")

    with pytest.raises(ValueError):
        await client.get_users(["someone", "channel"])

    assert (await client.get_users("someone")).id == 2
