from io import BytesIO
from types import SimpleNamespace

import pytest

import pyrogram
from pyrogram import enums, raw, types
from pyrogram.methods.bots.get_chat_menu_button import GetChatMenuButton
from pyrogram.types.listeners import registry as registry_module


def test_payment_form_photo_url_comes_from_the_web_document():
    form = raw.types.payments.PaymentFormStars(
        form_id=1,
        bot_id=2,
        title="t",
        description="d",
        photo=raw.types.WebDocumentNoProxy(
            url="https://example.org/p.jpg", size=1, mime_type="image/jpeg", attributes=[]
        ),
        invoice=raw.types.Invoice(currency="XTR", prices=[]),
        users=[],
    )

    parsed = types.PaymentForm._parse(None, form)

    assert parsed.photo_url == "https://example.org/p.jpg"


def _user_full(bot_info):
    return raw.types.users.UserFull(
        full_user=raw.types.UserFull(
            id=1,
            settings=raw.types.PeerSettings(),
            notify_settings=raw.types.PeerNotifySettings(),
            common_chats_count=0,
            bot_info=bot_info,
        ),
        chats=[],
        users=[],
    )


class _MenuClient(GetChatMenuButton):
    def __init__(self, bot_info):
        self.bot_info = bot_info

    async def invoke(self, query, *args, **kwargs):
        assert isinstance(query, raw.functions.users.GetFullUser)
        return _user_full(self.bot_info)


async def test_get_chat_menu_button_on_a_user_account_raises_a_clear_error():
    with pytest.raises(ValueError, match="not a bot"):
        await _MenuClient(None).get_chat_menu_button()


async def test_get_chat_menu_button_falls_back_to_default_when_unset():
    result = await _MenuClient(raw.types.BotInfo()).get_chat_menu_button()

    assert isinstance(result, types.MenuButtonDefault)


def test_sent_web_app_message_without_inline_keyboard_has_no_id():
    parsed = types.SentWebAppMessage._parse(raw.types.WebViewMessageSent())

    assert parsed.inline_message_id is None


async def test_story_privacy_survives_a_disallow_rule_after_the_public_rule():
    client = SimpleNamespace(me=None, fetch_stories=False)
    users = {
        7: raw.types.User(id=7, first_name="U", usernames=[], restriction_reason=[], access_hash=1)
    }
    story = raw.types.StoryItem(
        id=1,
        date=0,
        expire_date=0,
        media=raw.types.MessageMediaUnsupported(),
        entities=[],
        media_areas=[],
        privacy=[
            raw.types.PrivacyValueAllowAll(),
            raw.types.PrivacyValueDisallowUsers(users=[7]),
        ],
    )

    parsed = await types.Story._parse(client, story, raw.types.PeerUser(user_id=7), users, {})

    assert parsed.privacy is enums.StoriesPrivacyRules.PUBLIC
    assert [u.id for u in parsed.disallowed_users] == [7]


async def test_story_privacy_maps_an_allow_list_to_selected_users():
    client = SimpleNamespace(me=None, fetch_stories=False)
    users = {
        7: raw.types.User(
            id=7, first_name="U", usernames=[], restriction_reason=[], access_hash=1
        )
    }
    story = raw.types.StoryItem(
        id=1,
        date=0,
        expire_date=0,
        media=raw.types.MessageMediaUnsupported(),
        entities=[],
        media_areas=[],
        privacy=[raw.types.PrivacyValueAllowUsers(users=[7])],
    )

    parsed = await types.Story._parse(client, story, raw.types.PeerUser(user_id=7), users, {})

    assert parsed.privacy is enums.StoriesPrivacyRules.SELECTED_USERS
    assert [u.id for u in parsed.allowed_users] == [7]


async def test_story_privacy_keeps_close_friends_with_extra_users():
    client = SimpleNamespace(me=None, fetch_stories=False)
    users = {
        7: raw.types.User(
            id=7, first_name="U", usernames=[], restriction_reason=[], access_hash=1
        )
    }
    story = raw.types.StoryItem(
        id=1,
        date=0,
        expire_date=0,
        media=raw.types.MessageMediaUnsupported(),
        entities=[],
        media_areas=[],
        privacy=[
            raw.types.PrivacyValueAllowCloseFriends(),
            raw.types.PrivacyValueAllowUsers(users=[7]),
            raw.types.PrivacyValueDisallowAll(),
        ],
    )

    parsed = await types.Story._parse(client, story, raw.types.PeerUser(user_id=7), users, {})

    assert parsed.privacy is enums.StoriesPrivacyRules.CLOSE_FRIENDS
    assert [u.id for u in parsed.allowed_users] == [7]


async def test_story_privacy_reports_disallow_all_as_selected_users():
    client = SimpleNamespace(me=None, fetch_stories=False)
    story = raw.types.StoryItem(
        id=1,
        date=0,
        expire_date=0,
        media=raw.types.MessageMediaUnsupported(),
        entities=[],
        media_areas=[],
        privacy=[raw.types.PrivacyValueDisallowAll()],
    )

    parsed = await types.Story._parse(
        client,
        story,
        raw.types.PeerUser(user_id=7),
        {7: raw.types.User(id=7, first_name="U", usernames=[], restriction_reason=[], access_hash=1)},
        {},
    )

    assert parsed.privacy is enums.StoriesPrivacyRules.SELECTED_USERS
    assert parsed.allowed_users is None


async def test_story_privacy_reads_the_story_flags():
    client = SimpleNamespace(me=None, fetch_stories=False)
    story = raw.types.StoryItem(
        id=1,
        date=0,
        expire_date=0,
        media=raw.types.MessageMediaUnsupported(),
        entities=[],
        media_areas=[],
        privacy=[],
        contacts=True,
    )

    parsed = await types.Story._parse(
        client,
        story,
        raw.types.PeerUser(user_id=7),
        {7: raw.types.User(id=7, first_name="U", usernames=[], restriction_reason=[], access_hash=1)},
        {},
    )

    assert parsed.privacy is enums.StoriesPrivacyRules.CONTACTS


async def test_story_privacy_keeps_allowed_users_and_chats():
    client = SimpleNamespace(me=None, fetch_stories=False)
    users = {
        7: raw.types.User(
            id=7, first_name="U", usernames=[], restriction_reason=[], access_hash=1
        )
    }
    chats = {
        9: raw.types.Chat(
            id=9, title="G", photo=raw.types.ChatPhotoEmpty(), participants_count=1, date=0, version=1
        )
    }
    story = raw.types.StoryItem(
        id=1,
        date=0,
        expire_date=0,
        media=raw.types.MessageMediaUnsupported(),
        entities=[],
        media_areas=[],
        privacy=[
            raw.types.PrivacyValueAllowUsers(users=[7, 8]),
            raw.types.PrivacyValueAllowChatParticipants(chats=[9]),
            raw.types.PrivacyValueDisallowAll(),
        ],
    )

    parsed = await types.Story._parse(client, story, raw.types.PeerUser(user_id=7), users, chats)

    assert parsed.privacy is enums.StoriesPrivacyRules.SELECTED_USERS
    assert [u.id for u in parsed.allowed_users] == [7, -9]


async def test_parse_full_user_populates_bot_admin_rights():
    from pyrogram.types.user_and_chats.user import User

    full_user = raw.types.UserFull(
        id=1,
        settings=raw.types.PeerSettings(),
        notify_settings=raw.types.PeerNotifySettings(),
        common_chats_count=0,
        bot_group_admin_rights=raw.types.ChatAdminRights(change_info=True, ban_users=True),
        bot_broadcast_admin_rights=raw.types.ChatAdminRights(post_messages=True),
    )
    users = {
        1: raw.types.User(
            id=1, first_name="B", usernames=[], restriction_reason=[], access_hash=1
        )
    }

    class _Client:
        me = None

        async def get_messages(self, *args, **kwargs):
            return None

    parsed = await User._parse_full(_Client(), full_user, users, {})

    assert parsed.chat_admin_rights.can_change_info is True
    assert parsed.chat_admin_rights.can_restrict_members is True
    assert parsed.channel_admin_rights.can_post_messages is True


def _message(chat_id, user_id, outgoing):
    return SimpleNamespace(
        chat=SimpleNamespace(id=chat_id),
        from_user=SimpleNamespace(id=user_id),
        id=100,
        outgoing=outgoing,
        scheduled=False,
    )


def test_identify_keeps_an_outgoing_message_in_saved_messages():
    identified = registry_module._identify(
        enums.ListenerTypes.MESSAGE, _message(chat_id=10, user_id=10, outgoing=True)
    )

    assert identified is not None
    assert identified[1] == 10 and identified[2] == 10


def test_identify_still_drops_an_outgoing_message_elsewhere():
    assert (
        registry_module._identify(
            enums.ListenerTypes.MESSAGE, _message(chat_id=1, user_id=10, outgoing=True)
        )
        is None
    )


def test_restart_docstring_no_longer_promises_a_connection_error():
    assert "ConnectionError" not in pyrogram.Client.restart.__doc__


def test_invoice_photo_url():
    from pyrogram import raw, types

    photo = raw.types.WebDocument(
        url="https://example.com/p.jpg",
        access_hash=1,
        size=1,
        mime_type="image/jpeg",
        attributes=[],
    )
    media = raw.types.MessageMediaInvoice(
        title="t", description="d", currency="USD", total_amount=100, start_param="", photo=photo
    )
    assert types.Invoice._parse(None, media).photo_url == "https://example.com/p.jpg"
    assert (
        types.Invoice._parse(None, raw.types.Invoice(currency="XTR", prices=[])).photo_url is None
    )


def _roundtrip(obj):
    return raw.core.TLObject.read(BytesIO(obj.write()))


async def _received_rich_message(client, part=False):
    blocks = [
        raw.types.PageBlockParagraph(
            text=raw.types.TextConcat(
                texts=[
                    raw.types.TextPlain(text="Hi "),
                    raw.types.TextMentionName(text=raw.types.TextPlain(text="you"), user_id=111),
                ]
            )
        )
    ]
    photo = raw.types.Photo(id=5, access_hash=6, file_reference=b"r", date=0, sizes=[], dc_id=2)
    rich = raw.types.RichMessage(blocks=blocks, photos=[photo], documents=[], part=part)
    users = {111: _roundtrip(raw.types.User(id=111, access_hash=9, first_name="Ann"))}
    return blocks, await types.RichMessage._parse(client, rich, users, {})


@pytest.mark.parametrize("partial", [False, True])
async def test_a_received_rich_message_can_be_copied(partial):
    from pyrogram import utils

    client = pyrogram.Client("rich", api_id=1, api_hash="x", in_memory=True)
    blocks, rich = await _received_rich_message(client, part=partial)
    full_blocks, full = await _received_rich_message(client)
    sent, fetched = [], []

    async def send_rich_message(chat_id, **kwargs):
        sent.append(await utils.build_input_rich_message(client, kwargs["rich_text"]))
        return "copied"

    async def get_rich_message(chat_id, message_id):
        fetched.append((chat_id, message_id))
        return SimpleNamespace(rich_message=full)

    client.send_rich_message = send_rich_message
    client.get_rich_message = get_rich_message
    message = types.Message(
        id=7,
        chat=types.Chat(id=-1001, type=enums.ChatType.SUPERGROUP),
        rich_message=rich,
        client=client,
    )

    assert await message.copy(42) == "copied"
    assert fetched == ([(-1001, 7)] if partial else [])
    assert sent[0].blocks == (full_blocks if partial else blocks)
    assert sent[0].photos == [raw.types.InputPhoto(id=5, access_hash=6, file_reference=b"r")]
    assert sent[0].users == [raw.types.InputUser(user_id=111, access_hash=9)]
