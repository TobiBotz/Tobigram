from datetime import datetime
from unittest.mock import Mock

import pytest

import pyrogram
from pyrogram import enums, types
from pyrogram.types import Object
from pyrogram.types.messages_and_media.message import Str as MessageStr
from pyrogram.types.user_and_chats.user import Link as UserLink


# ---------------------------------------------------------------------------
# 1.  Test creating each type with the MINIMUM required parameters
# ---------------------------------------------------------------------------

class TestMinimalConstruction:
    def test_object_minimal(self):
        obj = Object()
        assert obj._client is None

    def test_message_minimal(self):
        msg = types.Message(id=1)
        assert msg.id == 1

    def test_user_minimal(self):
        user = types.User(id=123)
        assert user.id == 123

    def test_chat_minimal(self):
        chat = types.Chat()
        assert chat.id is None

    def test_chat_member_minimal(self):
        member = types.ChatMember(status=enums.ChatMemberStatus.MEMBER)
        assert member.status == enums.ChatMemberStatus.MEMBER

    def test_inline_keyboard_button_minimal(self):
        btn = types.InlineKeyboardButton(text="Click")
        assert btn.text == "Click"
        assert btn.callback_data is None

    def test_inline_keyboard_markup_minimal(self):
        btn = types.InlineKeyboardButton(text="A", callback_data="1")
        markup = types.InlineKeyboardMarkup(inline_keyboard=[[btn]])
        assert markup.inline_keyboard == [[btn]]

    def test_callback_query_minimal(self):
        user = types.User(id=1)
        q = types.CallbackQuery(id="cq1", from_user=user, chat_instance="ci1")
        assert q.id == "cq1"
        assert q.from_user.id == 1

    def test_reply_parameters_minimal(self):
        rp = types.ReplyParameters()
        assert rp.message_id is None

    def test_photo_minimal(self):
        dt = datetime(2023, 1, 1)
        photo = types.Photo(
            file_id="fid",
            file_unique_id="fuid",
            width=100,
            height=200,
            file_size=5000,
            date=dt,
        )
        assert photo.file_id == "fid"
        assert photo.width == 100

    def test_audio_minimal(self):
        audio = types.Audio(file_id="fid", file_unique_id="fuid", duration=120)
        assert audio.duration == 120

    def test_document_minimal(self):
        doc = types.Document(file_id="fid", file_unique_id="fuid")
        assert doc.file_id == "fid"

    def test_video_minimal(self):
        video = types.Video(
            file_id="fid",
            file_unique_id="fuid",
            width=640,
            height=480,
            codec="h264",
            duration=60,
        )
        assert video.codec == "h264"

    def test_voice_minimal(self):
        voice = types.Voice(file_id="fid", file_unique_id="fuid", duration=30)
        assert voice.duration == 30

    def test_video_note_minimal(self):
        vn = types.VideoNote(file_id="fid", file_unique_id="fuid", length=240, duration=10)
        assert vn.length == 240

    def test_animation_minimal(self):
        anim = types.Animation(
            file_id="fid",
            file_unique_id="fuid",
            width=320,
            height=240,
            duration=5,
        )
        assert anim.duration == 5

    def test_contact_minimal(self):
        contact = types.Contact(phone_number="+123", first_name="Alice")
        assert contact.phone_number == "+123"
        assert contact.first_name == "Alice"

    def test_location_minimal(self):
        loc = types.Location(latitude=1.0, longitude=2.0)
        assert loc.latitude == 1.0

    def test_venue_minimal(self):
        loc = types.Location(latitude=1.0, longitude=2.0)
        venue = types.Venue(location=loc, title="Cafe", address="123 St")
        assert venue.title == "Cafe"

    def test_poll_minimal(self):
        opt = types.PollOption(persistent_id="opt1")
        poll = types.Poll(
            id="poll1",
            options=[opt],
            is_closed=False,
        )
        assert poll.id == "poll1"
        assert len(poll.options) == 1

    def test_dice_minimal(self):
        dice = types.Dice(emoji="🎲", value=5)
        assert dice.emoji == "🎲"
        assert dice.value == 5

    def test_sticker_minimal(self):
        st = types.Sticker(
            file_id="fid",
            file_unique_id="fuid",
            type=enums.StickerType.REGULAR,
            width=512,
            height=512,
            is_animated=False,
            is_video=False,
        )
        assert st.type == enums.StickerType.REGULAR

    def test_web_page_minimal(self):
        wp = types.WebPage(id="wp1", url="https://example.com")
        assert wp.id == "wp1"
        assert wp.url == "https://example.com"

    def test_game_minimal(self):
        dt = datetime(2023, 1, 1)
        photo = types.Photo(
            file_id="fid", file_unique_id="fuid",
            width=100, height=100, file_size=1000, date=dt,
        )
        game = types.Game(
            id=1,
            title="Test",
            short_name="test",
            description="A game",
            photo=photo,
        )
        assert game.title == "Test"

    def test_message_entity_minimal(self):
        entity = types.MessageEntity(
            type=enums.MessageEntityType.BOLD,
            offset=0,
            length=5,
        )
        assert entity.type == enums.MessageEntityType.BOLD

    def test_forum_topic_minimal(self):
        topic = types.ForumTopic(id=42)
        assert topic.id == 42

    def test_keyboard_button_minimal(self):
        btn = types.KeyboardButton(text="Press")
        assert btn.text == "Press"

    def test_force_reply_minimal(self):
        fr = types.ForceReply()
        assert fr.selective is None

    def test_reply_keyboard_markup_minimal(self):
        btn = types.KeyboardButton(text="Go")
        markup = types.ReplyKeyboardMarkup(keyboard=[[btn]])
        assert markup.keyboard == [[btn]]

    def test_reply_keyboard_remove_minimal(self):
        rkr = types.ReplyKeyboardRemove()
        assert rkr.selective is None


# ---------------------------------------------------------------------------
# 2.  Test common properties / methods
# ---------------------------------------------------------------------------

class TestCommonProperties:
    def test_object_str_repr(self):
        obj = Object()
        s = str(obj)
        assert '"_": "Object"' in s
        r = repr(obj)
        assert r.startswith("pyrogram.types.Object(")

    def test_object_eq(self):
        a = Object()
        b = Object()
        assert a == b

    def test_object_bind(self):
        obj = Object()
        obj.bind(None)
        assert obj._client is None

    def test_object_default_datetime(self):
        result = Object.default(datetime(2023, 6, 15))
        assert isinstance(result, str)

    def test_user_full_name(self):
        user = types.User(id=1, first_name="John", last_name="Doe")
        assert user.full_name == "John Doe"

    def test_user_full_name_none_last(self):
        user = types.User(id=1, first_name="John")
        assert user.full_name == "John"

    def test_user_empty_full_name(self):
        user = types.User(id=1)
        assert user.full_name is None

    def test_user_mention(self):
        user = types.User(id=1, first_name="Alice")
        user._client = Mock()
        user._client.parse_mode = enums.ParseMode.HTML
        mention = user.mention
        assert "tg://user?id=1" in str(mention)

    def test_message_link(self):
        chat = types.Chat(
            id=-100123,
            type=enums.ChatType.SUPERGROUP,
            username="testgroup",
        )
        msg = types.Message(id=5, chat=chat)
        assert "t.me/testgroup/5" in msg.link

    def test_message_content_no_text(self):
        msg = types.Message(id=1)
        assert msg.content == ""

    def test_message_content_text(self):
        msg = types.Message(id=1, text=MessageStr("hello"))
        assert msg.content == "hello"

    def test_message_content_caption(self):
        msg = types.Message(id=1, caption=MessageStr("capt"))
        assert msg.content == "capt"

    def test_message_empty_default(self):
        msg = types.Message(id=1)
        assert msg.empty is None

    def test_message_empty_explicit(self):
        msg = types.Message(id=1, empty=True)
        assert msg.empty is True

    def test_callable_link(self):
        link = UserLink(url="tg://user?id=1", text="Alice", style=enums.ParseMode.HTML)
        assert callable(link)


# ---------------------------------------------------------------------------
# 3.  Test that all expected types are exported from pyrogram.types
# ---------------------------------------------------------------------------

class TestExports:
    _expected_types = [
        "Object",
        "Message",
        "User",
        "Chat",
        "ChatMember",
        "InlineKeyboardButton",
        "InlineKeyboardMarkup",
        "CallbackQuery",
        "ReplyParameters",
        "Photo",
        "Audio",
        "Document",
        "Video",
        "Voice",
        "VideoNote",
        "Animation",
        "Contact",
        "Location",
        "Venue",
        "Poll",
        "Dice",
        "Sticker",
        "WebPage",
        "Game",
        "MessageEntity",
        "ForumTopic",
        "KeyboardButton",
        "ForceReply",
        "ReplyKeyboardMarkup",
        "ReplyKeyboardRemove",
        "List",
        "InlineQuery",
        "ChosenInlineResult",
        "SentCode",
        "TermsOfService",
    ]

    def test_expected_types_exported(self):
        for name in self._expected_types:
            assert hasattr(pyrogram.types, name), f"{name} is not exported from pyrogram.types"

    def test_object_base(self):
        assert issubclass(types.Message, Object)
        assert issubclass(types.User, Object)
        assert issubclass(types.Chat, Object)
        assert issubclass(types.CallbackQuery, Object)
        assert issubclass(types.Poll, Object)


# ---------------------------------------------------------------------------
# 4.  Test type conversions / __init__ keyword-only behaviour
# ---------------------------------------------------------------------------

class TestInits:
    def test_message_requires_id(self):
        with pytest.raises(TypeError):
            types.Message()

    def test_user_requires_id(self):
        with pytest.raises(TypeError):
            types.User()

    def test_chat_member_requires_status(self):
        with pytest.raises(TypeError):
            types.ChatMember()

    def test_inline_keyboard_button_requires_text(self):
        with pytest.raises(TypeError):
            types.InlineKeyboardButton()

    def test_inline_keyboard_markup_requires_keyboard(self):
        with pytest.raises(TypeError):
            types.InlineKeyboardMarkup()

    def test_callback_query_requires_id_from_user_chat_instance(self):
        with pytest.raises(TypeError):
            types.CallbackQuery()
        with pytest.raises(TypeError):
            types.CallbackQuery(id="x", from_user=types.User(id=1))
        with pytest.raises(TypeError):
            types.CallbackQuery(id="x", chat_instance="ci")

    def test_photo_requires_file_fields(self):
        with pytest.raises(TypeError):
            types.Photo(file_id="fid")

    def test_audio_requires_duration(self):
        with pytest.raises(TypeError):
            types.Audio(file_id="fid", file_unique_id="fuid")

    def test_video_requires_media_fields(self):
        with pytest.raises(TypeError):
            types.Video(file_id="fid", file_unique_id="fuid", width=100, height=100)

    def test_dice_requires_emoji_and_value(self):
        with pytest.raises(TypeError):
            types.Dice(emoji="🎲")
        with pytest.raises(TypeError):
            types.Dice(value=3)

    def test_sticker_requires_all_required(self):
        with pytest.raises(TypeError):
            types.Sticker(file_id="fid")

    def test_message_entity_requires_type_offset_length(self):
        with pytest.raises(TypeError):
            types.MessageEntity(type=enums.MessageEntityType.BOLD)
        with pytest.raises(TypeError):
            types.MessageEntity(type=enums.MessageEntityType.BOLD, offset=0)

    def test_contact_requires_phone_and_first_name(self):
        with pytest.raises(TypeError):
            types.Contact(phone_number="+1")

    def test_venue_requires_location_title_address(self):
        with pytest.raises(TypeError):
            types.Venue(title="X", address="Y")
        with pytest.raises(TypeError):
            types.Venue(location=types.Location(), title="X")

    def test_poll_missing_is_closed(self):
        with pytest.raises(TypeError):
            types.Poll(id="p1", options=[types.PollOption(persistent_id="o")])

    def test_keyword_only_args(self):
        with pytest.raises(TypeError):
            types.User(123)

    def test_forum_topic_id_required(self):
        with pytest.raises(TypeError):
            types.ForumTopic()


# ---------------------------------------------------------------------------
# 5.  Test __setstate__ / __getstate__ (pickle support)
# ---------------------------------------------------------------------------

class TestPickle:
    def test_object_getstate_no_client(self):
        obj = Object()
        state = obj.__getstate__()
        assert "_client" not in state

    def test_object_pickle_roundtrip(self):
        obj = Object()
        state = obj.__getstate__()
        new_obj = Object()
        new_obj.__setstate__(state)
        assert getattr(new_obj, "_client", None) is None

    def test_object_pickle_datetime(self):
        msg = types.Message(id=1, date=datetime(2023, 1, 1, 12, 0))
        state = msg.__getstate__()
        new_msg = object.__new__(types.Message)
        new_msg.__setstate__(state)
        assert new_msg.date == datetime(2023, 1, 1, 12, 0)

    def test_message_pickle_roundtrip(self):
        msg = types.Message(id=42, text=MessageStr("hello"))
        state = msg.__getstate__()
        new_msg = object.__new__(types.Message)
        new_msg.__setstate__(state)
        assert new_msg.id == 42
        assert new_msg.text == "hello"


# ---------------------------------------------------------------------------
# 6.  Test InlineKeyboardButton customisation
# ---------------------------------------------------------------------------

class TestInlineKeyboardButton:
    def test_button_style_default(self):
        btn = types.InlineKeyboardButton(text="X", callback_data="d")
        assert btn.style == enums.ButtonStyle.DEFAULT

    def test_button_with_callback(self):
        btn = types.InlineKeyboardButton(text="X", callback_data="data")
        assert btn.callback_data == "data"

    def test_button_with_url(self):
        btn = types.InlineKeyboardButton(text="Link", url="https://t.me")
        assert btn.url == "https://t.me"

    def test_button_text_converted_to_str(self):
        btn = types.InlineKeyboardButton(text=123)
        assert isinstance(btn.text, str)
        assert btn.text == "123"


# ---------------------------------------------------------------------------
# 7.  Test ReplyKeyboardButton
# ---------------------------------------------------------------------------

class TestKeyboardButton:
    def test_button_text_converted_to_str(self):
        btn = types.KeyboardButton(text=42)
        assert isinstance(btn.text, str)
        assert btn.text == "42"

    def test_button_request_contact(self):
        btn = types.KeyboardButton(text="Share", request_contact=True)
        assert btn.request_contact is True


# ---------------------------------------------------------------------------
# 8.  Test Location edge cases
# ---------------------------------------------------------------------------

class TestLocation:
    def test_defaults(self):
        loc = types.Location()
        assert loc.longitude is None
        assert loc.latitude is None

    def test_with_coords(self):
        loc = types.Location(latitude=10.0, longitude=20.0)
        assert loc.latitude == 10.0
        assert loc.longitude == 20.0

    def test_live_period(self):
        loc = types.Location(latitude=1.0, longitude=2.0, live_period=60)
        assert loc.live_period == 60

    def test_heading(self):
        loc = types.Location(latitude=1.0, longitude=2.0, heading=90)
        assert loc.heading == 90

    def test_proximity_alert_radius(self):
        loc = types.Location(latitude=1.0, longitude=2.0, proximity_alert_radius=100)
        assert loc.proximity_alert_radius == 100


# ---------------------------------------------------------------------------
# 9.  Test the Link helper
# ---------------------------------------------------------------------------

class TestUserLink:
    def test_link_class(self):
        link = UserLink(url="tg://user?id=1", text="Alice", style=enums.ParseMode.HTML)
        assert "tg://user?id=1" in str(link)
        assert link.url == "tg://user?id=1"

    def test_link_format_html(self):
        result = UserLink.format(url="tg://user?id=1", text="Alice", style=enums.ParseMode.HTML)
        assert 'href=' in result
        assert "tg://user?id=1" in result
        assert "Alice</a>" in result

    def test_link_format_markdown(self):
        result = UserLink.format(url="tg://user?id=1", text="Alice", style=enums.ParseMode.MARKDOWN)
        assert result == "[Alice](tg://user?id=1)"


# ---------------------------------------------------------------------------
# 10.  Test Message.Str helper
# ---------------------------------------------------------------------------

class TestMessageStr:
    def test_str_init(self):
        s = MessageStr("hello")
        assert s == "hello"
        assert s.entities is None

    def test_str_init_entities(self):
        s = MessageStr("hello")
        s.init([])
        assert s.entities == []


# ---------------------------------------------------------------------------
# 11.  Test nested objects
# ---------------------------------------------------------------------------

class TestNestedTypes:
    def test_message_with_reply_markup(self):
        markup = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="B", callback_data="b")]]
        )
        msg = types.Message(id=1, reply_markup=markup)
        assert msg.reply_markup.inline_keyboard[0][0].text == "B"

    def test_chat_member_with_user(self):
        user = types.User(id=99, first_name="Bob")
        member = types.ChatMember(
            status=enums.ChatMemberStatus.MEMBER,
            user=user,
            joined_date=datetime(2024, 1, 1),
        )
        assert member.user.first_name == "Bob"
        assert member.joined_date == datetime(2024, 1, 1)

    def test_venue_with_location(self):
        loc = types.Location(latitude=40.0, longitude=-3.0)
        venue = types.Venue(location=loc, title="X", address="Y")
        assert venue.location.latitude == 40.0

    def test_poll_with_options(self):
        opt1 = types.PollOption(persistent_id="a")
        opt2 = types.PollOption(persistent_id="b")
        poll = types.Poll(id="p1", options=[opt1, opt2], is_closed=False)
        assert len(poll.options) == 2
        assert poll.options[0].persistent_id == "a"


# ---------------------------------------------------------------------------
# 12.  Test attribute assignment compability (no __slots__ used by these types)
# ---------------------------------------------------------------------------

class TestDynamicAttributes:
    def test_message_dynamic_attr(self):
        msg = types.Message(id=1)
        msg.custom_attr = 42
        assert msg.custom_attr == 42

    def test_user_dynamic_attr(self):
        user = types.User(id=1)
        user.custom_attr = "hello"
        assert user.custom_attr == "hello"

    def test_chat_dynamic_attr(self):
        chat = types.Chat(id=1)
        chat.custom_attr = [1, 2, 3]
        assert chat.custom_attr == [1, 2, 3]

    def test_callback_query_dynamic_attr(self):
        q = types.CallbackQuery(id="q", from_user=types.User(id=1), chat_instance="ci")
        q.new_field = True
        assert q.new_field is True

    def test_sticker_dynamic_attr(self):
        st = types.Sticker(
            file_id="fid", file_unique_id="fuid",
            type=enums.StickerType.REGULAR,
            width=100, height=100, is_animated=False, is_video=False,
        )
        st.extra = 1
        assert st.extra == 1


# ---------------------------------------------------------------------------
# 13.  Verify all user-facing types are subclasses of Object
# ---------------------------------------------------------------------------

_OBJECT_SUBCLASS_TYPES = [
    types.Message,
    types.User,
    types.Chat,
    types.ChatMember,
    types.InlineKeyboardButton,
    types.InlineKeyboardMarkup,
    types.CallbackQuery,
    types.ReplyParameters,
    types.Photo,
    types.Audio,
    types.Document,
    types.Video,
    types.Voice,
    types.VideoNote,
    types.Animation,
    types.Contact,
    types.Location,
    types.Venue,
    types.Poll,
    types.Dice,
    types.Sticker,
    types.WebPage,
    types.Game,
    types.MessageEntity,
    types.ForumTopic,
    types.KeyboardButton,
    types.ForceReply,
    types.ReplyKeyboardMarkup,
    types.ReplyKeyboardRemove,
]


class TestObjectSubclass:
    @pytest.mark.parametrize("cls", _OBJECT_SUBCLASS_TYPES, ids=lambda c: c.__name__)
    def test_is_object_subclass(self, cls):
        assert issubclass(cls, Object), f"{cls.__name__} is not a subclass of Object"


# ---------------------------------------------------------------------------
# 14.  Test that Poll.get_vote_percentage works as a static method
# ---------------------------------------------------------------------------

class TestPollVotePercentage:
    def test_all_zero(self):
        result = types.Poll.get_vote_percentage([0, 0, 0], 0)
        assert result == [0, 0, 0]

    def test_single_option(self):
        result = types.Poll.get_vote_percentage([10], 10)
        assert result == [100]

    def test_two_options_equal(self):
        result = types.Poll.get_vote_percentage([5, 5], 10)
        assert result == [50, 50]

    def test_three_options(self):
        result = types.Poll.get_vote_percentage([3, 3, 4], 10)
        assert sum(result) == 100
        assert len(result) == 3

    def test_total_voter_count_differs(self):
        result = types.Poll.get_vote_percentage([5, 5], 8)
        assert len(result) == 2
        assert result[0] == result[1]


# ---------------------------------------------------------------------------
# 15.  Test that the Link class __new__/__str__ work
# ---------------------------------------------------------------------------

class TestLinkStr:
    def test_link_str_html(self):
        link = UserLink(url="tg://user?id=1", text="Alice", style=enums.ParseMode.HTML)
        s = str(link)
        assert "tg://user?id=1" in s
        assert "Alice" in s

    def test_link_str_markdown(self):
        link = UserLink(url="tg://user?id=1", text="Alice", style=enums.ParseMode.MARKDOWN)
        s = str(link)
        assert s == "[Alice](tg://user?id=1)"

    def test_link_callable(self):
        link = UserLink(url="tg://user?id=1", text="Alice", style=enums.ParseMode.HTML)
        result = link("Bob")
        assert "Bob" in result
        assert "tg://user?id=1" in result

    def test_link_callable_with_style(self):
        link = UserLink(url="tg://user?id=1", text="Alice", style=enums.ParseMode.HTML)
        result = link(style=enums.ParseMode.MARKDOWN)
        assert "Alice" in result
        assert result.startswith("[")


# ---------------------------------------------------------------------------
# 16.  Test Message properties (content, md_text, html_text)
# ---------------------------------------------------------------------------

class TestMessageProperties:
    def test_md_text_no_text(self):
        msg = types.Message(id=1)
        assert msg.md_text == ""

    def test_html_text_no_text(self):
        msg = types.Message(id=1)
        assert msg.html_text == ""

    def test_md_text_with_text(self):
        s = MessageStr("hello")
        s.entities = []
        msg = types.Message(id=1, text=s, entities=[])
        assert msg.md_text == "hello"

    def test_html_text_with_text(self):
        s = MessageStr("hello")
        s.entities = []
        msg = types.Message(id=1, text=s, entities=[])
        assert msg.html_text == "hello"


# ---------------------------------------------------------------------------
# 17.  Test Object.__repr__ roundtrip property
# ---------------------------------------------------------------------------

class TestObjectRepr:
    def test_repr_includes_class_name(self):
        msg = types.Message(id=1)
        r = repr(msg)
        assert "Message(" in r

    def test_repr_includes_non_none_attrs(self):
        msg = types.Message(id=42, text=MessageStr("hi"))
        r = repr(msg)
        assert "id=42" in r
        assert "text=" in r


# ---------------------------------------------------------------------------
# 18.  Test Object.default for various types
# ---------------------------------------------------------------------------

class TestObjectDefault:
    def test_default_bytes(self):
        result = Object.default(b"hello")
        assert isinstance(result, str)

    def test_default_enum(self):
        result = Object.default(enums.ChatMemberStatus.MEMBER)
        assert isinstance(result, str)

    def test_default_datetime(self):
        result = Object.default(datetime(2024, 1, 1))
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# 19.  Test Object.__eq__
# ---------------------------------------------------------------------------

class TestObjectEq:
    def test_eq_same_attrs(self):
        a = types.Message(id=1)
        b = types.Message(id=1)
        assert a == b

    def test_eq_different_attrs(self):
        a = types.Message(id=1)
        b = types.Message(id=2)
        assert a != b

    def test_eq_different_types(self):
        a = types.User(id=1)
        b = types.Message(id=1)
        assert a != b


class TestCommunity:
    def test_minimal(self):
        c = types.Community(id=1, title="Test")
        assert c.id == 1
        assert c.title == "Test"
        assert c.date is None
        assert c.is_creator is None

    def test_chat_type_enum(self):
        assert enums.ChatType.COMMUNITY.value == "community"

    def test_message_service_type_enums(self):
        assert enums.MessageServiceType.COMMUNITY_CHAT_ADDED is not None
        assert enums.MessageServiceType.COMMUNITY_CHAT_REMOVED is not None

    def test_message_has_fields(self):
        msg = types.Message(id=1)
        assert msg.community_chat_added is None
        assert msg.community_chat_removed is None

    def test_chat_full_info(self):
        info = types.ChatFullInfo()
        assert info.community is None

    def test_community_chat_added(self):
        added = types.CommunityChatAdded(community_id=123)
        assert added.community_id == 123

    def test_community_chat_removed(self):
        removed = types.CommunityChatRemoved()
        assert removed.community_id is None
