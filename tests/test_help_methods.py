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

    async def resolve_peer(self, peer_id):
        if peer_id == "me":
            return raw.types.InputPeerSelf()
        uid = int(peer_id) if isinstance(peer_id, int) else 12345
        return raw.types.InputPeerUser(user_id=uid, access_hash=0)


@pytest.mark.asyncio
async def test_dismiss_suggestion_dispatches_query():
    from pyrogram.methods.help.dismiss_suggestion import DismissSuggestion

    class _Client(_Recorder, DismissSuggestion):
        pass

    client = _Client(result=True)
    res = await client.dismiss_suggestion(12345, "suggestion_key")

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.DismissSuggestion)
    assert call.suggestion == "suggestion_key"


@pytest.mark.asyncio
async def test_edit_user_info_dispatches_query():
    from pyrogram.methods.help.edit_user_info import EditUserInfo

    class _Client(_Recorder, EditUserInfo):
        pass

    dummy_info = raw.types.help.UserInfo(
        message="TSF info",
        entities=[],
        author="TSF",
        date=0,
    )
    client = _Client(result=dummy_info)
    res = await client.edit_user_info(12345, "TSF info")

    assert res == dummy_info
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.EditUserInfo)
    assert call.message == "TSF info"


@pytest.mark.asyncio
async def test_get_app_config_dispatches_query():
    from pyrogram.methods.help.get_app_config import GetAppConfig

    class _Client(_Recorder, GetAppConfig):
        pass

    dummy_cfg = raw.types.help.AppConfig(
        hash=123,
        config=raw.types.DataJSON(data="{}"),
    )
    client = _Client(result=dummy_cfg)
    res = await client.get_app_config(hash=123)

    assert res == dummy_cfg
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetAppConfig)
    assert call.hash == 123


@pytest.mark.asyncio
async def test_get_app_update_dispatches_query():
    from pyrogram.methods.help.get_app_update import GetAppUpdate

    class _Client(_Recorder, GetAppUpdate):
        pass

    dummy_upd = raw.types.help.NoAppUpdate()
    client = _Client(result=dummy_upd)
    res = await client.get_app_update("google_play")

    assert res == dummy_upd
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetAppUpdate)
    assert call.source == "google_play"


@pytest.mark.asyncio
async def test_get_cdn_config_dispatches_query():
    from pyrogram.methods.help.get_cdn_config import GetCdnConfig

    class _Client(_Recorder, GetCdnConfig):
        pass

    dummy_cdn = raw.types.CdnConfig(public_keys=[])
    client = _Client(result=dummy_cdn)
    res = await client.get_cdn_config()

    assert res == dummy_cdn
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetCdnConfig)


@pytest.mark.asyncio
async def test_get_countries_list_dispatches_query():
    from pyrogram.methods.help.get_countries_list import GetCountriesList

    class _Client(_Recorder, GetCountriesList):
        pass

    dummy_countries = raw.types.help.CountriesList(countries=[], hash=0)
    client = _Client(result=dummy_countries)
    res = await client.get_countries_list(lang_code="en", hash=0)

    assert res == dummy_countries
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetCountriesList)
    assert call.lang_code == "en"


@pytest.mark.asyncio
async def test_get_deep_link_info_dispatches_query():
    from pyrogram.methods.help.get_deep_link_info import GetDeepLinkInfo

    class _Client(_Recorder, GetDeepLinkInfo):
        pass

    dummy_info = raw.types.help.DeepLinkInfo(
        update_app=False,
        message="Info",
        entities=[],
    )
    client = _Client(result=dummy_info)
    res = await client.get_deep_link_info("some_path")

    assert res == dummy_info
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetDeepLinkInfo)
    assert call.path == "some_path"


@pytest.mark.asyncio
async def test_get_invite_text_dispatches_query():
    from pyrogram.methods.help.get_invite_text import GetInviteText

    class _Client(_Recorder, GetInviteText):
        pass

    dummy_text = raw.types.help.InviteText(message="Join Telegram!")
    client = _Client(result=dummy_text)
    res = await client.get_invite_text()

    assert res == dummy_text
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetInviteText)


@pytest.mark.asyncio
async def test_get_nearest_dc_dispatches_query():
    from pyrogram.methods.help.get_nearest_dc import GetNearestDc

    class _Client(_Recorder, GetNearestDc):
        pass

    dummy_dc = raw.types.NearestDc(country="US", this_dc=2, nearest_dc=2)
    client = _Client(result=dummy_dc)
    res = await client.get_nearest_dc()

    assert res == dummy_dc
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetNearestDc)


@pytest.mark.asyncio
async def test_get_passport_config_dispatches_query():
    from pyrogram.methods.help.get_passport_config import GetPassportConfig

    class _Client(_Recorder, GetPassportConfig):
        pass

    dummy_cfg = raw.types.help.PassportConfig(hash=0, countries_langs=raw.types.DataJSON(data="{}"))
    client = _Client(result=dummy_cfg)
    res = await client.get_passport_config(hash=0)

    assert res == dummy_cfg
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetPassportConfig)


@pytest.mark.asyncio
async def test_get_peer_colors_dispatches_query():
    from pyrogram.methods.help.get_peer_colors import GetPeerColors

    class _Client(_Recorder, GetPeerColors):
        pass

    dummy_colors = raw.types.help.PeerColors(hash=0, colors=[])
    client = _Client(result=dummy_colors)
    res = await client.get_peer_colors()

    assert res == dummy_colors
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetPeerColors)


@pytest.mark.asyncio
async def test_get_peer_profile_colors_dispatches_query():
    from pyrogram.methods.help.get_peer_profile_colors import GetPeerProfileColors

    class _Client(_Recorder, GetPeerProfileColors):
        pass

    dummy_colors = raw.types.help.PeerColors(hash=0, colors=[])
    client = _Client(result=dummy_colors)
    res = await client.get_peer_profile_colors()

    assert res == dummy_colors
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetPeerProfileColors)


@pytest.mark.asyncio
async def test_get_premium_promo_dispatches_query():
    from pyrogram.methods.help.get_premium_promo import GetPremiumPromo

    class _Client(_Recorder, GetPremiumPromo):
        pass

    dummy_promo = raw.types.help.PremiumPromo(
        status_text="Premium",
        status_entities=[],
        video_sections=[],
        videos=[],
        period_options=[],
        users=[],
    )
    client = _Client(result=dummy_promo)
    res = await client.get_premium_promo()

    assert res == dummy_promo
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetPremiumPromo)


@pytest.mark.asyncio
async def test_get_promo_data_dispatches_query():
    from pyrogram.methods.help.get_promo_data import GetPromoData

    class _Client(_Recorder, GetPromoData):
        pass

    dummy_promo = raw.types.help.PromoDataEmpty(expires=0)
    client = _Client(result=dummy_promo)
    res = await client.get_promo_data()

    assert res == dummy_promo
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetPromoData)


@pytest.mark.asyncio
async def test_get_recent_me_urls_dispatches_query():
    from pyrogram.methods.help.get_recent_me_urls import GetRecentMeUrls

    class _Client(_Recorder, GetRecentMeUrls):
        pass

    dummy_urls = raw.types.help.RecentMeUrls(urls=[], chats=[], users=[])
    client = _Client(result=dummy_urls)
    res = await client.get_recent_me_urls(referer="https://google.com")

    assert res == dummy_urls
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetRecentMeUrls)
    assert call.referer == "https://google.com"


@pytest.mark.asyncio
async def test_get_support_dispatches_query():
    from pyrogram.methods.help.get_support import GetSupport

    class _Client(_Recorder, GetSupport):
        pass

    dummy_user = raw.types.User(
        id=123,
        is_self=False,
        contact=False,
        mutual_contact=False,
        deleted=False,
        bot=False,
        bot_chat_history=False,
        bot_nochats=False,
        verified=False,
        restricted=False,
        min=False,
        bot_inline_geo=False,
        support=True,
        scam=False,
        apply_min_photo=False,
        fake=False,
        bot_attach_menu=False,
        premium=False,
        attach_menu_enabled=False,
        bot_can_edit=False,
        close_friend=False,
        stories_hidden=False,
        stories_unavailable=False,
        contact_require_premium=False,
        bot_business=False,
        bot_has_main_app=False,
    )
    dummy_sup = raw.types.help.Support(user=dummy_user, phone_number="+1234567890")
    client = _Client(result=dummy_sup)
    res = await client.get_support()

    assert res == dummy_sup
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetSupport)


@pytest.mark.asyncio
async def test_get_support_name_dispatches_query():
    from pyrogram.methods.help.get_support_name import GetSupportName

    class _Client(_Recorder, GetSupportName):
        pass

    dummy_name = raw.types.help.SupportName(name="Telegram Support")
    client = _Client(result=dummy_name)
    res = await client.get_support_name()

    assert res == dummy_name
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetSupportName)


@pytest.mark.asyncio
async def test_get_terms_of_service_update_dispatches_query():
    from pyrogram.methods.help.get_terms_of_service_update import GetTermsOfServiceUpdate

    class _Client(_Recorder, GetTermsOfServiceUpdate):
        pass

    dummy_tos = raw.types.help.TermsOfServiceUpdateEmpty(expires=0)
    client = _Client(result=dummy_tos)
    res = await client.get_terms_of_service_update()

    assert res == dummy_tos
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetTermsOfServiceUpdate)


@pytest.mark.asyncio
async def test_get_timezones_list_dispatches_query():
    from pyrogram.methods.help.get_timezones_list import GetTimezonesList

    class _Client(_Recorder, GetTimezonesList):
        pass

    dummy_tz = raw.types.help.TimezonesList(timezones=[], hash=0)
    client = _Client(result=dummy_tz)
    res = await client.get_timezones_list()

    assert res == dummy_tz
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetTimezonesList)


@pytest.mark.asyncio
async def test_get_user_info_dispatches_query():
    from pyrogram.methods.help.get_user_info import GetUserInfo

    class _Client(_Recorder, GetUserInfo):
        pass

    dummy_info = raw.types.help.UserInfoEmpty()
    client = _Client(result=dummy_info)
    res = await client.get_user_info(12345)

    assert res == dummy_info
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.GetUserInfo)


@pytest.mark.asyncio
async def test_hide_promo_data_dispatches_query():
    from pyrogram.methods.help.hide_promo_data import HidePromoData

    class _Client(_Recorder, HidePromoData):
        pass

    client = _Client(result=True)
    res = await client.hide_promo_data(12345)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.HidePromoData)


@pytest.mark.asyncio
async def test_save_app_log_dispatches_query():
    from pyrogram.methods.help.save_app_log import SaveAppLog

    class _Client(_Recorder, SaveAppLog):
        pass

    client = _Client(result=True)
    dummy_event = raw.types.InputAppEvent(
        time=0.0,
        type="click",
        peer=0,
        data=raw.types.DataJSON(data="{}"),
    )
    res = await client.save_app_log([dummy_event])

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.SaveAppLog)
    assert call.events == [dummy_event]


@pytest.mark.asyncio
async def test_set_bot_updates_status_dispatches_query():
    from pyrogram.methods.help.set_bot_updates_status import SetBotUpdatesStatus

    class _Client(_Recorder, SetBotUpdatesStatus):
        pass

    client = _Client(result=True)
    res = await client.set_bot_updates_status(10, "Pending")

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.help.SetBotUpdatesStatus)
    assert call.pending_updates_count == 10
    assert call.message == "Pending"


def test_client_has_help_methods():
    assert hasattr(pyrogram.Client, "dismiss_suggestion")
    assert hasattr(pyrogram.Client, "edit_user_info")
    assert hasattr(pyrogram.Client, "get_app_config")
    assert hasattr(pyrogram.Client, "get_app_update")
    assert hasattr(pyrogram.Client, "get_cdn_config")
    assert hasattr(pyrogram.Client, "get_countries_list")
    assert hasattr(pyrogram.Client, "get_deep_link_info")
    assert hasattr(pyrogram.Client, "get_invite_text")
    assert hasattr(pyrogram.Client, "get_nearest_dc")
    assert hasattr(pyrogram.Client, "get_passport_config")
    assert hasattr(pyrogram.Client, "get_peer_colors")
    assert hasattr(pyrogram.Client, "get_peer_profile_colors")
    assert hasattr(pyrogram.Client, "get_premium_promo")
    assert hasattr(pyrogram.Client, "get_promo_data")
    assert hasattr(pyrogram.Client, "get_recent_me_urls")
    assert hasattr(pyrogram.Client, "get_support")
    assert hasattr(pyrogram.Client, "get_support_name")
    assert hasattr(pyrogram.Client, "get_terms_of_service_update")
    assert hasattr(pyrogram.Client, "get_timezones_list")
    assert hasattr(pyrogram.Client, "get_user_info")
    assert hasattr(pyrogram.Client, "hide_promo_data")
    assert hasattr(pyrogram.Client, "save_app_log")
    assert hasattr(pyrogram.Client, "set_bot_updates_status")
