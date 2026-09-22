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
async def test_set_bot_default_privileges_calls_channel_and_group():
    from pyrogram.methods.bots.set_bot_default_privileges import SetBotDefaultPrivileges

    class _Client(_Recorder, SetBotDefaultPrivileges):
        pass

    # Group branch
    client_group = _Client(result=True)
    res_group = await client_group.set_bot_default_privileges(for_channels=False)
    assert res_group is True
    assert len(client_group.calls) == 1
    assert isinstance(client_group.calls[0], raw.functions.bots.SetBotGroupDefaultAdminRights)

    # Channel branch
    client_channel = _Client(result=True)
    res_channel = await client_channel.set_bot_default_privileges(for_channels=True)
    assert res_channel is True
    assert len(client_channel.calls) == 1
    assert isinstance(client_channel.calls[0], raw.functions.bots.SetBotBroadcastDefaultAdminRights)


@pytest.mark.asyncio
async def test_add_bot_preview_media_dispatches_query():
    from pyrogram.methods.bots.add_bot_preview_media import AddBotPreviewMedia

    media = raw.types.InputMediaEmpty()

    class _Client(_Recorder, AddBotPreviewMedia):
        pass

    client = _Client(result=raw.types.BotPreviewMedia(date=0, media=raw.types.MessageMediaEmpty()))
    res = await client.add_bot_preview_media("my_bot", "en", media)

    assert isinstance(res, raw.types.BotPreviewMedia)
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.AddPreviewMedia)
    assert call.lang_code == "en"
    assert call.media == media


@pytest.mark.asyncio
async def test_delete_bot_preview_media_dispatches_query():
    from pyrogram.methods.bots.delete_bot_preview_media import DeleteBotPreviewMedia

    media = [raw.types.InputMediaEmpty()]

    class _Client(_Recorder, DeleteBotPreviewMedia):
        pass

    client = _Client(result=True)
    res = await client.delete_bot_preview_media("my_bot", "en", media)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.DeletePreviewMedia)
    assert call.lang_code == "en"
    assert call.media == media


@pytest.mark.asyncio
async def test_edit_bot_preview_media_dispatches_query():
    from pyrogram.methods.bots.edit_bot_preview_media import EditBotPreviewMedia

    old_media = raw.types.InputMediaEmpty()
    new_media = raw.types.InputMediaEmpty()

    class _Client(_Recorder, EditBotPreviewMedia):
        pass

    client = _Client(result=raw.types.BotPreviewMedia(date=0, media=raw.types.MessageMediaEmpty()))
    res = await client.edit_bot_preview_media("my_bot", "en", old_media, new_media)

    assert isinstance(res, raw.types.BotPreviewMedia)
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.EditPreviewMedia)
    assert call.lang_code == "en"
    assert call.media == old_media
    assert call.new_media == new_media


@pytest.mark.asyncio
async def test_get_bot_preview_info_dispatches_query():
    from pyrogram.methods.bots.get_bot_preview_info import GetBotPreviewInfo

    dummy_info = raw.types.bots.PreviewInfo(media=[], lang_codes=[])

    class _Client(_Recorder, GetBotPreviewInfo):
        pass

    client = _Client(result=dummy_info)
    res = await client.get_bot_preview_info("my_bot", "en")

    assert res == dummy_info
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.GetPreviewInfo)
    assert call.lang_code == "en"


@pytest.mark.asyncio
async def test_get_bot_preview_medias_dispatches_query():
    from pyrogram.methods.bots.get_bot_preview_medias import GetBotPreviewMedias

    class _Client(_Recorder, GetBotPreviewMedias):
        pass

    client = _Client(result=[])
    res = await client.get_bot_preview_medias("my_bot")

    assert res == []
    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.bots.GetPreviewMedias)


@pytest.mark.asyncio
async def test_reorder_bot_preview_medias_dispatches_query():
    from pyrogram.methods.bots.reorder_bot_preview_medias import ReorderBotPreviewMedias

    order = [raw.types.InputMediaEmpty()]

    class _Client(_Recorder, ReorderBotPreviewMedias):
        pass

    client = _Client(result=True)
    res = await client.reorder_bot_preview_medias("my_bot", "en", order)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.ReorderPreviewMedias)
    assert call.lang_code == "en"
    assert call.order == order


@pytest.mark.asyncio
async def test_toggle_bot_username_dispatches_query():
    from pyrogram.methods.bots.toggle_bot_username import ToggleBotUsername

    class _Client(_Recorder, ToggleBotUsername):
        pass

    client = _Client(result=True)
    res = await client.toggle_bot_username("my_bot", "cool_bot", True)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.ToggleUsername)
    assert call.username == "cool_bot"
    assert call.active is True


@pytest.mark.asyncio
async def test_reorder_bot_usernames_dispatches_query():
    from pyrogram.methods.bots.reorder_bot_usernames import ReorderBotUsernames

    order = ["user1_bot", "user2_bot"]

    class _Client(_Recorder, ReorderBotUsernames):
        pass

    client = _Client(result=True)
    res = await client.reorder_bot_usernames("my_bot", order)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.ReorderUsernames)
    assert call.order == order


@pytest.mark.asyncio
async def test_toggle_user_emoji_status_permission_dispatches_query():
    from pyrogram.methods.bots.toggle_user_emoji_status_permission import (
        ToggleUserEmojiStatusPermission,
    )

    class _Client(_Recorder, ToggleUserEmojiStatusPermission):
        pass

    client = _Client(result=True)
    res = await client.toggle_user_emoji_status_permission("my_bot", True)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.ToggleUserEmojiStatusPermission)
    assert call.enabled is True


@pytest.mark.asyncio
async def test_update_user_emoji_status_dispatches_query():
    from pyrogram.methods.bots.update_user_emoji_status import UpdateUserEmojiStatus

    status = raw.types.EmojiStatus(document_id=123)

    class _Client(_Recorder, UpdateUserEmojiStatus):
        pass

    client = _Client(result=True)
    res = await client.update_user_emoji_status(12345, status)

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.UpdateUserEmojiStatus)
    assert call.emoji_status == status


@pytest.mark.asyncio
async def test_update_star_ref_program_dispatches_query():
    from pyrogram.methods.bots.update_star_ref_program import UpdateStarRefProgram

    dummy_program = raw.types.StarRefProgram(
        bot_id=123,
        commission_permille=50,
        duration_months=12,
    )

    class _Client(_Recorder, UpdateStarRefProgram):
        pass

    client = _Client(result=dummy_program)
    res = await client.update_star_ref_program("my_bot", commission_permille=50, duration_months=12)

    assert res == dummy_program
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.UpdateStarRefProgram)
    assert call.commission_permille == 50
    assert call.duration_months == 12


@pytest.mark.asyncio
async def test_answer_webhook_json_query_dispatches_query():
    from pyrogram.methods.bots.answer_webhook_json_query import AnswerWebhookJSONQuery

    class _Client(_Recorder, AnswerWebhookJSONQuery):
        pass

    client = _Client(result=True)
    res = await client.answer_webhook_json_query(123456, '{"status": "ok"}')

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.AnswerWebhookJSONQuery)
    assert call.query_id == 123456
    assert isinstance(call.data, raw.types.DataJSON)
    assert call.data.data == '{"status": "ok"}'


@pytest.mark.asyncio
async def test_send_custom_request_dispatches_query():
    from pyrogram.methods.bots.send_custom_request import SendCustomRequest

    res_json = raw.types.DataJSON(data='{"result": "success"}')

    class _Client(_Recorder, SendCustomRequest):
        pass

    client = _Client(result=res_json)
    res = await client.send_custom_request("myCustomMethod", '{"param": 1}')

    assert res == res_json
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.SendCustomRequest)
    assert call.custom_method == "myCustomMethod"
    assert isinstance(call.params, raw.types.DataJSON)
    assert call.params.data == '{"param": 1}'


@pytest.mark.asyncio
async def test_check_download_file_params_dispatches_query():
    from pyrogram.methods.bots.check_download_file_params import CheckDownloadFileParams

    class _Client(_Recorder, CheckDownloadFileParams):
        pass

    client = _Client(result=True)
    res = await client.check_download_file_params(
        "my_bot", "file.pdf", "https://example.com/file.pdf"
    )

    assert res is True
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.CheckDownloadFileParams)
    assert call.file_name == "file.pdf"
    assert call.url == "https://example.com/file.pdf"


@pytest.mark.asyncio
async def test_get_bot_recommendations_dispatches_query():
    from pyrogram.methods.bots.get_bot_recommendations import GetBotRecommendations

    dummy_users = raw.types.users.Users(users=[])

    class _Client(_Recorder, GetBotRecommendations):
        pass

    client = _Client(result=dummy_users)
    res = await client.get_bot_recommendations("my_bot")

    assert res == dummy_users
    assert len(client.calls) == 1
    assert isinstance(client.calls[0], raw.functions.bots.GetBotRecommendations)


@pytest.mark.asyncio
async def test_get_popular_app_bots_dispatches_query():
    from pyrogram.methods.bots.get_popular_app_bots import GetPopularAppBots

    dummy_apps = raw.types.bots.PopularAppBots(next_offset="off2", users=[])

    class _Client(_Recorder, GetPopularAppBots):
        pass

    client = _Client(result=dummy_apps)
    res = await client.get_popular_app_bots(offset="off1", limit=10)

    assert res == dummy_apps
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.GetPopularAppBots)
    assert call.offset == "off1"
    assert call.limit == 10


@pytest.mark.asyncio
async def test_get_requested_web_view_button_dispatches_query():
    from pyrogram.methods.bots.get_requested_web_view_button import GetRequestedWebViewButton

    btn = raw.types.KeyboardButton(text="Test", type=raw.types.ButtonTypeDefault())

    class _Client(_Recorder, GetRequestedWebViewButton):
        pass

    client = _Client(result=btn)
    res = await client.get_requested_web_view_button("my_bot", "req_999")

    assert res == btn
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.GetRequestedWebViewButton)
    assert call.webapp_req_id == "req_999"


@pytest.mark.asyncio
async def test_request_web_view_button_dispatches_query():
    from pyrogram.methods.bots.request_web_view_button import RequestWebViewButton

    btn = raw.types.KeyboardButton(text="Test", type=raw.types.ButtonTypeDefault())
    dummy_res = raw.types.bots.RequestedButton(webapp_req_id="req_123")

    class _Client(_Recorder, RequestWebViewButton):
        pass

    client = _Client(result=dummy_res)
    res = await client.request_web_view_button(12345, btn)

    assert res == dummy_res
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.RequestWebViewButton)
    assert call.button == btn


@pytest.mark.asyncio
async def test_invoke_web_view_custom_method_dispatches_query():
    from pyrogram.methods.bots.invoke_web_view_custom_method import InvokeWebViewCustomMethod

    res_data = raw.types.DataJSON(data='{"status": 200}')

    class _Client(_Recorder, InvokeWebViewCustomMethod):
        pass

    client = _Client(result=res_data)
    res = await client.invoke_web_view_custom_method("my_bot", "calc", '{"a": 1}')

    assert res == res_data
    assert len(client.calls) == 1
    call = client.calls[0]
    assert isinstance(call, raw.functions.bots.InvokeWebViewCustomMethod)
    assert call.custom_method == "calc"
    assert isinstance(call.params, raw.types.DataJSON)
    assert call.params.data == '{"a": 1}'


def test_client_has_all_new_bots_methods():
    client_methods = dir(pyrogram.Client)
    expected_methods = [
        "set_bot_default_privileges",
        "add_bot_preview_media",
        "delete_bot_preview_media",
        "edit_bot_preview_media",
        "get_bot_preview_info",
        "get_bot_preview_medias",
        "reorder_bot_preview_medias",
        "toggle_bot_username",
        "reorder_bot_usernames",
        "toggle_user_emoji_status_permission",
        "update_user_emoji_status",
        "update_star_ref_program",
        "answer_webhook_json_query",
        "send_custom_request",
        "check_download_file_params",
        "get_bot_recommendations",
        "get_popular_app_bots",
        "get_requested_web_view_button",
        "request_web_view_button",
        "invoke_web_view_custom_method",
    ]
    for method in expected_methods:
        assert method in client_methods, f"Client is missing method: {method}"
