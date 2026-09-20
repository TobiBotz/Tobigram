from unittest.mock import Mock

import pytest

import pyrogram
from pyrogram import raw, types


class FakeMessagesClient(pyrogram.Client):
    def __init__(self):
        self.sent_queries = []
        self.me = Mock(id=111, is_bot=False)
        self.lang_code = "en"
        self.parse_mode = pyrogram.enums.ParseMode.DEFAULT
        self.parser = pyrogram.parser.Parser(self)

    async def invoke(self, query, **kwargs):
        self.sent_queries.append(query)

        if isinstance(query, raw.functions.messages.ComposeMessageWithAI):
            return raw.types.messages.ComposedMessageWithAI(
                result_text=raw.types.TextWithEntities(
                    text=f"AI({query.text.text})",
                    entities=[],
                )
            )

        raise NotImplementedError(f"Unhandled query {query}")


@pytest.mark.asyncio
async def test_emojify_text_with_ai():
    app = FakeMessagesClient()

    res = await app.emojify_text_with_ai("Hello world!")
    assert isinstance(res, types.FormattedText)
    assert res.text == "AI(Hello world!)"

    q = app.sent_queries[-1]
    assert isinstance(q, raw.functions.messages.ComposeMessageWithAI)
    assert q.emojify is True
    assert not q.proofread
    assert q.translate_to_lang is None
    assert q.tone is None


@pytest.mark.asyncio
async def test_rephrase_text_with_ai():
    app = FakeMessagesClient()

    # With string tone
    res = await app.rephrase_text_with_ai("Hey there", tone="casual")
    assert isinstance(res, types.FormattedText)
    assert res.text == "AI(Hey there)"

    q = app.sent_queries[-1]
    assert isinstance(q, raw.functions.messages.ComposeMessageWithAI)
    assert isinstance(q.tone, raw.types.InputAiComposeToneDefault)
    assert q.tone.tone == "casual"
    assert not q.emojify
    assert q.translate_to_lang is None

    # With raw tone object
    custom_tone = raw.types.InputAiComposeToneDefault(tone="poetic")
    await app.rephrase_text_with_ai("Sunset is beautiful", tone=custom_tone)
    q2 = app.sent_queries[-1]
    assert q2.tone == custom_tone


@pytest.mark.asyncio
async def test_compose_text_with_ai_no_forced_translation():
    app = FakeMessagesClient()

    # Without translation language
    await app.compose_text_with_ai("Bonjour", add_emojis=True, style_name="friendly")
    q1 = app.sent_queries[-1]
    assert q1.translate_to_lang is None
    assert q1.emojify is True
    assert isinstance(q1.tone, raw.types.InputAiComposeToneDefault)
    assert q1.tone.tone == "friendly"

    # With explicit translation language
    await app.compose_text_with_ai("Hello", translate_to_language_code="es")
    q2 = app.sent_queries[-1]
    assert q2.translate_to_lang == "es"
