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
    users = {7: raw.types.User(
        id=7, first_name="U", usernames=[], restriction_reason=[], access_hash=1
    )}
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
    assert registry_module._identify(
        enums.ListenerTypes.MESSAGE, _message(chat_id=1, user_id=10, outgoing=True)
    ) is None
