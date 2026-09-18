import pytest
from unittest.mock import AsyncMock, MagicMock

import pyrogram
from pyrogram import raw, types


@pytest.mark.asyncio
async def test_client_no_joined_notifications_default():
    app = pyrogram.Client("test_no_joined_default", no_joined_notifications=True)
    assert app.no_joined_notifications is True


@pytest.mark.asyncio
async def test_sign_up_passes_no_joined_notifications():
    app = pyrogram.Client("test_sign_up_notifications", no_joined_notifications=True)

    mock_user = raw.types.User(
        id=1234567,
        is_self=True,
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
        support=False,
        scam=False,
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
        first_name="Test",
        last_name="User",
        access_hash=0,
        usernames=[],
        restriction_reason=[],
        status=None,
        color=None,
        profile_color=None,
        photo=None,
        emoji_status=None,
        lang_code=None,
        phone="1234567890",
        bot_active_users=None,
        bot_inline_placeholder=None,
        bot_forum_view=None,
        bot_forum_can_manage_topics=None,
        send_paid_messages_stars=None,
        bot_guestchat=None,
        bot_guard=None,
        bot_can_manage_bots=None,
        username=None,
    )
    auth_result = raw.types.auth.Authorization(user=mock_user)

    captured_queries = []

    async def mock_invoke(query, *args, **kwargs):
        captured_queries.append(query)
        return auth_result

    app.invoke = mock_invoke
    app.storage = MagicMock()
    app.storage.user_id = AsyncMock()
    app.storage.is_bot = AsyncMock()

    user = await app.sign_up(
        phone_number="+1234567890",
        phone_code_hash="hash123",
        first_name="Test",
        last_name="User",
    )

    assert isinstance(user, types.User)
    assert len(captured_queries) == 1
    query = captured_queries[0]
    assert isinstance(query, raw.functions.auth.SignUp)
    assert query.phone_number == "1234567890"
    assert query.first_name == "Test"
    assert query.last_name == "User"
    assert query.no_joined_notifications is True

    captured_queries.clear()
    await app.sign_up(
        phone_number="+1234567890",
        phone_code_hash="hash123",
        first_name="Test",
        last_name="User",
        no_joined_notifications=False,
    )
    assert len(captured_queries) == 1
    assert captured_queries[0].no_joined_notifications is False
