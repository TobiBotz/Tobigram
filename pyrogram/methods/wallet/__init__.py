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

from .accept_ton_connect_request import AcceptTonConnectRequest
from .start_ton_connect_session import StartTonConnectSession
from .create_user_wallet import CreateUserWallet
from .create_wallet import CreateWallet
from .decline_ton_connect_request import DeclineTonConnectRequest
from .disconnect_ton_connect_session import DisconnectTonConnectSession
from .disable_wallet_backup import DisableWalletBackup
from .enable_wallet_backup import EnableWalletBackup
from .export_wallet_secret_phrase import ExportWalletSecretPhrase
from .fetch_encrypted_secret_phrase_part import FetchEncryptedSecretPhrasePart
from .get_backup_holder_dcs import GetBackupHolderDcs
from .get_existing_wallet_balance import GetExistingWalletBalance
from .get_ton_connect_next_event_id import GetTonConnectNextEventId
from .get_ton_connect_pending import GetTonConnectPending
from .get_ton_connect_sessions import GetTonConnectSessions
from .get_user_wallet_addresses import GetUserWalletAddresses
from .get_proof_challenge import GetProofChallenge
from .get_wallet_gasless_info import GetWalletGaslessInfo
from .get_wallet_nfts import GetWalletNfts
from .get_wallet_state import GetWalletState
from .get_wallet_transactions import GetWalletTransactions
from .get_wallet_transactions_by_ids import GetWalletTransactionsByIds
from .get_wallet_transactions_by_msg_hash import GetWalletTransactionsByMsgHash
from .import_wallet import ImportWallet
from .register_ton_connect_key import RegisterTonConnectKey
from .replace_wallet import ReplaceWallet
from .send_ton_transfer import SendTonTransfer
from .submit_ton_connect_response import SubmitTonConnectResponse
from .submit_ton_connect_result import SubmitTonConnectResult


class Wallet(
    AcceptTonConnectRequest,
    StartTonConnectSession,
    CreateUserWallet,
    CreateWallet,
    DeclineTonConnectRequest,
    DisconnectTonConnectSession,
    DisableWalletBackup,
    EnableWalletBackup,
    ExportWalletSecretPhrase,
    FetchEncryptedSecretPhrasePart,
    GetBackupHolderDcs,
    GetExistingWalletBalance,
    GetTonConnectNextEventId,
    GetTonConnectPending,
    GetTonConnectSessions,
    GetUserWalletAddresses,
    GetProofChallenge,
    GetWalletGaslessInfo,
    GetWalletNfts,
    GetWalletState,
    GetWalletTransactions,
    GetWalletTransactionsByIds,
    GetWalletTransactionsByMsgHash,
    ImportWallet,
    RegisterTonConnectKey,
    ReplaceWallet,
    SendTonTransfer,
    SubmitTonConnectResponse,
    SubmitTonConnectResult,
):
    pass


# Backward compatibility aliases
CloseTonConnectSession = DisconnectTonConnectSession
CreateTonConnectSession = StartTonConnectSession
GetWalletProofChallenge = GetProofChallenge
