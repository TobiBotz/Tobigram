import datetime
import pytest

from pyrogram import Client, enums, filters
from pyrogram.handlers import ChatLeftHandler
from pyrogram.types import Chat, ChatMember, ChatMemberUpdated, User


def create_sample_update(
    old_status=enums.ChatMemberStatus.MEMBER,
    new_status=enums.ChatMemberStatus.LEFT,
    actor_id=123,
    user_id=123,
    new_member_none=False,
    old_member_none=False,
):
    target_user = User(id=user_id, first_name="TargetUser")
    actor = User(id=actor_id, first_name="ActorUser")
    chat = Chat(id=-1001234567890, type=enums.ChatType.SUPERGROUP, title="Test Group")

    old_member = None if old_member_none else ChatMember(status=old_status, user=target_user)
    new_member = None if new_member_none else ChatMember(status=new_status, user=target_user)

    return ChatMemberUpdated(
        chat=chat,
        from_user=actor,
        date=datetime.datetime.now(datetime.timezone.utc),
        old_chat_member=old_member,
        new_chat_member=new_member,
    )


class TestChatLeft:
    def test_properties_self_left(self):
        update = create_sample_update(
            old_status=enums.ChatMemberStatus.MEMBER,
            new_status=enums.ChatMemberStatus.LEFT,
            actor_id=123,
            user_id=123,
        )
        assert update.is_left is True
        assert update.is_self_left is True
        assert update.is_kicked is False
        assert update.user.id == 123
        assert update.left_chat_member.id == 123

    def test_properties_kicked_by_admin(self):
        update = create_sample_update(
            old_status=enums.ChatMemberStatus.MEMBER,
            new_status=enums.ChatMemberStatus.LEFT,
            actor_id=999,
            user_id=123,
        )
        assert update.is_left is True
        assert update.is_self_left is False
        assert update.is_kicked is True
        assert update.user.id == 123

    def test_properties_banned(self):
        update = create_sample_update(
            old_status=enums.ChatMemberStatus.MEMBER,
            new_status=enums.ChatMemberStatus.BANNED,
            actor_id=999,
            user_id=123,
        )
        assert update.is_left is True
        assert update.is_self_left is False
        assert update.is_kicked is True

    def test_properties_basic_group_left(self):
        # In basic groups, new_participant is None on leave
        update = create_sample_update(
            old_status=enums.ChatMemberStatus.MEMBER,
            actor_id=123,
            user_id=123,
            new_member_none=True,
        )
        assert update.is_left is True
        assert update.is_self_left is True
        assert update.user.id == 123

    def test_properties_new_member_join(self):
        # A new join is NOT a left event
        update = create_sample_update(
            old_status=enums.ChatMemberStatus.LEFT,
            new_status=enums.ChatMemberStatus.MEMBER,
            actor_id=123,
            user_id=123,
        )
        assert update.is_left is False
        assert update.is_self_left is False
        assert update.is_kicked is False
        assert update.left_chat_member is None

    def test_properties_new_member_join_none_old(self):
        update = create_sample_update(
            new_status=enums.ChatMemberStatus.MEMBER,
            actor_id=123,
            user_id=123,
            old_member_none=True,
        )
        assert update.is_left is False
        assert update.left_chat_member is None

    def test_properties_promoted_to_admin(self):
        # Promoting a member is NOT a left event
        update = create_sample_update(
            old_status=enums.ChatMemberStatus.MEMBER,
            new_status=enums.ChatMemberStatus.ADMINISTRATOR,
            actor_id=999,
            user_id=123,
        )
        assert update.is_left is False
        assert update.is_self_left is False
        assert update.is_kicked is False

    @pytest.mark.asyncio
    async def test_handler_check(self):
        async def dummy_callback(client, update):
            pass

        handler = ChatLeftHandler(dummy_callback)

        left_update = create_sample_update(new_status=enums.ChatMemberStatus.LEFT)
        join_update = create_sample_update(
            old_status=enums.ChatMemberStatus.LEFT, new_status=enums.ChatMemberStatus.MEMBER
        )

        assert await handler.check(None, left_update) is True
        assert await handler.check(None, join_update) is False

    @pytest.mark.asyncio
    async def test_handler_with_filter(self):
        async def dummy_callback(client, update):
            pass

        # Filter only chat with id -1001234567890
        chat_filter = filters.chat(-1001234567890)
        handler = ChatLeftHandler(dummy_callback, filters=chat_filter)

        left_update = create_sample_update(new_status=enums.ChatMemberStatus.LEFT)
        assert await handler.check(None, left_update) is True

        # Filter for a different chat
        diff_chat_filter = filters.chat(-1009999999999)
        diff_handler = ChatLeftHandler(dummy_callback, filters=diff_chat_filter)
        assert await diff_handler.check(None, left_update) is False

    def test_client_decorator_registration(self):
        client = Client("test_session", in_memory=True)

        @client.on_chat_left()
        async def on_left(c, u):
            pass

        handlers_in_group_0 = client.dispatcher.groups.get(0, [])
        left_handlers = [h for h in handlers_in_group_0 if isinstance(h, ChatLeftHandler)]
        assert len(left_handlers) == 1
        assert left_handlers[0].callback == on_left
