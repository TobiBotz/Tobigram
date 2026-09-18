import pytest

from pyrogram import raw, types

ALLOWED = {
    "article",
    "photo",
    "gif",
    "video",
    "audio",
    "voice",
    "file",
    "geo",
    "venue",
    "contact",
    "sticker",
    "game",
}

CONTENT = types.InputTextMessageContent("body")


@pytest.mark.parametrize(
    "result",
    [
        types.InlineQueryResultArticle(title="t", input_message_content=CONTENT),
        types.InlineQueryResultPhoto(photo_url="https://example.org/a.jpg"),
        types.InlineQueryResultAnimation(animation_url="https://example.org/a.gif"),
        types.InlineQueryResultVideo(
            video_url="https://example.org/a.mp4",
            thumb_url="https://example.org/a.jpg",
            title="t",
        ),
        types.InlineQueryResultAudio(audio_url="https://example.org/a.mp3", title="t"),
        types.InlineQueryResultVoice(voice_url="https://example.org/a.ogg", title="t"),
        types.InlineQueryResultDocument(document_url="https://example.org/a.pdf", title="t"),
        types.InlineQueryResultContact(phone_number="+15550001111", first_name="A"),
        types.InlineQueryResultLocation(title="t", latitude=1.0, longitude=2.0),
        types.InlineQueryResultVenue(title="t", address="a", latitude=1.0, longitude=2.0),
        types.InlineQueryResultCachedSticker(sticker_file_id="x"),
        types.InlineQueryResultCachedPhoto(photo_file_id="x"),
        types.InlineQueryResultCachedVideo(video_file_id="x", title="t"),
        types.InlineQueryResultCachedAnimation(animation_file_id="x"),
        types.InlineQueryResultCachedAudio(audio_file_id="x"),
        types.InlineQueryResultCachedVoice(voice_file_id="x"),
        types.InlineQueryResultCachedDocument(document_file_id="x", title="t"),
    ],
)
def test_every_result_uses_a_type_telegram_knows(result):
    assert result.type in ALLOWED


async def test_a_location_result_is_sent_as_geo():
    result = types.InlineQueryResultLocation(title="t", latitude=1.0, longitude=2.0)

    written = await result.write(None)

    assert isinstance(written, raw.types.InputBotInlineResult)
    assert written.type == "geo"
