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

from .accept_login_token import AcceptLoginToken
from .accept_terms_of_service import AcceptTermsOfService
from .bind_temp_auth_key import BindTempAuthKey
from .cancel_code import CancelCode
from .change_phone_number import ChangePhoneNumber
from .check_paid_auth import CheckPaidAuth
from .check_password import CheckPassword
from .check_recovery_password import CheckRecoveryPassword
from .connect import Connect
from .disconnect import Disconnect
from .drop_temp_auth_keys import DropTempAuthKeys
from .export_authorization import ExportAuthorization
from .export_login_token import ExportLoginToken
from .finish_firebase_pnv_login import FinishFirebasePnvLogin
from .finish_passkey_login import FinishPasskeyLogin
from .firebase_pnv_sign_up import FirebasePnvSignUp
from .get_active_sessions import GetActiveSessions
from .get_password_hint import GetPasswordHint
from .import_authorization import ImportAuthorization
from .import_login_token import ImportLoginToken
from .import_web_token_authorization import ImportWebTokenAuthorization
from .init_firebase_pnv_login import InitFirebasePnvLogin
from .init_passkey_login import InitPasskeyLogin
from .initialize import Initialize
from .log_out import LogOut
from .recover_password import RecoverPassword
from .report_missing_code import ReportMissingCode
from .request_firebase_sms import RequestFirebaseSms
from .resend_code import ResendCode
from .resend_phone_number_code import ResendPhoneNumberCode
from .reset_login_email import ResetLoginEmail
from .reset_session import ResetSession
from .reset_sessions import ResetSessions
from .send_code import SendCode
from .send_phone_number_code import SendPhoneNumberCode
from .send_recovery_code import SendRecoveryCode
from .sign_in import SignIn
from .sign_in_bot import SignInBot
from .sign_up import SignUp
from .terminate import Terminate


class Auth(
    AcceptLoginToken,
    AcceptTermsOfService,
    BindTempAuthKey,
    CancelCode,
    ChangePhoneNumber,
    CheckPaidAuth,
    CheckPassword,
    CheckRecoveryPassword,
    Connect,
    Disconnect,
    DropTempAuthKeys,
    ExportAuthorization,
    ExportLoginToken,
    FinishFirebasePnvLogin,
    FinishPasskeyLogin,
    FirebasePnvSignUp,
    GetActiveSessions,
    GetPasswordHint,
    ImportAuthorization,
    ImportLoginToken,
    ImportWebTokenAuthorization,
    InitFirebasePnvLogin,
    InitPasskeyLogin,
    Initialize,
    LogOut,
    RecoverPassword,
    ReportMissingCode,
    RequestFirebaseSms,
    ResendCode,
    ResendPhoneNumberCode,
    ResetLoginEmail,
    ResetSession,
    ResetSessions,
    SendCode,
    SendPhoneNumberCode,
    SendRecoveryCode,
    SignIn,
    SignInBot,
    SignUp,
    Terminate,
):
    pass
