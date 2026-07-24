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
import threading
import time

log = logging.getLogger(__name__)


class _MsgIdGenerator:
    def __init__(self):
        self._lock = threading.Lock()
        self.last_time = 0
        self.offset = 0

    def __call__(self) -> int:
        with self._lock:
            now = int(time.time())
            self.offset = (self.offset + 4) if now == self.last_time else 0
            msg_id = (now * 2 ** 32) + self.offset
            self.last_time = now
            return msg_id


MsgId = _MsgIdGenerator()  # module-level singleton for backward compat
