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
