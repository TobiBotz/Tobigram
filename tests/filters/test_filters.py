import pytest

from pyrogram import filters, enums
from pyrogram.types import (
    Animation,
    Audio,
    Chat,
    Contact,
    Dice,
    Document,
    Game,
    GameHighScore,
    Giveaway,
    GiveawayWinners,
    Location,
    Message,
    MessageOriginUser,
    Photo,
    Poll,
    Sticker,
    Story,
    SuccessfulPayment,
    User,
    Venue,
    Video,
    VideoChatEnded,
    VideoChatMembersInvited,
    VideoChatStarted,
    VideoNote,
    Voice,
    WebPage,
)


class FakeClient:
    def __init__(self):
        self.me = User(
            id=123, is_self=True, is_bot=False,
            first_name="User", username="username"
        )


c = FakeClient()


# ============================================================
# Media filters
# ============================================================

@pytest.mark.asyncio
async def test_photo_filter():
    m = Message(id=1, photo=Photo(
        file_id="f", file_unique_id="f", width=100, height=100,
        file_size=1000, date=None
    ))
    assert await filters.photo(c, m)
    m2 = Message(id=2)
    assert not await filters.photo(c, m2)


@pytest.mark.asyncio
async def test_video_filter():
    m = Message(id=1, video=Video(
        file_id="f", file_unique_id="f", width=100, height=100,
        codec="h264", duration=10
    ))
    assert await filters.video(c, m)
    m2 = Message(id=2)
    assert not await filters.video(c, m2)


@pytest.mark.asyncio
async def test_audio_filter():
    m = Message(id=1, audio=Audio(
        file_id="f", file_unique_id="f", duration=10
    ))
    assert await filters.audio(c, m)
    m2 = Message(id=2)
    assert not await filters.audio(c, m2)


@pytest.mark.asyncio
async def test_document_filter():
    m = Message(id=1, document=Document(
        file_id="f", file_unique_id="f"
    ))
    assert await filters.document(c, m)
    m2 = Message(id=2)
    assert not await filters.document(c, m2)


@pytest.mark.asyncio
async def test_sticker_filter():
    m = Message(id=1, sticker=Sticker(
        file_id="f", file_unique_id="f",
        type=enums.StickerType.REGULAR,
        width=100, height=100, is_animated=False, is_video=False
    ))
    assert await filters.sticker(c, m)
    m2 = Message(id=2)
    assert not await filters.sticker(c, m2)


@pytest.mark.asyncio
async def test_animation_filter():
    m = Message(id=1, animation=Animation(
        file_id="f", file_unique_id="f", width=100, height=100, duration=10
    ))
    assert await filters.animation(c, m)
    m2 = Message(id=2)
    assert not await filters.animation(c, m2)


@pytest.mark.asyncio
async def test_voice_filter():
    m = Message(id=1, voice=Voice(
        file_id="f", file_unique_id="f", duration=10
    ))
    assert await filters.voice(c, m)
    m2 = Message(id=2)
    assert not await filters.voice(c, m2)


@pytest.mark.asyncio
async def test_video_note_filter():
    m = Message(id=1, video_note=VideoNote(
        file_id="f", file_unique_id="f", length=100, duration=10
    ))
    assert await filters.video_note(c, m)
    m2 = Message(id=2)
    assert not await filters.video_note(c, m2)


@pytest.mark.asyncio
async def test_contact_filter():
    m = Message(id=1, contact=Contact(
        phone_number="12345", first_name="Test"
    ))
    assert await filters.contact(c, m)
    m2 = Message(id=2)
    assert not await filters.contact(c, m2)


@pytest.mark.asyncio
async def test_location_filter():
    m = Message(id=1, location=Location(
        longitude=0.0, latitude=0.0
    ))
    assert await filters.location(c, m)
    m_live = Message(id=2, location=Location(
        longitude=0.0, latitude=0.0, live_period=60
    ))
    assert not await filters.location(c, m_live)
    m3 = Message(id=3)
    assert not await filters.location(c, m3)


@pytest.mark.asyncio
async def test_venue_filter():
    m = Message(id=1, venue=Venue(
        location=Location(longitude=0.0, latitude=0.0),
        title="Venue", address="Addr"
    ))
    assert await filters.venue(c, m)
    m2 = Message(id=2)
    assert not await filters.venue(c, m2)


@pytest.mark.asyncio
async def test_poll_filter():
    m = Message(id=1, poll=Poll(
        id="1", question="?", options=[], is_closed=False
    ))
    assert await filters.poll(c, m)
    m2 = Message(id=2)
    assert not await filters.poll(c, m2)


@pytest.mark.asyncio
async def test_game_filter():
    m = Message(id=1, game=Game(
        id=1, title="G", short_name="g", description="d",
        photo=Photo(
            file_id="f", file_unique_id="f", width=100, height=100,
            file_size=1000, date=None
        )
    ))
    assert await filters.game(c, m)
    m2 = Message(id=2)
    assert not await filters.game(c, m2)


@pytest.mark.asyncio
async def test_dice_filter():
    m = Message(id=1, dice=Dice(emoji="🎲", value=5))
    assert await filters.dice(c, m)
    m2 = Message(id=2)
    assert not await filters.dice(c, m2)


@pytest.mark.asyncio
async def test_story_filter():
    m = Message(id=1, story=Story(id=1))
    assert await filters.story(c, m)
    m2 = Message(id=2)
    assert not await filters.story(c, m2)


@pytest.mark.asyncio
async def test_web_page_filter():
    m = Message(id=1, web_page=WebPage(
        id="1", url="https://example.com"
    ))
    assert await filters.web_page(c, m)
    m2 = Message(id=2)
    assert not await filters.web_page(c, m2)


@pytest.mark.asyncio
async def test_giveaway_filter():
    m = Message(id=1, giveaway=Giveaway())
    assert await filters.giveaway(c, m)
    m2 = Message(id=2)
    assert not await filters.giveaway(c, m2)


@pytest.mark.asyncio
async def test_giveaway_winners_filter():
    m = Message(id=1, giveaway_winners=GiveawayWinners(
        chat=Chat(id=1), giveaway_message_id=1,
        winners_selection_date=None, quantity=1,
        winner_count=1, winners=[]
    ))
    assert await filters.giveaway_winners(c, m)
    m2 = Message(id=2)
    assert not await filters.giveaway_winners(c, m2)


# ============================================================
# Service message filters
# ============================================================

@pytest.mark.asyncio
async def test_new_chat_members_filter():
    m = Message(id=1, new_chat_members=[User(id=1)])
    assert await filters.new_chat_members(c, m)
    m2 = Message(id=2)
    assert not await filters.new_chat_members(c, m2)


@pytest.mark.asyncio
async def test_left_chat_member_filter():
    m = Message(id=1, left_chat_member=User(id=1))
    assert await filters.left_chat_member(c, m)
    m2 = Message(id=2)
    assert not await filters.left_chat_member(c, m2)


@pytest.mark.asyncio
async def test_new_chat_title_filter():
    m = Message(id=1, new_chat_title="New Title")
    assert await filters.new_chat_title(c, m)
    m2 = Message(id=2)
    assert not await filters.new_chat_title(c, m2)


@pytest.mark.asyncio
async def test_new_chat_photo_filter():
    m = Message(id=1, new_chat_photo=[
        Photo(file_id="f", file_unique_id="f", width=100, height=100,
              file_size=1000, date=None)
    ])
    assert await filters.new_chat_photo(c, m)
    m2 = Message(id=2)
    assert not await filters.new_chat_photo(c, m2)


@pytest.mark.asyncio
async def test_delete_chat_photo_filter():
    m = Message(id=1, delete_chat_photo=True)
    assert await filters.delete_chat_photo(c, m)
    m2 = Message(id=2)
    assert not await filters.delete_chat_photo(c, m2)


@pytest.mark.asyncio
async def test_group_chat_created_filter():
    m = Message(id=1, group_chat_created=True)
    assert await filters.group_chat_created(c, m)
    m2 = Message(id=2)
    assert not await filters.group_chat_created(c, m2)


@pytest.mark.asyncio
async def test_supergroup_chat_created_filter():
    m = Message(id=1, supergroup_chat_created=True)
    assert await filters.supergroup_chat_created(c, m)
    m2 = Message(id=2)
    assert not await filters.supergroup_chat_created(c, m2)


@pytest.mark.asyncio
async def test_channel_chat_created_filter():
    m = Message(id=1, channel_chat_created=True)
    assert await filters.channel_chat_created(c, m)
    m2 = Message(id=2)
    assert not await filters.channel_chat_created(c, m2)


@pytest.mark.asyncio
async def test_pinned_message_filter():
    m = Message(id=1, pinned_message=Message(id=999))
    assert await filters.pinned_message(c, m)
    m2 = Message(id=2)
    assert not await filters.pinned_message(c, m2)


@pytest.mark.asyncio
async def test_game_high_score_filter():
    m = Message(id=1, game_high_score=GameHighScore(
        user=User(id=1), score=100
    ))
    assert await filters.game_high_score(c, m)
    m2 = Message(id=2)
    assert not await filters.game_high_score(c, m2)


@pytest.mark.asyncio
async def test_video_chat_started_filter():
    m = Message(id=1, video_chat_started=VideoChatStarted())
    assert await filters.video_chat_started(c, m)
    m2 = Message(id=2)
    assert not await filters.video_chat_started(c, m2)


@pytest.mark.asyncio
async def test_video_chat_ended_filter():
    m = Message(id=1, video_chat_ended=VideoChatEnded(duration=100))
    assert await filters.video_chat_ended(c, m)
    m2 = Message(id=2)
    assert not await filters.video_chat_ended(c, m2)


@pytest.mark.asyncio
async def test_video_chat_members_invited_filter():
    m = Message(id=1, video_chat_members_invited=VideoChatMembersInvited(
        users=[User(id=1)]
    ))
    assert await filters.video_chat_members_invited(c, m)
    m2 = Message(id=2)
    assert not await filters.video_chat_members_invited(c, m2)


@pytest.mark.asyncio
async def test_successful_payment_filter():
    m = Message(id=1, successful_payment=SuccessfulPayment(
        currency="USD", total_amount=100, invoice_payload="p",
        telegram_payment_charge_id="t", provider_payment_charge_id="p"
    ))
    assert await filters.successful_payment(c, m)
    m2 = Message(id=2)
    assert not await filters.successful_payment(c, m2)


@pytest.mark.asyncio
async def test_via_bot_filter():
    m = Message(id=1, via_bot=User(id=999, is_bot=True, first_name="Bot"))
    assert await filters.via_bot(c, m)
    m2 = Message(id=2)
    assert not await filters.via_bot(c, m2)


@pytest.mark.asyncio
async def test_outgoing_filter():
    m = Message(id=1, outgoing=True)
    assert await filters.outgoing(c, m)
    m2 = Message(id=2, outgoing=False)
    assert not await filters.outgoing(c, m2)


@pytest.mark.asyncio
async def test_incoming_filter():
    m = Message(id=1, outgoing=False)
    assert await filters.incoming(c, m)
    m2 = Message(id=2, outgoing=True)
    assert not await filters.incoming(c, m2)


# ============================================================
# Chat type filters
# ============================================================

@pytest.mark.asyncio
async def test_group_filter():
    m = Message(id=1, chat=Chat(type=enums.ChatType.GROUP))
    assert await filters.group(c, m)
    m2 = Message(id=2, chat=Chat(type=enums.ChatType.SUPERGROUP))
    assert await filters.group(c, m2)
    m3 = Message(id=3, chat=Chat(type=enums.ChatType.FORUM))
    assert await filters.group(c, m3)
    m4 = Message(id=4, chat=Chat(type=enums.ChatType.PRIVATE))
    assert not await filters.group(c, m4)


@pytest.mark.asyncio
async def test_private_filter():
    m = Message(id=1, chat=Chat(type=enums.ChatType.PRIVATE))
    assert await filters.private(c, m)
    m2 = Message(id=2, chat=Chat(type=enums.ChatType.BOT))
    assert await filters.private(c, m2)
    m3 = Message(id=3, chat=Chat(type=enums.ChatType.GROUP))
    assert not await filters.private(c, m3)


@pytest.mark.asyncio
async def test_channel_filter():
    m = Message(id=1, chat=Chat(type=enums.ChatType.CHANNEL))
    assert await filters.channel(c, m)
    m2 = Message(id=2, chat=Chat(type=enums.ChatType.GROUP))
    assert not await filters.channel(c, m2)


# ============================================================
# User / bot filters
# ============================================================

@pytest.mark.asyncio
async def test_bot_filter():
    m = Message(id=1, from_user=User(id=1, is_bot=True, first_name="Bot"))
    assert await filters.bot(c, m)
    m2 = Message(id=2, from_user=User(id=2, is_bot=False, first_name="User"))
    assert not await filters.bot(c, m2)


@pytest.mark.asyncio
async def test_user_filter():
    uf = filters.user(42)
    m = Message(id=1, from_user=User(id=42))
    assert await uf(c, m)
    m2 = Message(id=2, from_user=User(id=99))
    assert not await uf(c, m2)


@pytest.mark.asyncio
async def test_user_filter_by_username():
    uf = filters.user("testuser")
    m = Message(id=1, from_user=User(id=1, username="testuser"))
    assert await uf(c, m)
    m2 = Message(id=2, from_user=User(id=2, username="other"))
    assert not await uf(c, m2)


@pytest.mark.asyncio
async def test_sender_chat_filter():
    m = Message(id=1, sender_chat=Chat(id=-100, type=enums.ChatType.CHANNEL))
    assert await filters.sender_chat(c, m)
    m2 = Message(id=2)
    assert not await filters.sender_chat(c, m2)


# ============================================================
# Reply / forward filters
# ============================================================

@pytest.mark.asyncio
async def test_reply_filter():
    m = Message(id=1, reply_to_message_id=5)
    assert await filters.reply(c, m)
    m2 = Message(id=2)
    assert not await filters.reply(c, m2)


@pytest.mark.asyncio
async def test_forwarded_filter():
    m = Message(id=1, forward_origin=MessageOriginUser())
    assert await filters.forwarded(c, m)
    m2 = Message(id=2)
    assert not await filters.forwarded(c, m2)


# ============================================================
# Combinator filters (&, |, ~)
# ============================================================

@pytest.mark.asyncio
async def test_and_filter():
    combined = filters.photo & filters.media_group
    m = Message(id=1, photo=Photo(
        file_id="f", file_unique_id="f", width=100, height=100,
        file_size=1000, date=None
    ), media_group_id=None)
    assert not await combined(c, m)

    m2 = Message(id=2, photo=Photo(
        file_id="f", file_unique_id="f", width=100, height=100,
        file_size=1000, date=None
    ), media_group_id=10)
    assert await combined(c, m2)


@pytest.mark.asyncio
async def test_or_filter():
    combined = filters.photo | filters.video
    m = Message(id=1, photo=Photo(
        file_id="f", file_unique_id="f", width=100, height=100,
        file_size=1000, date=None
    ))
    assert await combined(c, m)

    m2 = Message(id=2, video=Video(
        file_id="f", file_unique_id="f", width=100, height=100,
        codec="h264", duration=10
    ))
    assert await combined(c, m2)

    m3 = Message(id=3)
    assert not await combined(c, m3)


@pytest.mark.asyncio
async def test_invert_filter():
    not_photo = ~filters.photo
    m = Message(id=1, photo=Photo(
        file_id="f", file_unique_id="f", width=100, height=100,
        file_size=1000, date=None
    ))
    assert not await not_photo(c, m)

    m2 = Message(id=2)
    assert await not_photo(c, m2)


# ============================================================
# Misc filters
# ============================================================

@pytest.mark.asyncio
async def test_mentioned_filter():
    m = Message(id=1, mentioned=True)
    assert await filters.mentioned(c, m)
    m2 = Message(id=2, mentioned=False)
    assert not await filters.mentioned(c, m2)


@pytest.mark.asyncio
async def test_media_group_filter():
    m = Message(id=1, media_group_id=42)
    assert await filters.media_group(c, m)
    m2 = Message(id=2)
    assert not await filters.media_group(c, m2)


@pytest.mark.asyncio
async def test_text_filter():
    m = Message(id=1, text="Hello")
    assert await filters.text(c, m)
    m2 = Message(id=2)
    assert not await filters.text(c, m2)


@pytest.mark.asyncio
async def test_caption_filter():
    m = Message(id=1, caption="Hello")
    assert await filters.caption(c, m)
    m2 = Message(id=2)
    assert not await filters.caption(c, m2)


@pytest.mark.asyncio
async def test_regex_filter():
    f = filters.regex(r"hello")
    m = Message(id=1, text="hello world")
    assert await f(c, m)
    m2 = Message(id=2, text="goodbye")
    assert not await f(c, m2)


@pytest.mark.asyncio
async def test_regex_filter_caption():
    f = filters.regex(r"hello")
    m = Message(id=1, caption="hello world")
    assert await f(c, m)


@pytest.mark.asyncio
async def test_regex_filter_sets_matches():
    f = filters.regex(r"hello")
    m = Message(id=1, text="hello world")
    await f(c, m)
    assert m.matches is not None
    assert len(m.matches) > 0


@pytest.mark.asyncio
async def test_command_filter():
    f = filters.command("start")
    m = Message(id=1, text="/start")
    assert await f(c, m)


@pytest.mark.asyncio
async def test_command_filter_no_match():
    f = filters.command("start")
    m = Message(id=1, text="/help")
    assert not await f(c, m)
