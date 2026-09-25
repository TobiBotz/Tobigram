from pyrogram import raw, types


class DummyClient:
    pass


def test_photo_parse_stripped_only():
    client = DummyClient()
    # A photo that only contains photoStrippedSize or photoPathSize
    raw_photo = raw.types.Photo(
        id=12345,
        access_hash=67890,
        file_reference=b"ref",
        date=1700000000,
        sizes=[
            raw.types.PhotoStrippedSize(type="i", bytes=b"test"),
            raw.types.PhotoPathSize(type="j", bytes=b"path"),
        ],
        dc_id=2,
    )
    parsed = types.Photo._parse(client, raw_photo)
    assert parsed is None


def test_photo_parse_with_progressive():
    client = DummyClient()
    raw_photo = raw.types.Photo(
        id=12345,
        access_hash=67890,
        file_reference=b"ref",
        date=1700000000,
        sizes=[
            raw.types.PhotoSizeProgressive(type="x", w=800, h=600, sizes=[100, 200, 300]),
        ],
        dc_id=2,
    )
    parsed = types.Photo._parse(client, raw_photo)
    assert parsed is not None
    assert parsed.width == 800
    assert parsed.height == 600
    assert parsed.file_size == 300
