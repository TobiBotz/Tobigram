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

import os
import time
from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple

from pyrogram import raw

from .. import utils

PEER_CACHE_SIZE = int(os.environ.get("WZGRAM_PEER_CACHE", 4096))
PEER_WRITE_TTL = 60 * 60


def get_input_peer(peer_id: int, access_hash: int, peer_type: str) -> "raw.base.InputPeer":
    if peer_type in ["user", "bot"]:
        return raw.types.InputPeerUser(
            user_id=peer_id,
            access_hash=access_hash
        )

    if peer_type == "group":
        return raw.types.InputPeerChat(
            chat_id=-peer_id
        )

    if peer_type in ["direct", "channel", "forum", "supergroup"]:
        return raw.types.InputPeerChannel(
            channel_id=utils.get_channel_id(peer_id),
            access_hash=access_hash
        )

    raise ValueError(f"Invalid peer type: {peer_type}")


class PeerRowCache:
    """Bounded cache of peer rows, in front of whatever storage engine owns them.

    It holds the **row**, not the ``InputPeer`` built from it: callers hand those
    to the API and are free to mutate them, so a shared instance would be shared
    mutable state. Rebuilding one costs a microsecond against the ~125us a query
    costs, or a network round trip on a remote engine.
    """

    def __init__(self, size: int = PEER_CACHE_SIZE, write_ttl: float = PEER_WRITE_TTL):
        self.size = size
        self.write_ttl = write_ttl
        self._rows: "OrderedDict[int, Tuple[Tuple[int, int, str], Optional[str], Optional[float]]]" = OrderedDict()

    def __len__(self) -> int:
        return len(self._rows)

    def get(self, peer_id: int) -> Optional[Tuple[int, int, str]]:
        entry = self._rows.get(peer_id)

        return entry[0] if entry is not None else None

    def matches(
        self,
        peer_id: int,
        access_hash: int,
        peer_type: str,
        phone_number: Optional[str] = None
    ) -> bool:
        entry = self._rows.get(peer_id)

        if entry is None:
            return False

        row, phone, written_at = entry

        if written_at is None or time.monotonic() - written_at > self.write_ttl:
            return False

        return row == (peer_id, access_hash, peer_type) and phone == phone_number

    def remember(
        self,
        row: Tuple[int, int, str],
        phone_number: Optional[str] = None,
        written: bool = False
    ) -> None:
        rows = self._rows

        rows.pop(row[0], None)
        rows[row[0]] = (
            tuple(row),
            phone_number,
            time.monotonic() if written else None
        )

        if len(rows) > self.size:
            while len(rows) > self.size:
                rows.popitem(last=False)

    def forget(self, peer_id: int) -> None:
        self._rows.pop(peer_id, None)

    def clear(self) -> None:
        self._rows.clear()


class SessionAttrCache:
    """The session row held in memory, so ``dc_id()`` on the send path is a dict
    lookup rather than a query or a round trip.

    A missing column and a column holding ``None`` are different states: the
    first has to be read once, the second must not be re-read on every call.
    ``MISSING`` is what keeps them apart.
    """

    MISSING = object()

    def __init__(self):
        self._values: Dict[str, Any] = {}

    def __contains__(self, attr: str) -> bool:
        return attr in self._values

    def get(self, attr: str) -> Any:
        value = self._values[attr]
        return None if value is self.MISSING else value

    def set(self, attr: str, value: Any) -> None:
        self._values[attr] = value

    def remember(self, attr: str, value: Any) -> None:
        self._values[attr] = self.MISSING if value is None else value

    def load(self, values: Dict[str, Any]) -> None:
        for attr, value in values.items():
            self._values[attr] = value

    def snapshot(self) -> Dict[str, Any]:
        return {
            attr: (None if value is self.MISSING else value)
            for attr, value in self._values.items()
        }

    def clear(self) -> None:
        self._values.clear()
