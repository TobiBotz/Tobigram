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
async def test_get_difference_dispatches_query():
    from pyrogram.methods.langpack.get_difference import GetDifference

    class _Client(_Recorder, GetDifference):
        pass

    dummy_diff = raw.types.LangPackDifference(
        lang_code="en",
        from_version=0,
        version=1,
        strings=[],
    )
    client = _Client(result=dummy_diff)
    res = await client.get_difference("android", "en", 0)

    assert res == dummy_diff
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.langpack.GetDifference)
    assert call.lang_pack == "android"
    assert call.lang_code == "en"
    assert call.from_version == 0


@pytest.mark.asyncio
async def test_get_lang_pack_dispatches_query():
    from pyrogram.methods.langpack.get_lang_pack import GetLangPack

    class _Client(_Recorder, GetLangPack):
        pass

    dummy_diff = raw.types.LangPackDifference(
        lang_code="en",
        from_version=0,
        version=1,
        strings=[],
    )
    client = _Client(result=dummy_diff)
    res = await client.get_lang_pack("android", "en")

    assert res == dummy_diff
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.langpack.GetLangPack)
    assert call.lang_pack == "android"
    assert call.lang_code == "en"


@pytest.mark.asyncio
async def test_get_language_dispatches_query():
    from pyrogram.methods.langpack.get_language import GetLanguage

    class _Client(_Recorder, GetLanguage):
        pass

    dummy_lang = raw.types.LangPackLanguage(
        name="English",
        native_name="English",
        lang_code="en",
        plural_code="en",
        strings_count=100,
        translated_count=100,
        translations_url="https://translations.telegram.org/en",
    )
    client = _Client(result=dummy_lang)
    res = await client.get_language("android", "en")

    assert res == dummy_lang
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.langpack.GetLanguage)
    assert call.lang_pack == "android"
    assert call.lang_code == "en"


@pytest.mark.asyncio
async def test_get_languages_dispatches_query():
    from pyrogram.methods.langpack.get_languages import GetLanguages

    class _Client(_Recorder, GetLanguages):
        pass

    dummy_langs = [
        raw.types.LangPackLanguage(
            name="English",
            native_name="English",
            lang_code="en",
            plural_code="en",
            strings_count=100,
            translated_count=100,
            translations_url="https://translations.telegram.org/en",
        )
    ]
    client = _Client(result=dummy_langs)
    res = await client.get_languages("android")

    assert res == dummy_langs
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.langpack.GetLanguages)
    assert call.lang_pack == "android"


@pytest.mark.asyncio
async def test_get_strings_dispatches_query():
    from pyrogram.methods.langpack.get_strings import GetStrings

    class _Client(_Recorder, GetStrings):
        pass

    dummy_strings = [raw.types.LangPackString(key="Cancel", value="Cancel")]
    client = _Client(result=dummy_strings)
    res = await client.get_strings("android", "en", ["Cancel"])

    assert res == dummy_strings
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.langpack.GetStrings)
    assert call.lang_pack == "android"
    assert call.lang_code == "en"
    assert call.keys == ["Cancel"]


def test_client_has_langpack_methods():
    assert hasattr(pyrogram.Client, "get_difference")
    assert hasattr(pyrogram.Client, "get_lang_pack")
    assert hasattr(pyrogram.Client, "get_language")
    assert hasattr(pyrogram.Client, "get_languages")
    assert hasattr(pyrogram.Client, "get_strings")
