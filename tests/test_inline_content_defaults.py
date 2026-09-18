from pyrogram import types


async def test_venue_content_without_place_ids():
    content = types.InputVenueMessageContent(51.5, -0.12, "title", "address")

    raw_content = await content.write(None, None)

    assert raw_content.provider == ""
    assert raw_content.venue_id == ""
    assert raw_content.venue_type == ""


async def test_venue_content_keeps_google_place():
    content = types.InputVenueMessageContent(
        51.5, -0.12, "title", "address", google_place_id="g", google_place_type="t"
    )

    raw_content = await content.write(None, None)

    assert raw_content.provider == "google"
    assert raw_content.venue_id == "g"
    assert raw_content.venue_type == "t"


async def test_contact_content_without_last_name_or_vcard():
    content = types.InputContactMessageContent("+15550001111", "First")

    raw_content = await content.write(None, None)

    assert raw_content.last_name == ""
    assert raw_content.vcard == ""


async def test_invoice_content_without_provider_token():
    content = types.InputInvoiceMessageContent(
        title="t",
        description="d",
        payload="p",
        currency="XTR",
        prices=[types.LabeledPrice("label", 1)],
    )

    class FakeClient:
        test_mode = False

    raw_content = await content.write(FakeClient(), None)

    assert raw_content.provider == ""
    assert raw_content.payload == b"p"


async def test_every_content_serialises():
    class FakeClient:
        test_mode = False

    for content in (
        types.InputVenueMessageContent(51.5, -0.12, "title", "address"),
        types.InputContactMessageContent("+15550001111", "First"),
        types.InputInvoiceMessageContent(
            title="t",
            description="d",
            payload="p",
            currency="XTR",
            prices=[types.LabeledPrice("label", 1)],
        ),
    ):
        assert bytes((await content.write(FakeClient(), None)).write())
