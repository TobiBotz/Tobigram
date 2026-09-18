import pytest

import pyrogram
from pyrogram import raw, types


class FakeClient:
    test_mode = False

    def __init__(self):
        self.sent = None

    async def invoke(self, query, **kwargs):
        self.sent = query
        return True

    async def resolve_peer(self, chat_id):
        return raw.types.InputPeerChannel(channel_id=chat_id, access_hash=0)

    async def pin_forum_topic(self, chat_id, topic_id):
        return await pyrogram.Client.pin_forum_topic(self, chat_id, topic_id)

    async def unpin_forum_topic(self, chat_id, topic_id):
        return await pyrogram.Client.unpin_forum_topic(self, chat_id, topic_id)


@pytest.fixture
def client():
    return FakeClient()


def invoice_content(**kwargs):
    return types.InputInvoiceMessageContent(
        title="t",
        description="d",
        payload="p",
        currency="XTR",
        prices=[types.LabeledPrice("one star", 7)],
        **kwargs,
    )


async def test_an_invoice_photo_without_sizes_still_serialises():
    content = invoice_content(photo_url="https://example.org/a.jpg")

    written = await content.write(FakeClient(), None)

    assert bytes(written.write())
    assert written.photo.size == 0
    assert written.photo.attributes[0].w == 0
    assert written.photo.attributes[0].h == 0


async def test_given_photo_sizes_are_kept():
    content = invoice_content(
        photo_url="https://example.org/a.jpg",
        photo_size=1024,
        photo_width=64,
        photo_height=48,
    )

    written = await content.write(FakeClient(), None)

    assert written.photo.size == 1024
    assert written.photo.attributes[0].w == 64
    assert written.photo.attributes[0].h == 48


def test_a_total_amount_is_derived_from_the_prices():
    raw_invoice = raw.types.Invoice(
        currency="XTR",
        prices=[
            raw.types.LabeledPrice(label="a", amount=7),
            raw.types.LabeledPrice(label="b", amount=3),
        ],
    )

    invoice = types.Invoice._parse(None, raw_invoice)

    assert invoice.total_amount == 10
    assert [price.amount for price in invoice.prices] == [7, 3]


def test_a_reported_total_amount_wins():
    raw_invoice = raw.types.MessageMediaInvoice(
        title="t", description="d", currency="XTR", total_amount=99, start_param=""
    )

    invoice = types.Invoice._parse(None, raw_invoice)

    assert invoice.total_amount == 99


async def test_pinning_a_topic_asks_the_server_to_pin(client):
    assert await client.pin_forum_topic(-100123, 7) is True
    assert isinstance(client.sent, raw.functions.messages.UpdatePinnedForumTopic)
    assert client.sent.topic_id == 7
    assert client.sent.pinned is True


async def test_unpinning_a_topic_asks_the_server_to_unpin(client):
    assert await client.unpin_forum_topic(-100123, 7) is True
    assert client.sent.pinned is False
