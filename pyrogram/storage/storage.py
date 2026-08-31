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

import logging
import struct
import zlib
from abc import ABC, abstractmethod
from typing import List, Tuple

from pyrogram import raw

log = logging.getLogger(__name__)

SESSION_STRING_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
SESSION_STRING_DECODE = {c: i for i, c in enumerate(SESSION_STRING_ALPHABET)}
WZ_PREFIX = "WZ_"

TEST = {
    1: "149.154.175.10",
    2: "149.154.167.40",
    3: "149.154.175.117"
}

PROD = {
    1: "149.154.175.53",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.130",
    203: "91.105.192.100"
}


class Storage(ABC):
    V2_PACKED_SIZE = 290
    V2_CRC_PACKED_SIZE = 294
    SESSION_STRING_FORMAT_V2 = ">BBI?256sQ?H16s"
    V3_PACKED_SIZE = 322
    V3_CRC_PACKED_SIZE = 326
    SESSION_STRING_FORMAT_V3 = ">BBI?256sQ?H48s"
    SERVER_ADDRESS_SIZE = 48

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def open(self):
        raise NotImplementedError

    @abstractmethod
    async def save(self):
        raise NotImplementedError

    @abstractmethod
    async def close(self):
        raise NotImplementedError

    @abstractmethod
    async def delete(self):
        raise NotImplementedError

    @abstractmethod
    async def update_peers(self, peers: List[Tuple[int, int, str, str]]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_usernames(self, usernames: List[Tuple[int, List[str]]]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_state(self, update_state: Tuple[int, int, int, int, int] = object) -> Tuple[int, int, int, int, int]:
        raise NotImplementedError

    @abstractmethod
    async def get_peer_by_id(self, peer_id: int) -> "raw.base.InputPeer":
        raise NotImplementedError

    @abstractmethod
    async def get_peer_by_username(self, username: str) -> "raw.base.InputPeer":
        raise NotImplementedError

    @abstractmethod
    async def get_peer_by_phone_number(self, phone_number: str) -> "raw.base.InputPeer":
        raise NotImplementedError

    @abstractmethod
    async def dc_id(self, value: int = object) -> int:
        raise NotImplementedError

    @abstractmethod
    async def api_id(self, value: int = object) -> int:
        raise NotImplementedError

    @abstractmethod
    async def server_address(self, value: str = object) -> str:
        raise NotImplementedError

    @abstractmethod
    async def port(self, value: int = object) -> int:
        raise NotImplementedError

    @abstractmethod
    async def test_mode(self, value: bool = object) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def auth_key(self, value: bytes = object) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def date(self, value: int = object) -> int:
        raise NotImplementedError

    @abstractmethod
    async def user_id(self, value: int = object) -> int:
        raise NotImplementedError

    @abstractmethod
    async def is_bot(self, value: bool = object) -> bool:
        raise NotImplementedError

    @staticmethod
    def _encode(raw: bytes) -> str:
        result = []
        for i in range(0, len(raw), 3):
            chunk = raw[i:i + 3]
            if len(chunk) == 3:
                n = (chunk[0] << 16) | (chunk[1] << 8) | chunk[2]
                result.append(SESSION_STRING_ALPHABET[(n >> 18) & 63])
                result.append(SESSION_STRING_ALPHABET[(n >> 12) & 63])
                result.append(SESSION_STRING_ALPHABET[(n >> 6) & 63])
                result.append(SESSION_STRING_ALPHABET[n & 63])
            elif len(chunk) == 2:
                n = (chunk[0] << 8) | chunk[1]
                result.append(SESSION_STRING_ALPHABET[(n >> 10) & 63])
                result.append(SESSION_STRING_ALPHABET[(n >> 4) & 63])
                result.append(SESSION_STRING_ALPHABET[(n << 2) & 63])
            else:
                n = chunk[0]
                result.append(SESSION_STRING_ALPHABET[(n >> 2) & 63])
                result.append(SESSION_STRING_ALPHABET[(n << 4) & 63])
        return "".join(result)

    @staticmethod
    def _decode(s: str) -> bytes:
        result = bytearray()
        i = 0
        while i < len(s):
            if i + 4 <= len(s):
                n = 0
                for c in s[i:i + 4]:
                    n = (n << 6) | SESSION_STRING_DECODE[c]
                result.append((n >> 16) & 255)
                result.append((n >> 8) & 255)
                result.append(n & 255)
                i += 4
            elif i + 3 == len(s):
                n = 0
                for c in s[i:]:
                    n = (n << 6) | SESSION_STRING_DECODE[c]
                n >>= 2
                result.append((n >> 8) & 255)
                result.append(n & 255)
                i += 3
            elif i + 2 == len(s):
                n = 0
                for c in s[i:]:
                    n = (n << 6) | SESSION_STRING_DECODE[c]
                n >>= 4
                result.append(n & 255)
                i += 2
            else:
                raise ValueError(
                    "Session string corruption: unexpected character count in encoding"
                )
        return bytes(result)

    @staticmethod
    def _try_decode_v3(raw: bytes):
        if len(raw) != Storage.V3_PACKED_SIZE:
            return None
        _, dc_id, api_id, test_mode, auth_key, user_id, is_bot, port, addr_bytes = struct.unpack(
            Storage.SESSION_STRING_FORMAT_V3, raw
        )
        server_address = addr_bytes.rstrip(b"\x00").decode("ascii")
        return dict(
            dc_id=dc_id, api_id=api_id, test_mode=test_mode,
            auth_key=auth_key, user_id=user_id, is_bot=is_bot,
            port=port, server_address=server_address,
        )

    @staticmethod
    def _try_decode_v3_with_crc(raw: bytes):
        if len(raw) != Storage.V3_CRC_PACKED_SIZE:
            return None
        payload = raw[:-4]
        stored_crc = struct.unpack("<I", raw[-4:])[0]
        if zlib.crc32(payload) != stored_crc:
            return None
        return Storage._try_decode_v3(payload)

    @staticmethod
    def _try_decode_v2(raw: bytes):
        if len(raw) != Storage.V2_PACKED_SIZE:
            return None
        _, dc_id, api_id, test_mode, auth_key, user_id, is_bot, port, addr_bytes = struct.unpack(
            Storage.SESSION_STRING_FORMAT_V2, raw
        )
        server_address = addr_bytes.rstrip(b"\x00").decode("ascii")
        return dict(
            dc_id=dc_id, api_id=api_id, test_mode=test_mode,
            auth_key=auth_key, user_id=user_id, is_bot=is_bot,
            port=port, server_address=server_address,
        )

    @staticmethod
    def _try_decode_v2_with_crc(raw: bytes):
        if len(raw) != Storage.V2_CRC_PACKED_SIZE:
            return None
        payload = raw[:-4]
        stored_crc = struct.unpack("<I", raw[-4:])[0]
        if zlib.crc32(payload) != stored_crc:
            return None
        return Storage._try_decode_v2(payload)

    @staticmethod
    def _validate_char_set(s: str) -> str:
        clean = []
        for c in s:
            if c in SESSION_STRING_DECODE:
                clean.append(c)
        return "".join(clean)

    @staticmethod
    def _strip_prefix(s: str) -> Tuple[str, bool]:
        if s.startswith(WZ_PREFIX):
            return s[len(WZ_PREFIX):], True
        return s, False

    @staticmethod
    def _try_decode_legacy(raw: bytes):
        if len(raw) not in (263, 267, 271):
            return None

        log.warning(
            "Session string uses legacy format (pre-V2). "
            "This format is deprecated and will be removed in future versions. "
            "Please re-export your session string."
        )

        if len(raw) == 271:
            dc_id, api_id, test_mode, auth_key, user_id, is_bot = struct.unpack(
                ">BI?256sQ?", raw
            )
            return dict(
                dc_id=dc_id, api_id=api_id, test_mode=test_mode,
                auth_key=auth_key, user_id=user_id, is_bot=is_bot,
                port=None, server_address=None,
            )

        if len(raw) == 267:
            dc_id, test_mode, auth_key, user_id, is_bot = struct.unpack(
                ">B?256sQ?", raw
            )
        else:
            dc_id, test_mode, auth_key, user_id, is_bot = struct.unpack(
                ">B?256sI?", raw
            )

        return dict(
            dc_id=dc_id, api_id=None, test_mode=test_mode,
            auth_key=auth_key, user_id=user_id, is_bot=is_bot,
            port=None, server_address=None,
        )

    @staticmethod
    def _try_every_format(raw: bytes, allow_unverified: bool):
        result = Storage._try_decode_v3_with_crc(raw) or Storage._try_decode_v2_with_crc(raw)

        if result:
            return result

        if not allow_unverified:
            return None

        result = Storage._try_decode_v3(raw) or Storage._try_decode_v2(raw)

        if result:
            log.warning(
                "Session string uses old format without CRC checksum. "
                "Consider re-exporting for integrity verification."
            )
            return result

        return Storage._try_decode_legacy(raw)

    @staticmethod
    def _decode_session_string(session_string: str) -> dict:
        s = session_string.strip()
        if not s:
            raise ValueError("Session string is empty")

        body, _ = Storage._strip_prefix(s)
        clean = Storage._validate_char_set(body)

        try:
            raw = Storage._decode(clean)
        except (KeyError, ValueError):
            raw = None

        if raw is not None:
            result = Storage._try_every_format(raw, allow_unverified=True)

            if result:
                return result

        for attempt in Storage._repair_attempts(clean):
            if attempt == clean:
                continue

            try:
                raw = Storage._decode(attempt)
            except (KeyError, ValueError):
                continue

            result = Storage._try_every_format(raw, allow_unverified=False)

            if result:
                log.info("Session string auto-repaired successfully")
                return result

        raise ValueError(
            "Session string is corrupted: after auto-repair attempts, "
            "none of the decoded values passed integrity check. "
            "Please re-export your session string."
        )

    @staticmethod
    def _repair_attempts(s: str):
        yield s

        for c in SESSION_STRING_ALPHABET:
            yield c + s
            yield s + c

        for c1 in SESSION_STRING_ALPHABET:
            for c2 in SESSION_STRING_ALPHABET:
                pair = c1 + c2
                yield pair + s
                yield s + pair

    async def load_session_string(self, session_string: str) -> None:
        """Fill this storage in from an exported session string.

        Every accessor it calls is part of the abstract surface, so this works
        for any engine - a remote one included - and is the partner of
        :meth:`export_session_string`.
        """
        data = self._decode_session_string(session_string)

        await self.dc_id(data["dc_id"])
        await self.test_mode(data["test_mode"])
        await self.auth_key(data["auth_key"])
        await self.user_id(data["user_id"])
        await self.is_bot(data["is_bot"])
        await self.date(0)

        table = TEST if data["test_mode"] else PROD
        default_address = table.get(data["dc_id"])

        if data["server_address"]:
            await self.server_address(data["server_address"])
            await self.port(data["port"] or (80 if data["test_mode"] else 443))
        elif default_address is not None:
            await self.server_address(default_address)
            await self.port(80 if data["test_mode"] else 443)

        if data["api_id"] is not None:
            await self.api_id(data["api_id"])

    async def export_session_string(self) -> str:
        dc_id = await self.dc_id()
        api_id = await self.api_id()
        test_mode = await self.test_mode()
        auth_key = await self.auth_key()
        user_id = await self.user_id()
        is_bot = await self.is_bot()
        port = await self.port()
        server_address = await self.server_address()

        if any(v is None for v in (dc_id, test_mode, auth_key, user_id, is_bot)):
            raise ValueError(
                "Cannot export session string: some required fields are missing. "
                "Make sure the client is fully initialized."
            )

        addr_bytes = (server_address or "").encode("ascii")

        if len(addr_bytes) > self.SERVER_ADDRESS_SIZE:
            raise ValueError(
                f"Cannot export session string: server address {server_address!r} is longer than "
                f"{self.SERVER_ADDRESS_SIZE} bytes."
            )

        addr_bytes = addr_bytes.ljust(self.SERVER_ADDRESS_SIZE, b"\x00")

        packed = struct.pack(
            self.SESSION_STRING_FORMAT_V3,
            3,
            dc_id,
            api_id or 0,
            test_mode,
            auth_key,
            user_id,
            is_bot,
            port or 0,
            addr_bytes,
        )

        crc = struct.pack("<I", zlib.crc32(packed))
        return WZ_PREFIX + Storage._encode(packed + crc)
