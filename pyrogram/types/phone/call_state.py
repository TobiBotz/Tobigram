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

from __future__ import annotations

from enum import Enum


class CallState(str, Enum):
    """Voice Chat / Call connection state."""

    IDLE = "idle"
    """Idle, no active stream."""

    CONNECTING = "connecting"
    """Establishing WebRTC handshake."""

    PLAYING = "playing"
    """Actively streaming media."""

    PAUSED = "paused"
    """Media stream is paused."""

    MUTED = "muted"
    """Client is muted in the call."""

    ENDED = "ended"
    """Call has ended or disconnected."""
