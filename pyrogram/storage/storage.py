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

import base64
import logging
import struct
import zlib
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from pyrogram import raw

log = logging.getLogger(__name__)


class Storage(ABC):
    OLD_SESSION_STRING_FORMAT = ">B?256sI?"
    OLD_SESSION_STRING_FORMAT_64 = ">B?256sQ?"
    SESSION_STRING_SIZE = 351
    SESSION_STRING_SIZE_64 = 356

    SESSION_STRING_FORMAT = ">BI?256sQ?"
    SESSION_STRING_SIZE_CURRENT = 362

    SESSION_STRING_FORMAT_V2 = ">BBI?256sQ?H16s"
    SESSION_STRING_SIZE_V2 = 387

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def open(self):
        """Opens the storage engine."""
        raise NotImplementedError

    @abstractmethod
    async def save(self):
        """Saves the current state of the storage engine."""
        raise NotImplementedError

    @abstractmethod
    async def close(self):
        """Closes the storage engine."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self):
        """Deletes the storage file."""
        raise NotImplementedError

    @abstractmethod
    async def update_peers(self, peers: List[Tuple[int, int, str, str]]) -> None:
        """
        Update the peers table with the provided information.

        Parameters:
            peers (``List[Tuple[int, int, str, str]]``):
                A list of tuples containing the
                information of the peers to be updated. Each tuple must contain the following
                information:
                - ``int``: The peer id.
                - ``int``: The peer access hash.
                - ``str``: The peer type (user, chat or channel).
                - ``str``: The peer phone number (if any).
        """
        raise NotImplementedError

    @abstractmethod
    async def update_usernames(self, usernames: List[Tuple[int, List[str]]]) -> None:
        """
        Update the usernames table with the provided information.

        Parameters:
            usernames (``List[Tuple[int, List[str]]]``):
                A list of tuples containing the
                information of the usernames to be updated. Each tuple must contain the following
                information:
                - ``int``: The peer id.
                - List of ``str``: The peer username (if any).
        """
        raise NotImplementedError

    @abstractmethod
    async def update_state(self, update_state: Tuple[int, int, int, int, int] = object) -> Tuple[int, int, int, int, int]:
        """Get or set the update state of the current session.

        Parameters:
            update_state (``Tuple[int, int, int, int, int]``):
                A tuple containing the update state to set.
                Tuple must contain the following information:
                - ``int``: The id of the entity.
                - ``int``: The pts.
                - ``int``: The qts.
                - ``int``: The date.
                - ``int``: The seq.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_peer_by_id(self, peer_id: int) -> "raw.base.InputPeer":
        """Retrieve a peer by its ID.

        Parameters:
            peer_id (``int``):
                The ID of the peer to retrieve.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_peer_by_username(self, username: str) -> "raw.base.InputPeer":
        """Retrieve a peer by its username.

        Parameters:
            username (``str``):
                The username of the peer to retrieve.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_peer_by_phone_number(self, phone_number: str) -> "raw.base.InputPeer":
        """Retrieve a peer by its phone number.

        Parameters:
            phone_number (``str``):
                The phone number of the peer to retrieve.
        """
        raise NotImplementedError

    @abstractmethod
    async def dc_id(self, value: int = object) -> int:
        """Get or set the DC ID of the current session.

        Parameters:
            value (``int``, *optional*):
                The DC ID to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def api_id(self, value: int = object) -> int:
        """Get or set the API ID of the current session.

        Parameters:
            value (``int``, *optional*):
                The API ID to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def server_address(self, value: str = object) -> str:
        """Get or set the server address of the current session.

        Parameters:
            value (``str``, *optional*):
                The server address to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def port(self, value: int = object) -> int:
        """Get or set the server port of the current session.

        Parameters:
            value (``int``, *optional*):
                The server port to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def test_mode(self, value: bool = object) -> bool:
        """Get or set the test mode of the current session.

        Parameters:
            value (``bool``, *optional*):
                The test mode to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def auth_key(self, value: bytes = object) -> bytes:
        """Get or set the authorization key of the current session.

        Parameters:
            value (``bytes``, *optional*):
                The authorization key to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def date(self, value: int = object) -> int:
        """Get or set the date of the current session.

        Parameters:
            value (``int``, *optional*):
                The date to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def user_id(self, value: int = object) -> int:
        """Get or set the user ID of the current session.

        Parameters:
            value (``int``, *optional*):
                The user ID to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def is_bot(self, value: bool = object) -> bool:
        """Get or set the bot flag of the current session.

        Parameters:
            value (``bool``, *optional*):
                The bot flag to set.
        """
        raise NotImplementedError

    async def export_session_string(self) -> str:
        dc_id = await self.dc_id()
        api_id = await self.api_id()
        test_mode = await self.test_mode()
        auth_key = await self.auth_key()
        user_id = await self.user_id()
        is_bot = await self.is_bot()
        port = await self.port()
        server_address = await self.server_address()

        if any(v is None for v in (dc_id, api_id, test_mode, auth_key, user_id, is_bot, port, server_address)):
            raise ValueError(
                "Cannot export session string: some required fields are missing. "
                "Make sure the client is fully initialized."
            )

        addr_bytes = server_address.encode("ascii").ljust(16, b"\x00")[:16]

        packed = struct.pack(
            self.SESSION_STRING_FORMAT_V2,
            2,              # version
            dc_id,
            api_id,
            test_mode,
            auth_key,
            user_id,
            is_bot,
            port,
            addr_bytes,
        )

        return base64.urlsafe_b64encode(packed).decode().rstrip("=")

    @staticmethod
    def _decode_session_string(
        session_string: str,
    ) -> dict:
        if session_string.startswith("WZ_"):
            session_string = session_string[3:]
        raw = base64.urlsafe_b64decode(session_string + "=" * (-len(session_string) % 4))
        length = len(raw)

        if length == 294:
            payload = raw[:-4]
            stored_crc = struct.unpack("<I", raw[-4:])[0]
            if zlib.crc32(payload) != stored_crc:
                raise ValueError("Session string CRC mismatch")
            raw = payload
            length = len(raw)

        if length == 263:
            dc_id, test_mode, auth_key, user_id, is_bot = struct.unpack(
                Storage.OLD_SESSION_STRING_FORMAT, raw
            )
            log.warning("Old session string format without api_id; upgrade by re-exporting")
            return dict(
                dc_id=dc_id, api_id=None, test_mode=test_mode,
                auth_key=auth_key, user_id=user_id, is_bot=is_bot,
                port=None, server_address=None,
            )

        if length == 267:
            dc_id, test_mode, auth_key, user_id, is_bot = struct.unpack(
                Storage.OLD_SESSION_STRING_FORMAT_64, raw
            )
            log.warning("Old session string format without api_id; upgrade by re-exporting")
            return dict(
                dc_id=dc_id, api_id=None, test_mode=test_mode,
                auth_key=auth_key, user_id=user_id, is_bot=is_bot,
                port=None, server_address=None,
            )

        if length == 271:
            dc_id, api_id, test_mode, auth_key, user_id, is_bot = struct.unpack(
                Storage.SESSION_STRING_FORMAT, raw
            )
            return dict(
                dc_id=dc_id, api_id=api_id, test_mode=test_mode,
                auth_key=auth_key, user_id=user_id, is_bot=is_bot,
                port=None, server_address=None,
            )

        if length == 290:
            _, dc_id, api_id, test_mode, auth_key, user_id, is_bot, port, addr_bytes = struct.unpack(
                Storage.SESSION_STRING_FORMAT_V2, raw
            )
            server_address = addr_bytes.rstrip(b"\x00").decode("ascii")
            return dict(
                dc_id=dc_id, api_id=api_id, test_mode=test_mode,
                auth_key=auth_key, user_id=user_id, is_bot=is_bot,
                port=port, server_address=server_address,
            )

        raise ValueError(
            f"Invalid session string: unexpected length {length} bytes. "
            "The session string may be corrupted or from an incompatible version."
        )

