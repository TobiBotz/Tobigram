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
