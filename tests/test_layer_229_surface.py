#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

"""The Bot API 10.3 surface, which arrived with MTProto layer 229.

Every case here is a field or constructor that has one shape in Bot API and
another in the TL schema, which is the seam a parameter goes missing at.
"""

import ast
import inspect
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from pyrogram import enums, raw, types
from pyrogram.dispatcher import Dispatcher
from pyrogram.handlers import MessageGenerationStoppedHandler

ROOT = Path(__file__).resolve().parents[1]


def _raw_user(user_id, first_name="U"):
    return raw.types.User(
        id=user_id, first_name=first_name, usernames=[], restriction_reason=[]
    )


class TestRichMessageButton:
    """A rich button and a keyboard button are one MTProto union and two Bot API types."""

    def test_it_writes_a_page_button(self):
        button = types.RichMessageButton(text="Go", url="https://example.org")
        written = button.write()

        assert isinstance(written, raw.types.PageButton)
        assert isinstance(written.type, raw.types.InlineButtonTypeUrl)
        assert written.type.url == "https://example.org"

    def test_it_writes_a_text_button(self):
        written = types.RichMessageButton(text="Go", callback_data="d").write_text()

        assert isinstance(written, raw.types.TextButton)
        assert written.type.data == b"d"

    def test_a_login_url_needs_no_resolved_bot(self):
        """A rich block writes synchronously, and layer 229 made the bot optional."""

        written = types.RichMessageButton(
            text="Log in", login_url=types.LoginUrl(url="https://example.org")
        ).write()

        assert isinstance(written.type, raw.types.InputInlineButtonTypeUrlAuth)
        assert written.type.bot is None

    @pytest.mark.parametrize(
        "style,flag",
        [
            (enums.RichButtonStyle.LINK, "link"),
            (enums.RichButtonStyle.PRIMARY, "bg_primary"),
            (enums.RichButtonStyle.DANGER, "bg_danger"),
            (enums.RichButtonStyle.SUCCESS, "bg_success"),
        ],
    )
    def test_every_style_round_trips(self, style, flag):
        written = types.RichMessageButton(text="x", url="u", style=style).write()

        assert getattr(written.style, flag) is True
        assert types.RichMessageButton._parse_style(written.style) == style

    def test_the_default_style_writes_nothing(self):
        assert types.RichMessageButton(text="x", url="u").write().style is None
        assert (
            types.RichMessageButton._parse_style(None) == enums.RichButtonStyle.DEFAULT
        )

    async def test_it_parses_back(self):
        page_button = raw.types.PageButton(
            text=raw.types.TextPlain(text="Copy"),
            type=raw.types.InlineButtonTypeCopy(copy_text="hello"),
            style=raw.types.RichButtonStyle(bg_danger=True),
        )
        parsed = await types.RichMessageButton._parse(Mock(), page_button)

        assert parsed.text == "Copy"
        assert parsed.copy_text.text == "hello"
        assert parsed.style == enums.RichButtonStyle.DANGER

    async def test_a_keyboard_only_member_is_dropped_rather_than_passed_on(self):
        """RichMessageButton has no pay field, and the union it shares does."""

        page_button = raw.types.PageButton(
            text=raw.types.TextPlain(text="Buy"),
            type=raw.types.InlineButtonTypeBuy(),
        )

        parsed = await types.RichMessageButton._parse(Mock(), page_button)

        assert not hasattr(parsed, "pay")


class TestInstantViewBlocks:
    def test_a_button_row_carries_its_alignment(self):
        block = types.InputRichBlockButtons(
            buttons=[types.RichMessageButton(text="a", url="u")],
            align=enums.BlockAlignment.CENTER,
        ).write()

        assert isinstance(block, raw.types.PageBlockButtonRow)
        assert block.align_center is True
        assert block.align_left is None
        assert block.align_right is None

    def test_an_unaligned_row_sets_no_flag(self):
        block = types.InputRichBlockButtons(
            buttons=[types.RichMessageButton(text="a", url="u")]
        ).write()

        assert (block.align_left, block.align_center, block.align_right) == (
            None,
            None,
            None,
        )

    def test_an_expandable_quotation_is_a_collapsed_blockquote(self):
        block = types.InputRichBlockExpandableBlockQuotation(text="hi").write()

        assert isinstance(block, raw.types.PageBlockBlockquote)
        assert block.collapsed is True

    def test_a_plain_quotation_is_not_collapsed(self):
        block = types.InputRichBlockBlockQuotation(blocks=[]).write()

        assert getattr(block, "collapsed", None) is None

    def test_a_document_block_writes_its_identifier(self):
        block = types.InputRichBlockDocument(document_id=7, caption="c").write()

        assert isinstance(block, raw.types.PageBlockDocument)
        assert block.document_id == 7

    def test_a_compact_table_sets_the_flag(self):
        block = types.InputRichBlockTable(title="t", rows=[], compact=True).write()

        assert block.compact is True

    async def test_a_collapsed_blockquote_parses_as_expandable(self):
        block = await types.RichBlock._parse(
            Mock(),
            raw.types.PageBlockBlockquote(
                text=raw.types.TextPlain(text="quote"),
                caption=raw.types.TextPlain(text="who"),
                collapsed=True,
            ),
        )

        assert isinstance(block, types.RichBlockExpandableBlockQuotation)
        assert block.text == "quote"

        plain = await types.RichBlock._parse(
            Mock(),
            raw.types.PageBlockBlockquote(
                text=raw.types.TextPlain(text="quote"),
                caption=raw.types.TextPlain(text="who"),
            ),
        )

        assert isinstance(plain, types.RichBlockBlockQuotation)

    async def test_a_button_row_parses_with_its_alignment(self):
        block = await types.RichBlock._parse(
            Mock(),
            raw.types.PageBlockButtonRow(
                buttons=[
                    raw.types.PageButton(
                        text=raw.types.TextPlain(text="a"),
                        type=raw.types.InlineButtonTypeUrl(url="u"),
                    )
                ],
                align_right=True,
            ),
        )

        assert isinstance(block, types.RichBlockButtons)
        assert block.align == enums.BlockAlignment.RIGHT
        assert block.buttons[0].url == "u"

    async def test_a_table_parses_its_compact_flag(self):
        block = await types.RichBlock._parse(
            Mock(),
            raw.types.PageBlockTable(
                title=raw.types.TextPlain(text=""), rows=[], compact=True
            ),
        )

        assert block.is_compact is True

    async def test_a_text_button_parses_as_rich_text(self):
        parsed = await types.RichText._parse(
            Mock(),
            raw.types.TextButton(
                text=raw.types.TextPlain(text="press"),
                type=raw.types.InlineButtonTypeCallback(data=b"d"),
            ),
        )

        assert isinstance(parsed, types.RichTextButton)
        assert parsed.button.callback_data == "d"


class TestWelcomeMessages:
    """chatAdminRights.manage_welcome_messages, and the three welcome RPCs."""

    def test_the_admin_right_survives_a_round_trip(self):
        from pyrogram.types.bots_and_keyboards.keyboard_button import _admin_rights

        rights = types.ChatAdministratorRights(can_send_welcome_messages=True)
        raw_rights = _admin_rights(rights)

        assert raw_rights.manage_welcome_messages is True
        assert (
            types.ChatAdministratorRights._parse(raw_rights).can_send_welcome_messages
            is True
        )

    @pytest.mark.parametrize(
        "path",
        [
            "pyrogram/methods/chats/promote_chat_member.py",
            "pyrogram/methods/bots/set_bot_default_privileges.py",
        ],
    )
    def test_every_admin_rights_writer_sends_the_flag(self, path):
        """A writer that forgets it silently demotes the right on every edit."""

        source = (ROOT / path).read_text(encoding="utf-8")

        assert "manage_welcome_messages=privileges.can_send_welcome_messages" in source

    @pytest.mark.parametrize(
        "method,function",
        [
            ("get_welcome_messages", "GetWelcomeMessages"),
            ("delete_welcome_message", "DeleteWelcomeMessage"),
            ("delete_all_welcome_messages", "DeleteAllWelcomeMessages"),
        ],
    )
    def test_each_method_calls_its_own_rpc(self, method, function):
        import pyrogram

        source = inspect.getsource(getattr(pyrogram.Client, method))

        assert f"raw.functions.ephemeral.{function}(" in source

    def test_send_ephemeral_message_threads_every_new_flag(self):
        """The flags are set on both branches, and the rich one is easy to miss."""

        import pyrogram

        source = inspect.getsource(pyrogram.Client.send_ephemeral_message)
        tree = ast.parse(inspect.cleandoc(source))
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "SendMessage"
        ]

        assert len(calls) == 2, "the plain and rich branches each build one"

        for call in calls:
            names = {kw.arg for kw in call.keywords}

            assert {"welcome", "anchor", "invert_media", "noforwards"} <= names


class TestMessageGenerationStopped:
    def test_the_dispatcher_routes_every_typing_update(self):
        for update in (
            raw.types.UpdateUserTyping,
            raw.types.UpdateChatUserTyping,
            raw.types.UpdateChannelUserTyping,
        ):
            assert update in Dispatcher.TYPING_UPDATES

    def test_the_draft_sends_the_stop_flags(self):
        import pyrogram

        source = inspect.getsource(pyrogram.Client.send_rich_message_draft)

        assert "can_stop=can_stop" in source
        assert "keep_on_stop=keep_on_stop" in source

    def test_it_parses_a_stop_action(self):
        update = raw.types.UpdateUserTyping(
            user_id=5,
            action=raw.types.SendMessageStopDraftAction(random_id=99),
            top_msg_id=3,
        )
        parsed = types.MessageGenerationStopped._parse(
            Mock(), update, {5: _raw_user(5)}, {}
        )

        assert parsed.draft_id == 99
        assert parsed.chat.id == 5
        assert parsed.message_thread_id == 3

    def test_any_other_typing_action_is_not_one(self):
        """Every SendMessageAction arrives on these updates, and only one has a handler."""

        update = raw.types.UpdateUserTyping(
            user_id=5, action=raw.types.SendMessageTypingAction()
        )

        assert types.MessageGenerationStopped._parse(Mock(), update, {}, {}) is None

    async def test_an_unrelated_action_matches_no_handler(self):
        dispatcher = Dispatcher(Mock(listeners=None))
        parser = dispatcher.update_parsers[raw.types.UpdateUserTyping]

        parsed, handler_type = await parser(
            raw.types.UpdateUserTyping(
                user_id=5, action=raw.types.SendMessageTypingAction()
            ),
            {},
            {},
        )

        assert parsed is None
        assert handler_type is type(None), (
            "a handler type that matches would call check() with None"
        )

        parsed, handler_type = await parser(
            raw.types.UpdateUserTyping(
                user_id=5, action=raw.types.SendMessageStopDraftAction(random_id=1)
            ),
            {5: _raw_user(5)},
            {},
        )

        assert handler_type is MessageGenerationStoppedHandler


class TestGiftsAndCommunities:
    async def test_a_unique_gift_keeps_its_text_and_hidden_name(self):
        action = raw.types.MessageActionStarGiftUnique(
            gift=raw.types.StarGiftUnique(
                id=1,
                gift_id=1,
                title="t",
                slug="s",
                num=1,
                attributes=[],
                availability_issued=1,
                availability_total=1,
                owner_id=raw.types.PeerUser(user_id=2),
            ),
            name_hidden=True,
            message=raw.types.TextWithEntities(text="for you", entities=[]),
        )

        parsed = await types.Gift._parse_action(Mock(), action)

        assert parsed.is_name_hidden is True
        assert parsed.text.text == "for you"

    def test_the_resale_invoice_carries_a_message(self):
        import pyrogram

        source = inspect.getsource(pyrogram.Client.send_resold_gift)

        assert "show_name=show_name" in source
        assert "message=raw.types.TextWithEntities(" in source

    def test_a_community_join_is_its_own_service_type(self):
        action = raw.types.MessageActionChatJoinedViaCommunity(community_id=42)
        parsed = types.CommunityChatJoined._parse(Mock(), action, {})

        assert parsed.community_id == 42
        assert enums.MessageServiceType.COMMUNITY_CHAT_JOINED


class TestParsedTextIsRefusedOnInput:
    """A parsed RichText has no write(), and it used to be found by serialising one.

    The high-level types describe a message that arrived. Handing one to an input
    block failed with AttributeError from inside the request, several frames away
    from the call that was actually wrong.
    """

    @pytest.mark.parametrize(
        "block",
        [
            lambda text: types.InputRichBlockParagraph(text=text),
            lambda text: types.InputRichBlockPullQuotation(text=text),
            lambda text: types.InputRichBlockExpandableBlockQuotation(text=text),
        ],
    )
    def test_it_raises_where_it_is_written(self, block):
        with pytest.raises(TypeError, match="raw.types.Text"):
            block(types.RichTextBold(text="x")).write()

    def test_a_rich_button_refuses_one_too(self):
        with pytest.raises(TypeError, match="raw.types.Text"):
            types.RichMessageButton(text=types.RichTextBold(text="x"), url="u").write()

    def test_plain_text_and_raw_text_still_pass(self):
        assert types.InputRichBlockParagraph(text="hi").write().text
        assert types.InputRichBlockParagraph(
            text=raw.types.TextBold(text=raw.types.TextPlain(text="hi"))
        ).write().text

    async def test_a_plain_text_button_round_trips(self):
        """TextPlain parses back to str, which is the one shape that survives."""

        page = raw.types.PageButton(
            text=raw.types.TextPlain(text="Go"),
            type=raw.types.InlineButtonTypeUrl(url="u"),
        )
        parsed = await types.RichMessageButton._parse(Mock(), page)

        assert parsed.write().write()


class TestCommunityLookupIsGuarded:
    """chats is keyed by id across every peer kind, so a community id can miss."""

    def test_a_non_community_resolves_to_nothing(self):
        channel = raw.types.Channel(
            id=42, title="T", photo=raw.types.ChatPhotoEmpty(), date=0
        )
        action = raw.types.MessageActionChatJoinedViaCommunity(community_id=42)

        parsed = types.CommunityChatJoined._parse(Mock(), action, {42: channel})

        assert parsed.community_id == 42
        assert parsed.community is None

    def test_a_community_still_resolves(self):
        community = raw.types.Community(
            id=42, title="T", date=0, photo=raw.types.ChatPhotoEmpty()
        )
        action = raw.types.MessageActionChatJoinedViaCommunity(community_id=42)

        parsed = types.CommunityChatJoined._parse(Mock(), action, {42: community})

        assert parsed.community.title == "T"


class TestForceReply:
    async def test_an_inline_markup_carries_it(self):
        markup = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="x", url="u")]],
            force_reply=True,
        )
        written = await markup.write(AsyncMock())

        assert written.force_reply is True
        assert types.InlineKeyboardMarkup.read(written).force_reply is True

    async def test_a_reply_markup_carries_it(self):
        written = await types.ReplyKeyboardMarkup(
            keyboard=[["a"]], force_reply=True
        ).write(AsyncMock())

        assert written.force_reply is True
        assert types.ReplyKeyboardMarkup.read(written).force_reply is True

    async def test_it_is_absent_rather_than_false_when_unset(self):
        written = await types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="x", url="u")]]
        ).write(AsyncMock())

        assert written.force_reply is None


class TestDisabledButton:
    async def test_it_is_accepted_and_written(self):
        written = await types.InlineKeyboardButton(
            text="x", disabled=types.DisabledButton()
        ).write(AsyncMock())

        assert isinstance(written.type, raw.types.InlineButtonTypeDisabled)

    async def test_it_reads_back_as_the_type(self):
        button = types.InlineKeyboardButton.read(
            raw.types.KeyboardInlineButton(
                text="x", type=raw.types.InlineButtonTypeDisabled()
            )
        )

        assert isinstance(button.disabled, types.DisabledButton)
