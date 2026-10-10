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

from typing import TYPE_CHECKING

from pyrogram import utils

if TYPE_CHECKING:
    from datetime import datetime

    from pyrogram import raw

from ..object import Object


class WalletTonConnectRequest(Object):
    """A Wallet TON Connect request service message.

    Parameters:
        session_id (``int``):
            Session identifier.

        expires (:py:obj:`~datetime.datetime`):
            Point in time when the request expires.

        accepted (``bool``, *optional*):
            Whether the request was accepted.

        declined (``bool``, *optional*):
            Whether the request was declined.

        topic (``str``, *optional*):
            Request topic.

        trace_id (``str``, *optional*):
            Trace identifier.

        dapp_name (``str``, *optional*):
            Decentralized app name.
    """

    def __init__(
        self,
        *,
        session_id: int,
        expires: datetime,
        accepted: bool | None = None,
        declined: bool | None = None,
        topic: str | None = None,
        trace_id: str | None = None,
        dapp_name: str | None = None,
    ):
        super().__init__()

        self.session_id = session_id
        self.expires = expires
        self.accepted = accepted
        self.declined = declined
        self.topic = topic
        self.trace_id = trace_id
        self.dapp_name = dapp_name

    @staticmethod
    def _parse(
        client,
        action: raw.types.MessageActionWalletTonConnectRequest,
    ) -> WalletTonConnectRequest:
        return WalletTonConnectRequest(
            session_id=action.session_id,
            expires=utils.timestamp_to_datetime(action.expires),
            accepted=action.accepted,
            declined=action.declined,
            topic=action.topic,
            trace_id=action.trace_id,
            dapp_name=action.dapp_name,
        )
