from unittest.mock import AsyncMock, MagicMock
import pytest
from pyrogram import Client, enums, raw, utils


def test_report_reason_enum():
    assert enums.ReportReason.SPAM.value == "spam"
    assert enums.ReportReason.VIOLENCE.value == "violence"
    assert enums.ReportReason.PORNOGRAPHY.value == "pornography"
    assert enums.ReportReason.CHILD_ABUSE.value == "child_abuse"
    assert enums.ReportReason.COPYRIGHT.value == "copyright"
    assert enums.ReportReason.GEO_IRRELEVANT.value == "geo_irrelevant"
    assert enums.ReportReason.FAKE.value == "fake"
    assert enums.ReportReason.ILLEGAL_DRUGS.value == "illegal_drugs"
    assert enums.ReportReason.PERSONAL_DETAILS.value == "personal_details"
    assert enums.ReportReason.OTHER.value == "other"


def test_parse_report_reason():
    # From Enum
    assert isinstance(
        utils.parse_report_reason(enums.ReportReason.SPAM), raw.types.InputReportReasonSpam
    )
    assert isinstance(
        utils.parse_report_reason(enums.ReportReason.VIOLENCE), raw.types.InputReportReasonViolence
    )
    assert isinstance(
        utils.parse_report_reason(enums.ReportReason.PORNOGRAPHY),
        raw.types.InputReportReasonPornography,
    )
    assert isinstance(
        utils.parse_report_reason(enums.ReportReason.CHILD_ABUSE),
        raw.types.InputReportReasonChildAbuse,
    )
    assert isinstance(
        utils.parse_report_reason(enums.ReportReason.COPYRIGHT),
        raw.types.InputReportReasonCopyright,
    )
    assert isinstance(
        utils.parse_report_reason(enums.ReportReason.GEO_IRRELEVANT),
        raw.types.InputReportReasonGeoIrrelevant,
    )
    assert isinstance(
        utils.parse_report_reason(enums.ReportReason.FAKE), raw.types.InputReportReasonFake
    )
    assert isinstance(
        utils.parse_report_reason(enums.ReportReason.ILLEGAL_DRUGS),
        raw.types.InputReportReasonIllegalDrugs,
    )
    assert isinstance(
        utils.parse_report_reason(enums.ReportReason.PERSONAL_DETAILS),
        raw.types.InputReportReasonPersonalDetails,
    )
    assert isinstance(
        utils.parse_report_reason(enums.ReportReason.OTHER), raw.types.InputReportReasonOther
    )

    # From string name
    assert isinstance(utils.parse_report_reason("spam"), raw.types.InputReportReasonSpam)
    assert isinstance(utils.parse_report_reason("SPAM"), raw.types.InputReportReasonSpam)
    assert isinstance(
        utils.parse_report_reason("child_abuse"), raw.types.InputReportReasonChildAbuse
    )

    # From raw object
    raw_obj = raw.types.InputReportReasonSpam()
    assert utils.parse_report_reason(raw_obj) is raw_obj

    # Invalid
    with pytest.raises(ValueError):
        utils.parse_report_reason("invalid_reason")


@pytest.mark.asyncio
async def test_report_chat():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerChannel(channel_id=123, access_hash=456)
    )
    client.invoke = AsyncMock(return_value=True)

    result = await client.report_chat(123, enums.ReportReason.SPAM, "Test spam")
    assert result is True

    client.invoke.assert_called_once()
    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.account.ReportPeer)
    assert isinstance(call_arg.reason, raw.types.InputReportReasonSpam)
    assert call_arg.message == "Test spam"


@pytest.mark.asyncio
async def test_report_user():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerUser(user_id=789, access_hash=101)
    )
    client.invoke = AsyncMock(return_value=True)

    result = await client.report_user(789, enums.ReportReason.FAKE, "Fake account")
    assert result is True

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.account.ReportPeer)
    assert isinstance(call_arg.reason, raw.types.InputReportReasonFake)
    assert call_arg.message == "Fake account"


@pytest.mark.asyncio
async def test_report_spam():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerUser(user_id=789, access_hash=101)
    )
    client.invoke = AsyncMock(return_value=True)

    result = await client.report_spam(789)
    assert result is True

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.messages.ReportSpam)


@pytest.mark.asyncio
async def test_report_profile_photo():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerUser(user_id=789, access_hash=101)
    )
    client.invoke = AsyncMock(return_value=True)

    photo = raw.types.InputPhoto(id=111, access_hash=222, file_reference=b"ref")
    result = await client.report_profile_photo(789, photo, enums.ReportReason.PORNOGRAPHY)
    assert result is True

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.account.ReportProfilePhoto)
    assert call_arg.photo_id.id == 111
    assert isinstance(call_arg.reason, raw.types.InputReportReasonPornography)


@pytest.mark.asyncio
async def test_report_messages_direct_option():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerChannel(channel_id=123, access_hash=456)
    )
    client.invoke = AsyncMock(return_value=True)

    result = await client.report_messages(123, [1, 2], option=b"test_opt", message="Spam text")
    assert result is True

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.messages.Report)
    assert call_arg.id == [1, 2]
    assert call_arg.option == b"test_opt"
    assert call_arg.message == "Spam text"


@pytest.mark.asyncio
async def test_report_messages_with_choose_option():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerChannel(channel_id=123, access_hash=456)
    )

    # First invocation returns options, second reports
    choose_res = raw.types.ReportResultChooseOption(
        title="Report",
        options=[
            raw.types.MessageReportOption(text="Spam", option=b"opt_spam"),
            raw.types.MessageReportOption(text="Violence", option=b"opt_violence"),
        ],
    )
    client.invoke = AsyncMock(side_effect=[choose_res, raw.types.ReportResultReported()])

    result = await client.report_messages(
        123, 1, reason=enums.ReportReason.SPAM, message="Spam details"
    )
    assert result is True
    assert client.invoke.call_count == 2

    second_call = client.invoke.call_args_list[1][0][0]
    assert isinstance(second_call, raw.functions.messages.Report)
    assert second_call.option == b"opt_spam"
    assert second_call.message == "Spam details"


@pytest.mark.asyncio
async def test_report_messages_participant():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(
        side_effect=[
            raw.types.InputPeerChannel(channel_id=123, access_hash=456),
            raw.types.InputPeerUser(user_id=789, access_hash=101),
        ]
    )
    client.invoke = AsyncMock(return_value=True)

    result = await client.report_messages(123, [1, 2], participant=789)
    assert result is True

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.channels.ReportSpam)
    assert call_arg.id == [1, 2]


@pytest.mark.asyncio
async def test_report_reaction():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(
        side_effect=[
            raw.types.InputPeerChannel(channel_id=123, access_hash=456),
            raw.types.InputPeerUser(user_id=789, access_hash=101),
        ]
    )
    client.invoke = AsyncMock(return_value=True)

    result = await client.report_reaction(123, 42, 789)
    assert result is True

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.messages.ReportReaction)
    assert call_arg.id == 42


@pytest.mark.asyncio
async def test_report_anti_spam_false_positive():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerChannel(channel_id=123, access_hash=456)
    )
    client.invoke = AsyncMock(return_value=True)

    result = await client.report_anti_spam_false_positive(123, 42)
    assert result is True

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.channels.ReportAntiSpamFalsePositive)
    assert call_arg.msg_id == 42


@pytest.mark.asyncio
async def test_report_story():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerUser(user_id=789, access_hash=101)
    )
    client.invoke = AsyncMock(return_value=raw.types.ReportResultReported())

    result = await client.report_story(789, 5, option=b"opt")
    assert result is True

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.stories.Report)
    assert call_arg.id == [5]


@pytest.mark.asyncio
async def test_bound_methods():
    client = Client("test", in_memory=True)
    client.report_chat = AsyncMock(return_value=True)
    client.report_spam = AsyncMock(return_value=True)
    client.report_user = AsyncMock(return_value=True)
    client.report_messages = AsyncMock(return_value=True)
    client.report_story = AsyncMock(return_value=True)

    # Chat
    chat = MagicMock()
    chat._client = client
    chat.id = 123
    from pyrogram.types.user_and_chats.chat import Chat

    assert await Chat.report(chat, enums.ReportReason.SPAM) is True
    client.report_chat.assert_called_once_with(123, reason=enums.ReportReason.SPAM, message="")

    assert await Chat.report_spam(chat) is True
    client.report_spam.assert_called_once_with(123)

    # User
    user = MagicMock()
    user._client = client
    user.id = 789
    from pyrogram.types.user_and_chats.user import User

    assert await User.report(user, enums.ReportReason.FAKE) is True
    client.report_user.assert_called_once_with(789, reason=enums.ReportReason.FAKE, message="")

    # Message
    msg = MagicMock()
    msg._client = client
    msg.id = 456
    msg.chat.id = 123
    from pyrogram.types.messages_and_media.message import Message

    assert await Message.report(msg, enums.ReportReason.SPAM) is True
    client.report_messages.assert_called_once_with(
        chat_id=123, message_ids=456, reason=enums.ReportReason.SPAM, message="", option=b""
    )

    # Story
    story = MagicMock()
    story._client = client
    story.id = 999
    story.chat.id = 123
    from pyrogram.types.messages_and_media.story import Story

    assert await Story.report(story, enums.ReportReason.SPAM) is True
    client.report_story.assert_called_once_with(
        chat_id=123, story_ids=999, reason=enums.ReportReason.SPAM, message="", option=b""
    )
