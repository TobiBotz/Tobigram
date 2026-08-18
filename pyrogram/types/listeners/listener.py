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


import asyncio
from typing import Callable, Optional, Tuple, Union

import pyrogram

from .identifier import Identifier

UNSET = object()


class Listener:
    """A pending wait for a future update.

    Parameters:
        listener_type (:obj:`~pyrogram.enums.ListenerTypes`):
            Kind of update being awaited.

        identifier (:obj:`~pyrogram.types.Identifier`):
            Criteria the update must match.

        filters (:obj:`~pyrogram.filters.Filter`, *optional*):
            Extra filter the update must pass.

        future (``asyncio.Future``, *optional*):
            Resolved with the matching update. Mutually exclusive with *callback*.

        callback (``Callable``, *optional*):
            Invoked with the matching update. Mutually exclusive with *future*.

        unallowed_click_alert (``bool`` | ``str``, *optional*):
            Answer text shown to a user clicking a button this listener does not
            expect from them. ``True`` uses the client default, ``False`` disables it.
    """

    __slots__ = (
        "listener_type",
        "identifier",
        "filters",
        "future",
        "callback",
        "unallowed_click_alert",
        "keys",
    )

    def __init__(
        self,
        listener_type: "pyrogram.enums.ListenerTypes",
        identifier: Identifier,
        filters: Optional["pyrogram.filters.Filter"] = None,
        future: Optional[asyncio.Future] = None,
        callback: Optional[Callable] = None,
        unallowed_click_alert: Union[bool, str] = True,
    ):
        if (future is None) == (callback is None):
            raise ValueError("A listener needs exactly one of future or callback")

        self.listener_type = listener_type
        self.identifier = identifier
        self.filters = filters
        self.future = future
        self.callback = callback
        self.unallowed_click_alert = unallowed_click_alert
        self.keys: Tuple = ()

    @property
    def pending(self) -> bool:
        if self.callback is not None:
            return True

        return self.future is not None and not self.future.done()

    def detach(self) -> None:
        self.future = None
        self.filters = None
        self.callback = None

    def __repr__(self) -> str:
        return (
            f"pyrogram.types.Listener(listener_type={self.listener_type}, "
            f"identifier={self.identifier!r})"
        )
