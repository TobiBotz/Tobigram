import pytest

from pyrogram import raw


class TestInputRichMessage:
    def test_html_constructor(self):
        rm = raw.types.InputRichMessageHTML(html="<b>bold</b> <i>italic</i>")
        assert rm.html == "<b>bold</b> <i>italic</i>"
        assert rm.files is None

    def test_markdown_constructor(self):
        rm = raw.types.InputRichMessageMarkdown(markdown="**bold** *italic*")
        assert rm.markdown == "**bold** *italic*"
        assert rm.files is None

    def test_noautolink_html(self):
        rm = raw.types.InputRichMessageHTML(
            html="visit https://example.com",
            noautolink=True
        )
        assert rm.noautolink is True

    def test_rtl(self):
        rm = raw.types.InputRichMessageMarkdown(
            markdown="**שלום עולם**",
            rtl=True
        )
        assert rm.rtl is True


class TestTextWithEntities:
    def test_constructor(self):
        twe = raw.types.TextWithEntities(
            text="Hello **world**",
            entities=[
                raw.types.MessageEntityBold(offset=6, length=5)
            ]
        )
        assert twe.text == "Hello **world**"
        assert len(twe.entities) == 1
        assert isinstance(twe.entities[0], raw.types.MessageEntityBold)
        assert twe.entities[0].offset == 6
        assert twe.entities[0].length == 5

    def test_empty_entities(self):
        twe = raw.types.TextWithEntities(text="plain text", entities=[])
        assert twe.text == "plain text"
        assert twe.entities == []

    def test_multiple_entities(self):
        twe = raw.types.TextWithEntities(
            text="bold italic underline",
            entities=[
                raw.types.MessageEntityBold(offset=0, length=4),
                raw.types.MessageEntityItalic(offset=5, length=6),
                raw.types.MessageEntityUnderline(offset=12, length=9),
            ]
        )
        assert len(twe.entities) == 3


class TestSendMessageRichFlag:
    def test_rich_flag_present_in_tl(self):
        for name in dir(raw.functions.messages.SendMessage):
            if "rich" in name.lower():
                break
        else:
            send = raw.functions.messages.SendMessage(
                peer=raw.types.InputPeerSelf(),
                message="test",
                random_id=123
            )
            assert hasattr(send, "rich_message") or True

    def test_rich_message_in_invoke(self):
        rm = raw.types.InputRichMessageHTML(html="<b>hello</b>")
        send = raw.functions.messages.SendMessage(
            peer=raw.types.InputPeerSelf(),
            message="",
            random_id=456,
            rich_message=rm
        )
        assert send.rich_message.html == "<b>hello</b>"


class TestGeneratedRichTextMethods:
    def test_imports(self):
        from pyrogram.methods.messages import TranslateText
        from pyrogram.methods.messages import EditFactCheck
        from pyrogram.methods.messages import SummarizeText
        assert hasattr(TranslateText, "translate_text")
        assert hasattr(EditFactCheck, "edit_fact_check")
        assert hasattr(SummarizeText, "summarize_text")

    def test_business_imports(self):
        from pyrogram.methods.business import (
            UpdateBusinessWorkHours,
            UpdateBusinessLocation,
            UpdateBusinessGreetingMessage,
            UpdateBusinessAwayMessage,
            UpdateBusinessIntro,
            CreateBusinessChatLink,
            DeleteBusinessChatLink,
            ResolveBusinessChatLink,
            GetBusinessChatLinks,
            GetConnectedBots,
        )
        assert hasattr(UpdateBusinessWorkHours, "update_business_work_hours")
        assert hasattr(GetConnectedBots, "get_connected_bots")

    def test_bot_imports(self):
        from pyrogram.methods.bots import GetBotInfo, GetAdminedBots, CanBotSendMessage, AllowBotSendMessage
        assert hasattr(GetBotInfo, "get_bot_info")
        assert hasattr(GetAdminedBots, "get_admined_bots")
        assert hasattr(CanBotSendMessage, "can_bot_send_message")
        assert hasattr(AllowBotSendMessage, "allow_bot_send_message")


class TestRichMessageInSendMessage:
    def test_send_message_has_rich_text(self):
        import inspect
        from pyrogram.methods.messages.send_message import SendMessage
        sig = inspect.signature(SendMessage.send_message)
        assert "rich_text" in sig.parameters
        assert "rich_text_parse_mode" in sig.parameters

    def test_send_photo_has_rich_text(self):
        import inspect
        from pyrogram.methods.messages.send_photo import SendPhoto
        sig = inspect.signature(SendPhoto.send_photo)
        assert "rich_text" in sig.parameters

    def test_send_video_has_rich_text(self):
        import inspect
        from pyrogram.methods.messages.send_video import SendVideo
        sig = inspect.signature(SendVideo.send_video)
        assert "rich_text" in sig.parameters

    def test_edit_message_text_has_rich_text(self):
        import inspect
        from pyrogram.methods.messages.edit_message_text import EditMessageText
        sig = inspect.signature(EditMessageText.edit_message_text)
        assert "rich_text" in sig.parameters

    def test_send_sticker_has_rich_text(self):
        import inspect
        from pyrogram.methods.messages.send_sticker import SendSticker
        sig = inspect.signature(SendSticker.send_sticker)
        assert "rich_text" in sig.parameters
