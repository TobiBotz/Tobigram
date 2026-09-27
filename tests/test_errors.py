import pytest

from pyrogram.errors import (
    BadRequest,
    Flood,
    Forbidden,
    RPCError,
    UnknownError,
)
from pyrogram.errors.exceptions.bad_request_400 import AboutTooLong, ChatAdminRequired400 as ChatAdminRequired
from pyrogram.errors.exceptions.flood_420 import FloodWait, SlowmodeWait
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden, UserIsBlocked


class TestRPCErrorBase:
    def test_is_exception(self):
        assert issubclass(RPCError, Exception)

    def test_default_attributes(self):
        assert RPCError.ID is None
        assert RPCError.CODE is None
        assert RPCError.NAME is None

    def test_message_format(self):
        class CustomError(RPCError):
            CODE = 400
            ID = "CUSTOM_ERROR"
            MESSAGE = "Something went wrong: {value}"

        err = CustomError(value=42)
        msg = str(err)
        assert "400" in msg
        assert "CUSTOM_ERROR" in msg
        assert "Something went wrong: 42" in msg

    def test_value_conversion_int(self):
        class CustomError(RPCError):
            CODE = 400
            ID = "CUSTOM"
            MESSAGE = "{value}"

        err = CustomError(value="42")
        assert err.value == 42

    def test_value_conversion_string(self):
        class CustomError(RPCError):
            CODE = 400
            ID = "CUSTOM"
            MESSAGE = "{value}"

        err = CustomError(value="not_a_number")
        assert isinstance(err.value, str)

    def test_unknown_error_defaults(self):
        err = UnknownError()
        assert err.CODE == 520
        assert "Unknown error" in err.NAME
        assert "520" in str(err)

    def test_caused_by_message(self):
        class CustomError(RPCError):
            CODE = 400
            ID = "CUSTOM"
            MESSAGE = "{value}"

        err = CustomError(value="test", rpc_name="users.getFullUser")
        msg = str(err)
        assert '(caused by "users.getFullUser")' in msg

    def test_signed_code(self):
        class CustomError(RPCError):
            CODE = 400
            ID = "CUSTOM"
            MESSAGE = "{value}"

        err = CustomError(value="test", is_signed=True)
        msg = str(err)
        assert "-400" in msg


class TestBadRequest:
    def test_code(self):
        assert BadRequest.CODE == 400
        assert "Bad Request" in BadRequest.NAME

    def test_hierarchy(self):
        assert issubclass(BadRequest, RPCError)

    def test_about_too_long(self):
        assert AboutTooLong.CODE == 400
        assert AboutTooLong.ID == "ABOUT_TOO_LONG"
        assert issubclass(AboutTooLong, BadRequest)

    def test_chat_admin_required(self):
        assert ChatAdminRequired.CODE == 400
        assert ChatAdminRequired.ID == "CHAT_ADMIN_REQUIRED"
        assert issubclass(ChatAdminRequired, BadRequest)

    def test_about_too_long_message(self):
        err = AboutTooLong(value="something")
        assert "400" in str(err)
        assert "ABOUT_TOO_LONG" in str(err)
        assert "About string too long." in str(err)

    def test_chat_admin_required_message(self):
        err = ChatAdminRequired()
        assert "400" in str(err)
        assert "CHAT_ADMIN_REQUIRED" in str(err)

    def test_about_too_long_raises(self):
        with pytest.raises(AboutTooLong):
            raise AboutTooLong(value="test")


class TestForbidden:
    def test_code(self):
        assert Forbidden.CODE == 403
        assert "Forbidden" in Forbidden.NAME

    def test_hierarchy(self):
        assert issubclass(Forbidden, RPCError)

    def test_chat_write_forbidden(self):
        assert ChatWriteForbidden.CODE == 403
        assert ChatWriteForbidden.ID == "CHAT_WRITE_FORBIDDEN"
        assert issubclass(ChatWriteForbidden, Forbidden)

    def test_user_is_blocked(self):
        assert UserIsBlocked.CODE == 403
        assert UserIsBlocked.ID == "USER_IS_BLOCKED"
        assert issubclass(UserIsBlocked, Forbidden)

    def test_chat_write_forbidden_message(self):
        err = ChatWriteForbidden()
        msg = str(err)
        assert "403" in msg
        assert "CHAT_WRITE_FORBIDDEN" in msg
        assert "You can't write in this chat." in msg


class TestFlood:
    def test_code(self):
        assert Flood.CODE == 420
        assert "Flood" in Flood.NAME

    def test_hierarchy(self):
        assert issubclass(Flood, RPCError)

    def test_flood_wait(self):
        assert FloodWait.CODE == 420
        assert FloodWait.ID == "FLOOD_WAIT_X"
        assert issubclass(FloodWait, Flood)

    def test_slowmode_wait(self):
        assert SlowmodeWait.CODE == 420
        assert SlowmodeWait.ID == "SLOWMODE_WAIT_X"
        assert issubclass(SlowmodeWait, Flood)

    def test_flood_wait_message(self):
        err = FloodWait(value=60)
        msg = str(err)
        assert "420" in msg
        assert "FLOOD_WAIT_X" in msg
        assert "60" in msg

    def test_flood_wait_value(self):
        err = FloodWait(value=60)
        assert err.value == 60

    def test_slowmode_wait_value(self):
        err = SlowmodeWait(value=10)
        assert err.value == 10


class TestUnknownError:
    def test_code(self):
        assert UnknownError.CODE == 520

    def test_instantiation(self):
        err = UnknownError()
        assert "520" in str(err)
        assert "Unknown error" in str(err)

    def test_with_rpc_name(self):
        err = UnknownError(rpc_name="messages.sendMessage")
        assert '(caused by "messages.sendMessage")' in str(err)


def _all_known_errors():
    from pyrogram.errors.exceptions.all import exceptions

    return [(code, error_id) for code, table in exceptions.items() for error_id in table if error_id != "_"]


@pytest.mark.parametrize("code,error_id", _all_known_errors())
def test_an_error_keeps_the_code_telegram_sent(code, error_id):
    import pyrogram.errors as errors
    from pyrogram import raw
    from pyrogram.errors.exceptions.all import exceptions

    message = error_id.replace("_X", "_2").replace("_*", "_A")

    with pytest.raises(RPCError) as info:
        RPCError.raise_it(raw.types.RpcError(error_code=code, error_message=message), raw.functions.Ping)

    assert info.value.CODE == code
    assert isinstance(info.value, getattr(errors, exceptions[code]["_"]))
    assert f"[{code} " in str(info.value)


def test_a_phone_number_refused_with_400_is_a_bad_request():
    from pyrogram import raw
    from pyrogram.errors import NotAcceptable, PhoneNumberInvalid

    with pytest.raises(PhoneNumberInvalid) as info:
        RPCError.raise_it(
            raw.types.RpcError(error_code=400, error_message="PHONE_NUMBER_INVALID"), raw.functions.Ping
        )

    assert isinstance(info.value, BadRequest)
    assert info.value.CODE == 400
    assert PhoneNumberInvalid.CODE == 406
    assert issubclass(PhoneNumberInvalid, NotAcceptable)


def test_an_error_known_under_two_codes_keeps_its_class_name():
    from pyrogram.errors.exceptions import forbidden_403

    assert UserIsBlocked is forbidden_403.UserIsBlocked
    assert UserIsBlocked.CODE == 403
