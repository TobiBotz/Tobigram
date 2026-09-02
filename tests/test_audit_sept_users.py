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


def test_accepted_gift_types_only_disallows_what_was_set_to_false():
    written = types.AcceptedGiftTypes(limited_gifts=False).write()

    assert written.disallow_limited_stargifts is True
    assert not any((
        written.disallow_unlimited_stargifts,
        written.disallow_unique_stargifts,
        written.disallow_stargifts_from_channels,
        written.disallow_premium_gifts,
    )), "a field left as None is not a refusal"


async def test_update_birthday_refuses_a_partial_date_and_removes_on_no_arguments():
    from pyrogram.methods.users.update_birthday import UpdateBirthday

    class _Client(UpdateBirthday):
        sent = None

        async def invoke(self, query, *args, **kwargs):
            self.sent = query
            return True

    client = _Client()

    with pytest.raises(ValueError):
        await client.update_birthday(year=2000)

    assert client.sent is None, "a partial date must not reach the server as a removal"

    assert await client.update_birthday() is True
    assert client.sent.birthday is None

    await client.update_birthday(day=1, month=2)
    assert (client.sent.birthday.day, client.sent.birthday.month) == (1, 2)


async def test_set_profile_photo_without_a_file_is_refused_before_the_request():
    from pyrogram.methods.users.set_profile_photo import SetProfilePhoto

    class _Client(SetProfilePhoto):
        async def save_file(self, *args, **kwargs):
            raise AssertionError("nothing to upload")

        async def invoke(self, query, *args, **kwargs):
            raise AssertionError("an empty request must not go out")

    with pytest.raises(ValueError):
        await _Client().set_profile_photo()


def _bot_channel_client(chat_photo):
    class _Client:
        me = SimpleNamespace(is_bot=True)
        queries = []

        async def resolve_peer(self, chat_id):
            return raw.types.InputPeerChannel(channel_id=1, access_hash=0)

        async def invoke(self, query, *args, **kwargs):
            self.queries.append(query)

            if isinstance(query, raw.functions.channels.GetFullChannel):
                return SimpleNamespace(full_chat=SimpleNamespace(chat_photo=chat_photo))

            raise AssertionError(f"{query.QUALNAME} is user-only")

    return _Client()


async def test_a_bot_reads_a_channels_photo_from_the_full_chat(monkeypatch):
    from pyrogram.methods.users.get_chat_photos import GetChatPhotos
    from pyrogram.methods.users.get_chat_photos_count import GetChatPhotosCount

    photo = raw.types.Photo(
        id=1, access_hash=1, file_reference=b"", date=0, sizes=[], dc_id=2
    )
    parsed = SimpleNamespace(file_id="id", file_unique_id="current")

    monkeypatch.setattr(
        types.Photo, "_parse", staticmethod(lambda _c, p: parsed if p is photo else None)
    )

    client = _bot_channel_client(photo)
    got = [p async for p in GetChatPhotos.get_chat_photos(client, 1)]
    assert got == [parsed]
    assert await GetChatPhotosCount.get_chat_photos_count(client, 1) == 1

    client = _bot_channel_client(raw.types.PhotoEmpty(id=0))
    assert [p async for p in GetChatPhotos.get_chat_photos(client, 1)] == []
    assert await GetChatPhotosCount.get_chat_photos_count(client, 1) == 0
