import pytest

import pyrogram
from pyrogram import enums, raw, types, utils
from pyrogram.parser import Parser
from pyrogram.types.messages_and_media.rich_message import (
    _sanitize_block,
    _sanitize_list_item,
    _sanitize_ordered_list_item,
)


class FakeStorage:
    async def dc_id(self):
        return 2


class FakeClient:
    sleep_threshold = 10
    parse_mode = enums.ParseMode.DEFAULT

    def __init__(self):
        self.storage = FakeStorage()
        self.parser = Parser(self)
        self.sent = None
        self.invoked_kwargs = {}
        self.message_cache = {}
        self.topic_cache = {}
        self.fetch_topics = False
        self.me = None

    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerUser(user_id=777, access_hash=42)

    async def invoke(self, query, sleep_threshold=None, business_connection_id=None):
        self.sent = query
        self.invoked_kwargs = {
            "sleep_threshold": sleep_threshold,
            "business_connection_id": business_connection_id,
        }

        if isinstance(query, raw.functions.messages.GetArchivedStickers):
            return raw.types.messages.ArchivedStickers(count=0, sets=[])
        if isinstance(query, raw.functions.messages.SetInlineGameScore):
            return True
        if isinstance(query, raw.functions.messages.GetInlineGameHighScores):
            return raw.types.messages.HighScores(scores=[], users=[])
        if isinstance(query, raw.functions.payments.GetPaymentForm):
            from unittest.mock import Mock

            return Mock(form_id=987)
        if isinstance(query, raw.functions.payments.SendStarsForm):
            return raw.types.payments.PaymentResult(
                updates=raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0)
            )
        if isinstance(query, raw.functions.users.SetSecureValueErrors):
            return True

        return raw.types.Updates(
            updates=[
                raw.types.UpdateEditMessage(
                    message=raw.types.Message(
                        id=1,
                        peer_id=raw.types.PeerUser(user_id=777),
                        from_id=raw.types.PeerUser(user_id=777),
                        date=1700000000,
                        message="",
                        entities=[],
                    ),
                    pts=1,
                    pts_count=1,
                )
            ],
            users=[
                raw.types.User(
                    id=777,
                    first_name="User",
                    access_hash=42,
                )
            ],
            chats=[],
            date=0,
            seq=0,
        )

    edit_message_live_location = pyrogram.Client.edit_message_live_location
    stop_message_live_location = pyrogram.Client.stop_message_live_location
    set_business_account_gift_settings = pyrogram.Client.set_business_account_gift_settings
    get_archived_stickers = pyrogram.Client.get_archived_stickers
    set_game_score = pyrogram.Client.set_game_score
    get_game_high_scores = pyrogram.Client.get_game_high_scores
    gift_premium_subscription = pyrogram.Client.gift_premium_subscription
    set_passport_data_errors = pyrogram.Client.set_passport_data_errors
    set_secure_value_errors = pyrogram.Client.set_secure_value_errors


@pytest.fixture
def inline_message_id():
    return utils.pack_inline_message_id(
        raw.types.InputBotInlineMessageID(dc_id=2, id=10, access_hash=20)
    )


@pytest.fixture
def client():
    return FakeClient()


async def test_edit_message_live_location_chat(client):
    msg = await client.edit_message_live_location(
        chat_id=123,
        message_id=456,
        latitude=45.0,
        longitude=9.0,
        heading=180,
    )

    assert isinstance(client.sent, raw.functions.messages.EditMessage)
    assert client.sent.id == 456
    assert isinstance(client.sent.media, raw.types.InputMediaGeoLive)
    assert client.sent.media.geo_point.lat == 45.0
    assert client.sent.media.geo_point.long == 9.0
    assert client.sent.media.heading == 180
    assert client.sent.reply_markup is None
    assert isinstance(msg, types.Message)


async def test_edit_message_live_location_inline(client, inline_message_id):
    res = await client.edit_message_live_location(
        inline_message_id=inline_message_id,
        latitude=45.0,
        longitude=9.0,
    )

    assert isinstance(client.sent, raw.functions.messages.EditInlineBotMessage)
    assert client.sent.id.dc_id == 2
    assert client.sent.id.id == 10
    assert isinstance(client.sent.media, raw.types.InputMediaGeoLive)
    assert client.sent.media.geo_point.lat == 45.0
    assert client.sent.media.geo_point.long == 9.0
    assert res is not None


async def test_edit_message_live_location_reply_markup_none(client):
    await client.edit_message_live_location(
        chat_id=123,
        message_id=456,
        latitude=45.0,
        longitude=9.0,
        reply_markup=None,
    )

    assert isinstance(client.sent.reply_markup, raw.types.ReplyInlineMarkup)
    assert client.sent.reply_markup.rows == []


async def test_edit_message_live_location_validation(client):
    with pytest.raises(ValueError, match="Either \\(chat_id, message_id\\) or inline_message_id"):
        await client.edit_message_live_location(latitude=45.0, longitude=9.0)


async def test_stop_message_live_location_chat(client):
    msg = await client.stop_message_live_location(chat_id=123, message_id=456)

    assert isinstance(client.sent, raw.functions.messages.EditMessage)
    assert client.sent.id == 456
    assert isinstance(client.sent.media, raw.types.InputMediaGeoLive)
    assert client.sent.media.stopped is True
    assert isinstance(client.sent.media.geo_point, raw.types.InputGeoPointEmpty)
    assert isinstance(msg, types.Message)


async def test_stop_message_live_location_inline(client, inline_message_id):
    res = await client.stop_message_live_location(
        inline_message_id=inline_message_id,
        business_connection_id="bc_123",
    )

    assert isinstance(client.sent, raw.functions.messages.EditInlineBotMessage)
    assert client.sent.id.dc_id == 2
    assert client.sent.id.id == 10
    assert isinstance(client.sent.media, raw.types.InputMediaGeoLive)
    assert client.sent.media.stopped is True
    assert client.invoked_kwargs.get("business_connection_id") == "bc_123"
    assert res is not None


async def test_stop_message_live_location_reply_markup_none(client):
    await client.stop_message_live_location(
        chat_id=123,
        message_id=456,
        reply_markup=None,
    )

    assert isinstance(client.sent.reply_markup, raw.types.ReplyInlineMarkup)
    assert client.sent.reply_markup.rows == []


async def test_stop_message_live_location_validation(client):
    with pytest.raises(ValueError, match="Either \\(chat_id, message_id\\) or inline_message_id"):
        await client.stop_message_live_location()


async def test_set_business_account_gift_settings(client):
    await client.set_business_account_gift_settings(
        show_gift_button=True,
        accepted_gift_types=True,
        business_connection_id="biz_conn_99",
    )

    assert isinstance(client.sent, raw.functions.account.SetGlobalPrivacySettings)
    assert isinstance(client.sent.settings, raw.types.GlobalPrivacySettings)
    assert client.sent.settings.display_gifts_button is True
    assert client.sent.settings.disallowed_gifts is True
    assert client.invoked_kwargs.get("business_connection_id") == "biz_conn_99"


async def test_get_archived_stickers(client):
    archived = await client.get_archived_stickers(masks=True, emojis=False, limit=50)

    assert isinstance(client.sent, raw.functions.messages.GetArchivedStickers)
    assert client.sent.masks is True
    assert client.sent.emojis is False
    assert client.sent.limit == 50
    assert not hasattr(client.sent, "hash")
    assert isinstance(archived, raw.types.messages.ArchivedStickers)


async def test_set_game_score_chat(client):
    msg = await client.set_game_score(user_id=777, score=100, chat_id=123, message_id=456)

    assert isinstance(client.sent, raw.functions.messages.SetGameScore)
    assert client.sent.score == 100
    assert client.sent.id == 456
    assert isinstance(msg, types.Message)


async def test_set_game_score_inline(client, inline_message_id):
    res = await client.set_game_score(user_id=777, score=500, inline_message_id=inline_message_id)

    assert isinstance(client.sent, raw.functions.messages.SetInlineGameScore)
    assert client.sent.id.dc_id == 2
    assert client.sent.id.id == 10
    assert client.sent.score == 500
    assert res is True


async def test_get_game_high_scores_inline(client, inline_message_id):
    scores = await client.get_game_high_scores(user_id=777, inline_message_id=inline_message_id)

    assert isinstance(client.sent, raw.functions.messages.GetInlineGameHighScores)
    assert client.sent.id.dc_id == 2
    assert client.sent.id.id == 10
    assert isinstance(scores, list)


async def test_gift_premium_subscription(client):
    res = await client.gift_premium_subscription(
        user_id=777,
        month_count=3,
        star_count=1000,
        text="Happy birthday!",
    )

    assert isinstance(client.sent, raw.functions.payments.SendStarsForm)
    assert client.sent.form_id == 987
    assert isinstance(client.sent.invoice, raw.types.InputInvoicePremiumGiftStars)
    assert client.sent.invoice.months == 3
    assert isinstance(client.sent.invoice.user_id, raw.types.InputUser)
    assert client.sent.invoice.message.text == "Happy birthday!"
    assert res is True


def test_rich_message_sanitizers():
    # Test PageBlockVideo without flags
    video_block = raw.types.PageBlockVideo(
        video_id=123,
        caption=raw.types.PageCaption(
            text=raw.types.TextPlain(text="video"), credit=raw.types.TextEmpty()
        ),
        autoplay=True,
        loop=False,
    )
    sanitized_video = _sanitize_block(video_block)
    assert isinstance(sanitized_video, raw.types.PageBlockVideo)
    assert sanitized_video.video_id == 123
    assert sanitized_video.autoplay is True

    # Test PageBlockList and PageBlockOrderedList
    list_item = raw.types.PageListItemText(text=raw.types.TextPlain(text="item 1"))
    unordered_list = raw.types.PageBlockList(items=[list_item])
    sanitized_unordered = _sanitize_block(unordered_list)
    assert isinstance(sanitized_unordered, raw.types.PageBlockList)
    assert len(sanitized_unordered.items) == 1

    ordered_item = raw.types.PageListOrderedItemText(
        num="1.", text=raw.types.TextPlain(text="first")
    )
    ordered_list = raw.types.PageBlockOrderedList(items=[ordered_item])
    sanitized_ordered = _sanitize_block(ordered_list)
    assert isinstance(sanitized_ordered, raw.types.PageBlockOrderedList)
    assert len(sanitized_ordered.items) == 1


async def test_set_passport_data_errors(client):
    error = raw.types.SecureValueError(
        type=raw.types.SecureValueTypePersonalDetails(),
        hash=b"hash",
        text="Invalid details",
    )
    res = await client.set_passport_data_errors(user_id=777, errors=[error])

    assert isinstance(client.sent, raw.functions.users.SetSecureValueErrors)
    assert isinstance(client.sent.id, raw.types.InputUser)
    assert client.sent.errors == [error]
    assert res is True
