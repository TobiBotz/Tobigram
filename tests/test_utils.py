from datetime import datetime, timedelta, timezone

import pytest

from pyrogram.utils import (
    ZERO_CHANNEL_ID,
    datetime_to_timestamp,
    get_channel_id,
    get_peer_id,
    get_peer_type,
    timestamp_to_datetime,
    zero_datetime,
)


class TestZeroDatetime:
    def test_returns_epoch(self):
        dt = zero_datetime()
        assert dt.year == 1970
        assert dt.month == 1
        assert dt.day == 1
        assert dt.tzinfo == timezone.utc


class TestTimestampToDatetime:
    def test_valid(self):
        ts = 1704067200
        dt = timestamp_to_datetime(ts)
        assert dt == datetime.fromtimestamp(ts)

    def test_none(self):
        assert timestamp_to_datetime(None) is None

    def test_zero(self):
        assert timestamp_to_datetime(0) is None

    def test_negative(self):
        ts = -1
        dt = timestamp_to_datetime(ts)
        assert dt == datetime.fromtimestamp(ts)


class TestDatetimeToTimestamp:
    def test_datetime_with_tz(self):
        dt = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        assert datetime_to_timestamp(dt) == 1704067200

    def test_datetime_naive(self):
        dt = datetime(2024, 1, 1, 0, 0, 0)
        assert datetime_to_timestamp(dt) == int(dt.timestamp())

    def test_timedelta(self):
        td = timedelta(hours=1)
        result = datetime_to_timestamp(td)
        expected = int((datetime.now() + td).timestamp())
        assert result == expected

    def test_none(self):
        assert datetime_to_timestamp(None) is None


class TestGetPeerId:
    def test_user_peer(self):
        from pyrogram.raw.types import PeerUser

        peer = PeerUser(user_id=12345)
        assert get_peer_id(peer) == 12345

    def test_chat_peer(self):
        from pyrogram.raw.types import PeerChat

        peer = PeerChat(chat_id=67890)
        assert get_peer_id(peer) == -67890

    def test_channel_peer(self):
        from pyrogram.raw.types import PeerChannel

        peer = PeerChannel(channel_id=11111)
        assert get_peer_id(peer) == ZERO_CHANNEL_ID - 11111

    def test_input_peer_user(self):
        from pyrogram.raw.types import InputPeerUser

        peer = InputPeerUser(user_id=222, access_hash=0)
        assert get_peer_id(peer) == 222

    def test_input_peer_chat(self):
        from pyrogram.raw.types import InputPeerChat

        peer = InputPeerChat(chat_id=333)
        assert get_peer_id(peer) == -333

    def test_input_peer_channel(self):
        from pyrogram.raw.types import InputPeerChannel

        peer = InputPeerChannel(channel_id=444, access_hash=0)
        assert get_peer_id(peer) == ZERO_CHANNEL_ID - 444

    def test_invalid_raises(self):
        class Fake:
            pass

        with pytest.raises(ValueError, match="Peer type invalid"):
            get_peer_id(Fake())


class TestGetPeerType:
    def test_user(self):
        assert get_peer_type(1) == "user"
        assert get_peer_type(123456789) == "user"
        assert get_peer_type((1 << 40) - 1) == "user"

    def test_chat(self):
        assert get_peer_type(-1) == "chat"
        assert get_peer_type(-999999999999) == "chat"

    def test_channel(self):
        assert get_peer_type(-1000000000001) == "channel"
        assert get_peer_type(-1500000000000) == "channel"

    def test_secret_chat(self):
        assert get_peer_type(-2000000000001) == "secret_chat"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Peer id invalid"):
            get_peer_type(0)

    def test_invalid_too_large_raises(self):
        with pytest.raises(ValueError, match="Peer id invalid"):
            get_peer_type((1 << 40) + 1)


class TestGetChannelId:
    def test_positive(self):
        assert get_channel_id(123) == ZERO_CHANNEL_ID - 123

    def test_negative(self):
        channel_id = -1999999999999
        assert get_channel_id(channel_id) == ZERO_CHANNEL_ID - channel_id

    def test_zero(self):
        assert get_channel_id(0) == ZERO_CHANNEL_ID
