import pytest
from unittest.mock import AsyncMock, MagicMock
from pyrogram import enums, raw, types
from pyrogram.methods.messages.copy_message import CopyMessage
from pyrogram.methods.messages.copy_messages import CopyMessages


@pytest.mark.asyncio
async def test_reply_keyboard_markup_read_write():
    # 1. Test parsing raw ReplyKeyboardMarkup with various buttons
    raw_kb = raw.types.ReplyKeyboardMarkup(
        rows=[
            raw.types.KeyboardButtonRow(
                buttons=[
                    raw.types.KeyboardButton(
                        text="Regular Button 1",
                        type=raw.types.ButtonTypeDefault(),
                    ),
                    raw.types.KeyboardButton(
                        text="Contact Button",
                        type=raw.types.ButtonTypeRequestPhone(),
                    ),
                    raw.types.KeyboardButton(
                        text="Location Button",
                        type=raw.types.ButtonTypeRequestGeoLocation(),
                    ),
                ]
            ),
            raw.types.KeyboardButtonRow(
                buttons=[
                    raw.types.KeyboardButton(
                        text="Poll Button",
                        type=raw.types.ButtonTypeRequestPoll(quiz=True),
                    ),
                    raw.types.KeyboardButton(
                        text="Web App Button",
                        type=raw.types.ButtonTypeSimpleWebView(url="https://app.example.com"),
                    ),
                ]
            ),
        ],
        resize=True,
        persistent=True,
    )

    parsed_kb = types.ReplyKeyboardMarkup.read(raw_kb)
    assert parsed_kb is not None
    assert len(parsed_kb.keyboard) == 2
    assert parsed_kb.keyboard[0][0] == "Regular Button 1"
    assert isinstance(parsed_kb.keyboard[0][1], types.KeyboardButton)
    assert parsed_kb.keyboard[0][1].request_contact is True
    assert isinstance(parsed_kb.keyboard[0][2], types.KeyboardButton)
    assert parsed_kb.keyboard[0][2].request_location is True
    assert isinstance(parsed_kb.keyboard[1][0], types.KeyboardButton)
    assert parsed_kb.keyboard[1][0].request_poll.is_quiz is True
    assert isinstance(parsed_kb.keyboard[1][1], types.KeyboardButton)
    assert parsed_kb.keyboard[1][1].web_app.url == "https://app.example.com"

    # 2. Test serializing parsed ReplyKeyboardMarkup
    mock_client = MagicMock()
    serialized_kb = await parsed_kb.write(mock_client)
    assert isinstance(serialized_kb, raw.types.ReplyKeyboardMarkup)
    assert len(serialized_kb.rows) == 2
    assert len(serialized_kb.rows[0].buttons) == 3
    assert serialized_kb.rows[0].buttons[0].text == "Regular Button 1"
    assert serialized_kb.rows[0].buttons[1].text == "Contact Button"


@pytest.mark.asyncio
async def test_message_copy_preserves_regular_buttons():
    mock_client = MagicMock()
    mock_client.send_message = AsyncMock()
    mock_client.send_contact = AsyncMock()
    mock_client.send_location = AsyncMock()
    mock_client.send_venue = AsyncMock()
    mock_client.send_poll = AsyncMock()
    mock_client.send_game = AsyncMock()
    mock_client.send_dice = AsyncMock()
    mock_client.send_cached_media = AsyncMock()

    regular_kb = types.ReplyKeyboardMarkup(
        keyboard=[
            ["Button A", "Button B"],
            [types.KeyboardButton("Send Contact", request_contact=True)],
        ],
        resize_keyboard=True,
    )

    # 1. Test Text Message copy: ReplyKeyboardMarkup is NOT copied by default
    text_msg = types.Message(
        id=101,
        chat=types.Chat(id=1001, type=enums.ChatType.PRIVATE),
        text=types.Str("Hello World"),
        reply_markup=regular_kb,
        client=mock_client,
    )

    await text_msg.copy(chat_id=2002)
    mock_client.send_message.assert_called_once()
    assert mock_client.send_message.call_args.kwargs["reply_markup"] is None

    # Test that InlineKeyboardMarkup IS copied by default
    inline_kb = types.InlineKeyboardMarkup([[types.InlineKeyboardButton("URL", url="https://t.me")]])
    text_msg_inline = types.Message(
        id=1011,
        chat=types.Chat(id=1001, type=enums.ChatType.PRIVATE),
        text=types.Str("Hello Inline"),
        reply_markup=inline_kb,
        client=mock_client,
    )
    await text_msg_inline.copy(chat_id=2002)
    assert mock_client.send_message.call_args.kwargs["reply_markup"] is inline_kb

    # 2. Test Contact Message copy: ReplyKeyboardMarkup not copied by default
    contact_msg = types.Message(
        id=102,
        chat=types.Chat(id=1001, type=enums.ChatType.PRIVATE),
        contact=types.Contact(phone_number="+1234567890", first_name="John"),
        media=enums.MessageMediaType.CONTACT,
        reply_markup=regular_kb,
        client=mock_client,
    )
    await contact_msg.copy(chat_id=2002)
    mock_client.send_contact.assert_called_once()
    assert mock_client.send_contact.call_args.kwargs["reply_markup"] is None

    # 3. Test Location Message copy: ReplyKeyboardMarkup not copied by default
    location_msg = types.Message(
        id=103,
        chat=types.Chat(id=1001, type=enums.ChatType.PRIVATE),
        location=types.Location(latitude=12.34, longitude=56.78),
        media=enums.MessageMediaType.LOCATION,
        reply_markup=regular_kb,
        client=mock_client,
    )
    await location_msg.copy(chat_id=2002)
    mock_client.send_location.assert_called_once()
    assert mock_client.send_location.call_args.kwargs["reply_markup"] is None

    # 4. Test Poll Message copy: ReplyKeyboardMarkup not copied by default
    poll_msg = types.Message(
        id=104,
        chat=types.Chat(id=1001, type=enums.ChatType.PRIVATE),
        poll=types.Poll(
            id="1",
            question=types.FormattedText(text="Favorite color?"),
            options=[types.PollOption(persistent_id="1", text=types.FormattedText(text="Blue"))],
            total_voter_count=0,
            is_closed=False,
            is_anonymous=True,
            type=enums.PollType.REGULAR,
            allows_multiple_answers=False,
        ),
        media=enums.MessageMediaType.POLL,
        reply_markup=regular_kb,
        client=mock_client,
    )
    await poll_msg.copy(chat_id=2002)
    mock_client.send_poll.assert_called_once()
    assert mock_client.send_poll.call_args.kwargs["reply_markup"] is None

    # 5. Test Dice Message copy: ReplyKeyboardMarkup not copied by default
    dice_msg = types.Message(
        id=105,
        chat=types.Chat(id=1001, type=enums.ChatType.PRIVATE),
        dice=types.Dice(value=6, emoji="🎲"),
        media=enums.MessageMediaType.DICE,
        reply_markup=regular_kb,
        client=mock_client,
    )
    await dice_msg.copy(chat_id=2002)
    mock_client.send_dice.assert_called_once()
    assert mock_client.send_dice.call_args.kwargs["reply_markup"] is None

    # Explicit custom reply_markup is respected even if it's a ReplyKeyboardMarkup
    await dice_msg.copy(chat_id=2002, reply_markup=regular_kb)
    assert mock_client.send_dice.call_args.kwargs["reply_markup"] is regular_kb


@pytest.mark.asyncio
async def test_copy_message_client_method():
    mock_client = MagicMock()
    mock_client.send_message = AsyncMock()

    regular_kb = types.ReplyKeyboardMarkup([["Option 1", "Option 2"]])
    msg = types.Message(
        id=555,
        chat=types.Chat(id=111, type=enums.ChatType.PRIVATE),
        text=types.Str("Testing copy_message"),
        reply_markup=regular_kb,
        client=mock_client,
    )

    mock_client.get_messages = AsyncMock(return_value=msg)

    # Without explicit reply_markup: ReplyKeyboardMarkup is NOT copied (becomes None)
    await CopyMessage.copy_message(mock_client, chat_id=222, from_chat_id=111, message_id=555)
    assert mock_client.send_message.call_args.kwargs["reply_markup"] is None

    # With custom reply_markup passed explicitly:
    custom_kb = types.ReplyKeyboardMarkup([["Custom 1"]])
    await CopyMessage.copy_message(
        mock_client, chat_id=222, from_chat_id=111, message_id=555, reply_markup=custom_kb
    )
    assert mock_client.send_message.call_args.kwargs["reply_markup"] is custom_kb

    # copy_messages bulk: ReplyKeyboardMarkup is NOT copied by default
    await CopyMessages.copy_messages(mock_client, chat_id=222, from_chat_id=111, message_ids=[555])
    assert mock_client.send_message.call_args.kwargs["reply_markup"] is None
