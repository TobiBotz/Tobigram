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

from .get_collectible_info import GetCollectibleInfo
from .get_file_hashes import GetFileHashes
from .get_web_file import GetWebFile
from .init_connection import InitConnection
from .invoke import Invoke
from .invoke_after_msg import InvokeAfterMsg
from .invoke_after_msgs import InvokeAfterMsgs
from .invoke_with_apns_secret import InvokeWithApnsSecret
from .invoke_with_google_play_integrity import InvokeWithGooglePlayIntegrity
from .invoke_with_layer import InvokeWithLayer
from .invoke_with_messages_range import InvokeWithMessagesRange
from .recover_gaps import RecoverGaps
from .resolve_peer import ResolvePeer
from .save_file import SaveFile


class Advanced(
    GetCollectibleInfo,
    GetFileHashes,
    GetWebFile,
    InitConnection,
    Invoke,
    InvokeAfterMsg,
    InvokeAfterMsgs,
    InvokeWithApnsSecret,
    InvokeWithGooglePlayIntegrity,
    InvokeWithLayer,
    InvokeWithMessagesRange,
    RecoverGaps,
    ResolvePeer,
    SaveFile,
):
    pass
