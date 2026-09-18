from unittest.mock import AsyncMock, MagicMock

import pytest

from pyrogram import enums, raw, types
from pyrogram.types.messages_and_media.message import Str


class TestMessageContent:
    def test_legacy_flat_param_synthesizes_media_content(self):
        photo = types.Photo(
            file_id="photo_123",
            file_unique_id="unique_123",
            width=100,
            height=100,
            file_size=1024,
            date=None,
        )
        msg = types.Message(id=1, photo=photo)

        # Flat attribute remains accessible
        assert msg.photo is photo
        # media_content is automatically synthesized
        assert msg.media_content is not None
        assert isinstance(msg.media_content, types.MessageContent)
        assert msg.media_content.photo is photo
        assert msg.media_content.type == enums.MessageMediaType.PHOTO

    def test_modern_media_content_populates_flat_attrs(self):
        video = types.Video(
            file_id="video_123",
            file_unique_id="unique_vid_123",
            width=1920,
            height=1080,
            duration=60,
            codec="h264",
        )
        content = types.MessageContent(type=enums.MessageMediaType.VIDEO, video=video)
        msg = types.Message(id=2, media_content=content)

        # media_content is preserved
        assert msg.media_content is content
        # flat attribute is automatically unpacked
        assert msg.video is video

    def test_content_alias_accepts_message_content(self):
        doc = types.Document(
            file_id="doc_123",
            file_unique_id="unique_doc_123",
        )
        content = types.MessageContent(type=enums.MessageMediaType.DOCUMENT, document=doc)
        msg = types.Message(id=3, content=content)

        assert msg.media_content is content
        assert msg.document is doc

    def test_text_only_message_has_none_media_content(self):
        msg = types.Message(id=4, text=Str("Hello world"))

        assert msg.text == "Hello world"
        assert msg.media_content is None
        assert msg.content == "Hello world"

    def test_message_content_auto_infers_type(self):
        audio = types.Audio(
            file_id="audio_123",
            file_unique_id="unique_aud_123",
            duration=120,
        )
        content = types.MessageContent(audio=audio)

        assert content.type == enums.MessageMediaType.AUDIO
        assert content.audio is audio

    def test_live_photo_support(self):
        lp = types.LivePhoto(
            file_id="lp_123",
            file_unique_id="unique_lp_123",
            width=500,
            height=500,
            duration=3,
        )
        content = types.MessageContent(live_photo=lp)

        assert content.type == enums.MessageMediaType.LIVE_PHOTO
        assert content.live_photo is lp

        msg = types.Message(id=5, media_content=content)
        assert msg.live_photo is lp

    @pytest.mark.asyncio
    async def test_parse_message_delegates_to_message_content(self):
        client = MagicMock()
        client.invoke = AsyncMock()

        raw_media = raw.types.MessageMediaPhoto(
            photo=raw.types.Photo(
                id=999,
                access_hash=888,
                file_reference=b"ref",
                date=1700000000,
                sizes=[
                    raw.types.PhotoSize(
                        type="s",
                        w=100,
                        h=100,
                        size=1024,
                    )
                ],
                dc_id=1,
            )
        )

        raw_msg = raw.types.Message(
            id=42,
            peer_id=raw.types.PeerChat(chat_id=12345),
            date=1700000000,
            message="Check this out",
            media=raw_media,
            entities=[],
        )

        users = {}
        chats = {
            12345: raw.types.Chat(
                id=12345,
                title="Test Chat",
                photo=raw.types.ChatPhotoEmpty(),
                participants_count=1,
                date=1700000000,
                version=1,
            )
        }

        parsed = await types.Message._parse_message(
            client=client,
            message=raw_msg,
            users=users,
            chats=chats,
        )

        assert parsed.id == 42
        assert parsed.photo is not None
        assert parsed.media_content is not None
        assert parsed.media_content.photo is parsed.photo
        assert parsed.media_content.type == enums.MessageMediaType.PHOTO
        assert parsed.media == enums.MessageMediaType.PHOTO
        assert parsed.caption == "Check this out"
        assert parsed.content == "Check this out"
