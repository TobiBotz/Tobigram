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

"""How much work one update costs, counted rather than timed.

`Message._parse` runs for every message a client receives and is the largest
per-update cost there is — several times the raw deserialise. Most of what it
used to spend went on sub-parsers called with a field that was already `None`,
each of which cost a call and a dict lookup to hand `None` straight back.

Counting calls is exact where timing is not: a wasted one changes the count by
one whatever else the machine is doing.
"""

import inspect
from collections import Counter
from unittest.mock import Mock

import pytest

from pyrogram import raw, types

# what an ordinary text message in a channel legitimately needs: itself, the
# sender, the chat, their verification badges and its two entities
CALL_BUDGET = 12
NONE_BUDGET = 3


def _user(uid=1):
    return raw.types.User(
        id=uid, first_name="U", usernames=[], restriction_reason=[], access_hash=1
    )


def _channel(cid=100):
    return raw.types.Channel(
        id=cid,
        title="C",
        photo=raw.types.ChatPhotoEmpty(),
        date=0,
        access_hash=1,
        usernames=[],
        restriction_reason=[],
    )


def _message():
    return raw.types.Message(
        id=1,
        peer_id=raw.types.PeerChannel(channel_id=100),
        from_id=raw.types.PeerUser(user_id=1),
        date=1700000000,
        restriction_reason=[],
        message="hello",
        entities=[
            raw.types.MessageEntityBold(offset=0, length=5),
        ],
    )


def _client():
    client = Mock()
    client.me = Mock(id=999, is_bot=True, is_premium=False)
    client.message_cache = {}
    client.parse_mode = None

    return client


@pytest.fixture
def counted(monkeypatch):
    """Every types.*._parse* wrapped, so the calls one parse makes can be counted."""

    calls, nones = Counter(), Counter()

    for name in dir(types):
        cls = getattr(types, name)

        if not isinstance(cls, type):
            continue

        for attr in dir(cls):
            if not attr.startswith("_parse"):
                continue

            static = inspect.getattr_static(cls, attr, None)

            if not isinstance(static, staticmethod):
                continue

            inner = static.__func__
            key = f"{name}.{attr}"

            if inspect.iscoroutinefunction(inner):
                def wrap(inner=inner, key=key):
                    async def wrapper(*args, **kwargs):
                        calls[key] += 1
                        result = await inner(*args, **kwargs)

                        if result is None:
                            nones[key] += 1

                        return result

                    return wrapper
            else:
                def wrap(inner=inner, key=key):
                    def wrapper(*args, **kwargs):
                        calls[key] += 1
                        result = inner(*args, **kwargs)

                        if result is None:
                            nones[key] += 1

                        return result

                    return wrapper

            monkeypatch.setattr(cls, attr, staticmethod(wrap()), raising=False)

    return calls, nones


async def test_an_ordinary_message_makes_few_sub_parser_calls(counted):
    calls, _ = counted

    await types.Message._parse(_client(), _message(), {1: _user()}, {100: _channel()})

    total = sum(calls.values())

    assert total <= CALL_BUDGET, (
        f"parsing one message made {total} sub-parser calls: "
        f"{dict(calls.most_common())}"
    )


async def test_almost_none_of_them_answer_none(counted):
    """A parser handed a field that is already None costs a call to say so."""

    calls, nones = counted

    await types.Message._parse(_client(), _message(), {1: _user()}, {100: _channel()})

    wasted = sum(nones.values())

    assert wasted <= NONE_BUDGET, (
        f"{wasted} of {sum(calls.values())} sub-parser calls answered None: "
        f"{dict(nones.most_common())}"
    )


async def test_each_peer_is_parsed_once(counted):
    """from_user, sender_chat, via_bot and the rest used to re-parse the same peers."""

    calls, _ = counted

    await types.Message._parse(_client(), _message(), {1: _user()}, {100: _channel()})

    assert calls["User._parse"] == 1
    assert calls["Chat._parse"] == 1
    assert calls["Chat._parse_channel_chat"] == 1


async def test_the_message_still_parses_correctly(counted):
    """A budget met by parsing nothing would be no use."""

    parsed = await types.Message._parse(
        _client(), _message(), {1: _user()}, {100: _channel()}
    )

    assert parsed.id == 1
    assert parsed.from_user.id == 1
    assert parsed.chat.id == -1000000000100
    assert parsed.text == "hello"
    assert parsed.entities[0].type is not None
