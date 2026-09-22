import pytest

import pyrogram
from pyrogram import raw


class _Recorder:
    def __init__(self, result=True):
        self.calls = []
        self.result = result

    async def invoke(self, query, *args, **kwargs):
        self.calls.append(query)
        return self.result


@pytest.mark.asyncio
async def test_create_ai_tone_dispatches_query():
    from pyrogram.methods.aicompose.create_ai_tone import CreateAITone

    dummy_tone = raw.types.AiComposeTone(
        id=1,
        access_hash=12345,
        slug="pirate",
        title="Pirate",
        prompt="Speak like a pirate",
        emoji_id=12345,
    )

    class _Client(_Recorder, CreateAITone):
        pass

    client = _Client(result=dummy_tone)
    res = await client.create_ai_tone(
        title="Pirate",
        prompt="Speak like a pirate",
        emoji_id=12345,
        display_author=True,
    )

    assert res == dummy_tone
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.aicompose.CreateTone)
    assert call.title == "Pirate"
    assert call.prompt == "Speak like a pirate"
    assert call.emoji_id == 12345
    assert call.display_author is True


@pytest.mark.asyncio
async def test_get_ai_tones_dispatches_query():
    from pyrogram.methods.aicompose.get_ai_tones import GetAITones

    dummy_tones = raw.types.aicompose.Tones(
        hash=42,
        tones=[],
        users=[],
    )

    class _Client(_Recorder, GetAITones):
        pass

    client = _Client(result=dummy_tones)
    res = await client.get_ai_tones(hash=42)

    assert res == dummy_tones
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.aicompose.GetTones)
    assert call.hash == 42


@pytest.mark.asyncio
async def test_get_ai_tone_dispatches_query():
    from pyrogram.methods.aicompose.get_ai_tone import GetAITone

    dummy_tones = raw.types.aicompose.Tones(
        hash=0,
        tones=[],
        users=[],
    )
    input_tone = raw.types.InputAiComposeToneID(id=1, access_hash=12345)

    class _Client(_Recorder, GetAITone):
        pass

    client = _Client(result=dummy_tones)
    res = await client.get_ai_tone(input_tone)

    assert res == dummy_tones
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.aicompose.GetTone)
    assert call.tone == input_tone


@pytest.mark.asyncio
async def test_get_ai_tone_example_dispatches_query():
    from pyrogram.methods.aicompose.get_ai_tone_example import GetAIToneExample

    dummy_example = raw.types.AiComposeToneExample(
        from_peer=raw.types.TextWithEntities(text="Hello", entities=[]),
        to=raw.types.TextWithEntities(text="Ahoy matey!", entities=[]),
    )
    input_tone = raw.types.InputAiComposeToneID(id=1, access_hash=12345)

    class _Client(_Recorder, GetAIToneExample):
        pass

    client = _Client(result=dummy_example)
    res = await client.get_ai_tone_example(input_tone, example_number=2)

    assert res == dummy_example
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.aicompose.GetToneExample)
    assert call.tone == input_tone
    assert call.num == 2


@pytest.mark.asyncio
async def test_update_ai_tone_dispatches_query():
    from pyrogram.methods.aicompose.update_ai_tone import UpdateAITone

    dummy_tone = raw.types.AiComposeTone(
        id=1,
        access_hash=12345,
        slug="pirate",
        title="Pirate Updated",
        prompt="Arr matey!",
        emoji_id=999,
    )
    input_tone = raw.types.InputAiComposeToneID(id=1, access_hash=12345)

    class _Client(_Recorder, UpdateAITone):
        pass

    client = _Client(result=dummy_tone)
    res = await client.update_ai_tone(
        tone=input_tone,
        title="Pirate Updated",
        prompt="Arr matey!",
        emoji_id=999,
        display_author=False,
    )

    assert res == dummy_tone
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.aicompose.UpdateTone)
    assert call.tone == input_tone
    assert call.title == "Pirate Updated"
    assert call.prompt == "Arr matey!"
    assert call.emoji_id == 999
    assert call.display_author is False


@pytest.mark.asyncio
async def test_save_ai_tone_dispatches_query():
    from pyrogram.methods.aicompose.save_ai_tone import SaveAITone

    input_tone = raw.types.InputAiComposeToneID(id=1, access_hash=12345)

    class _Client(_Recorder, SaveAITone):
        pass

    client = _Client(result=True)

    # Save
    res = await client.save_ai_tone(input_tone)
    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.aicompose.SaveTone)
    assert call.tone == input_tone
    assert call.unsave is False

    # Unsave
    res_unsave = await client.save_ai_tone(input_tone, unsave=True)
    assert res_unsave is True
    assert len(client.calls) == 2
    call_unsave = client.calls[1]
    assert isinstance(call_unsave, raw.functions.aicompose.SaveTone)
    assert call_unsave.tone == input_tone
    assert call_unsave.unsave is True


@pytest.mark.asyncio
async def test_delete_ai_tone_dispatches_query():
    from pyrogram.methods.aicompose.delete_ai_tone import DeleteAITone

    input_tone = raw.types.InputAiComposeToneID(id=1, access_hash=12345)

    class _Client(_Recorder, DeleteAITone):
        pass

    client = _Client(result=True)
    res = await client.delete_ai_tone(input_tone)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.aicompose.DeleteTone)
    assert call.tone == input_tone


def test_client_has_all_aicompose_methods():
    client_methods = dir(pyrogram.Client)
    expected_methods = [
        "create_ai_tone",
        "get_ai_tones",
        "get_ai_tone",
        "get_ai_tone_example",
        "update_ai_tone",
        "save_ai_tone",
        "delete_ai_tone",
    ]
    for method in expected_methods:
        assert method in client_methods, f"Client is missing method: {method}"
