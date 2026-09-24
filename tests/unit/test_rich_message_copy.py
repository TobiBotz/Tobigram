import pytest
from unittest.mock import AsyncMock, MagicMock
from pyrogram import enums, raw, types


@pytest.mark.asyncio
async def test_rich_message_copy():
    # 1. Test RichMessage parsing with _raw
    mock_client = MagicMock()
    mock_client.send_rich_message = AsyncMock()

    raw_button = raw.types.TextButton(
        text=raw.types.TextPlain(text="NAZKI"),
        type=raw.types.InlineButtonTypeUrl(url="https://example.com"),
        style=raw.types.RichButtonStyle(bg_primary=True),
    )
    raw_para = raw.types.PageBlockParagraph(
        text=raw.types.TextConcat(
            texts=[
                raw.types.TextBold(text=raw.types.TextPlain(text="FIXED")),
                raw.types.TextPlain(text=" "),
                raw_button,
            ]
        )
    )
    raw_rich = raw.types.RichMessage(
        blocks=[raw_para],
        photos=[],
        documents=[],
    )

    parsed_rich = await types.RichMessage._parse(mock_client, raw_rich)
    assert hasattr(parsed_rich, "_raw")
    assert parsed_rich._raw is raw_rich

    # 2. Test to_input_rich_message
    input_rich = parsed_rich.to_input_rich_message()
    assert isinstance(input_rich, raw.types.InputRichMessage)
    assert input_rich.blocks == raw_rich.blocks

    # 3. Test Message.copy() with rich_message
    msg = types.Message(
        id=123,
        chat=types.Chat(id=456, type=enums.ChatType.PRIVATE),
        client=mock_client,
    )
    msg.rich_message = parsed_rich

    reply_markup = types.InlineKeyboardMarkup(
        [[types.InlineKeyboardButton("Test", callback_data="test")]]
    )

    await msg.copy(chat_id=789, reply_markup=reply_markup)

    mock_client.send_rich_message.assert_called_once()
    kwargs = mock_client.send_rich_message.call_args.kwargs
    assert kwargs["chat_id"] == 789
    assert kwargs["rich_text"] is parsed_rich
    assert kwargs["reply_markup"] == reply_markup

    # 4. Test Client.send_rich_message with types.RichMessage
    real_client = mock_client
    real_client.invoke = AsyncMock(
        return_value=raw.types.Updates(updates=[], users=[], chats=[], date=0, seq=0)
    )
    real_client.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerUser(user_id=789, access_hash=0)
    )
    real_client.rnd_id = MagicMock(return_value=12345)
    from pyrogram.methods.messages.send_rich_message import SendRichMessage

    sent = await SendRichMessage.send_rich_message(
        real_client, chat_id=789, rich_text=parsed_rich, reply_markup=reply_markup
    )
    real_client.invoke.assert_called_once()
    invoked_rpc = real_client.invoke.call_args[0][0]
    assert isinstance(invoked_rpc, raw.functions.messages.SendMessage)
    assert isinstance(invoked_rpc.rich_message, raw.types.InputRichMessage)
    assert invoked_rpc.rich_message.blocks == raw_rich.blocks

    # 5. Test Client.copy_message with rich message
    from pyrogram.methods.messages.copy_message import CopyMessage

    real_client.get_messages = AsyncMock(return_value=msg)
    await CopyMessage.copy_message(
        real_client, chat_id=789, from_chat_id=456, message_id=123, reply_markup=reply_markup
    )
    assert mock_client.send_rich_message.call_count == 2


@pytest.mark.asyncio
async def test_rich_text_nested_formatting_and_strip():
    mock_client = MagicMock()

    # 1. Mention containing Bold text (reproduction of user's issue)
    raw_mention = raw.types.TextMention(
        text=raw.types.TextBold(text=raw.types.TextPlain(text="@durov"))
    )
    parsed_mention = await types.RichText._parse(mock_client, raw_mention)
    assert isinstance(parsed_mention, types.RichTextMention)
    assert isinstance(parsed_mention.text, types.RichTextBold)
    assert parsed_mention.username == "durov"
    assert parsed_mention.to_plain_text() == "@durov"
    assert str(parsed_mention) == "@durov"

    # 2. Hashtag containing Italic text
    raw_hashtag = raw.types.TextHashtag(
        text=raw.types.TextItalic(text=raw.types.TextPlain(text="#telegram"))
    )
    parsed_hashtag = await types.RichText._parse(mock_client, raw_hashtag)
    assert isinstance(parsed_hashtag, types.RichTextHashtag)
    assert isinstance(parsed_hashtag.text, types.RichTextItalic)
    assert parsed_hashtag.hashtag == "telegram"
    assert parsed_hashtag.to_plain_text() == "#telegram"

    # 3. Cashtag containing Underline text
    raw_cashtag = raw.types.TextCashtag(
        text=raw.types.TextUnderline(text=raw.types.TextPlain(text="$TON"))
    )
    parsed_cashtag = await types.RichText._parse(mock_client, raw_cashtag)
    assert isinstance(parsed_cashtag, types.RichTextCashtag)
    assert isinstance(parsed_cashtag.text, types.RichTextUnderline)
    assert parsed_cashtag.cashtag == "TON"

    # 4. BotCommand containing Code text
    raw_command = raw.types.TextBotCommand(
        text=raw.types.TextFixed(text=raw.types.TextPlain(text="/start"))
    )
    parsed_command = await types.RichText._parse(mock_client, raw_command)
    assert isinstance(parsed_command, types.RichTextBotCommand)
    assert isinstance(parsed_command.text, types.RichTextCode)
    assert parsed_command.bot_command == "start"

    # 5. TextAutoUrl containing Bold text
    raw_auto_url = raw.types.TextAutoUrl(
        text=raw.types.TextBold(text=raw.types.TextPlain(text="https://telegram.org"))
    )
    parsed_url = await types.RichText._parse(mock_client, raw_auto_url)
    assert isinstance(parsed_url, types.RichTextUrl)
    assert isinstance(parsed_url.text, types.RichTextBold)
    assert parsed_url.url == "https://telegram.org"

    # 6. Concat mention: ["@", Bold("coolbot")]
    raw_concat_mention = raw.types.TextMention(
        text=raw.types.TextConcat(
            texts=[
                raw.types.TextPlain(text="@"),
                raw.types.TextBold(text=raw.types.TextPlain(text="coolbot")),
            ]
        )
    )
    parsed_concat = await types.RichText._parse(mock_client, raw_concat_mention)
    assert isinstance(parsed_concat, types.RichTextMention)
    assert parsed_concat.username == "coolbot"
