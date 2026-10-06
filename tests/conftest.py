import os

import pytest

from pyrogram.session.internals import MsgId


@pytest.fixture(scope="session")
def auth_key():
    return os.urandom(256)


@pytest.fixture(scope="session")
def session_id():
    return os.urandom(8)


@pytest.fixture(scope="session")
def auth_key_id(auth_key):
    from hashlib import sha1

    return sha1(auth_key).digest()[-8:]


@pytest.fixture
def msg_id():
    return MsgId()
@pytest.fixture(autouse=True)
def fresh_msg_id_clock():
    from pyrogram.session.internals.msg_id import _MsgIdGenerator

    saved = {
        k: getattr(_MsgIdGenerator, k)
        for k in ("_last_msg_id", "_base_wall", "_base_mono", "time_offset")
    }
    yield
    for k, v in saved.items():
        setattr(_MsgIdGenerator, k, v)

