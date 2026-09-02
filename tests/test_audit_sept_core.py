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
