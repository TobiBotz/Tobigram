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
def fresh_media_windows():
    # learned per auth key and DC for the life of the process; tests reuse keys
    from pyrogram.session import session

    session._media_windows.clear()
    yield
    session._media_windows.clear()
