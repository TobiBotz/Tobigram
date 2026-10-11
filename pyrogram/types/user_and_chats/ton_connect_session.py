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

from pyrogram import raw, utils
from ..object import Object

if TYPE_CHECKING:
    from datetime import datetime
    import pyrogram


class TonConnectSession(Object):
    """Contains information about an active TON Connect decentralized app session.

    Parameters:
        id (``int``):
            Unique identifier of the TON Connect session.

        dapp_client_id (``str``):
            Client identifier of the decentralized application.

        client_id (``str``, *optional*):
            Registered client identifier.

        date (:py:obj:`~datetime.datetime`):
            Creation date of the session.

        is_pending (``bool``):
            True if session handshake is pending approval.

        is_closing (``bool``):
            True if the session is currently closing.

        is_closed (``bool``):
            True if the session is terminated.

        manifest_url (``str``, *optional*):
            URL to the dApp manifest.

        manifest_name (``str``, *optional*):
            Branding name of the decentralized application.

        manifest_icon_url (``str``, *optional*):
            URL to the dApp icon.

        manifest_error (``int``, *optional*):
            Error code while loading the manifest, if any.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        id: int,
        dapp_client_id: str,
        date: datetime,
        client_id: str | None = None,
        is_pending: bool = False,
        is_closing: bool = False,
        is_closed: bool = False,
        manifest_url: str | None = None,
        manifest_name: str | None = None,
        manifest_icon_url: str | None = None,
        manifest_error: int | None = None,
    ):
        super().__init__(client)

        self.id = id
        self.dapp_client_id = dapp_client_id
        self.date = date
        self.client_id = client_id
        self.is_pending = is_pending
        self.is_closing = is_closing
        self.is_closed = is_closed
        self.manifest_url = manifest_url
        self.manifest_name = manifest_name
        self.manifest_icon_url = manifest_icon_url
        self.manifest_error = manifest_error

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        session: raw.types.TonConnectSession,
    ) -> TonConnectSession | None:
        if not session:
            return None

        manifest_url = None
        manifest_name = None
        manifest_icon_url = None

        if session.manifest:
            manifest_url = session.manifest.url
            manifest_name = session.manifest.name
            if session.manifest.icon and hasattr(session.manifest.icon, "url"):
                manifest_icon_url = session.manifest.icon.url

        return TonConnectSession(
            client=client,
            id=session.id,
            dapp_client_id=session.dapp_client_id,
            client_id=session.client_id,
            date=utils.timestamp_to_datetime(session.date),
            is_pending=bool(session.pending),
            is_closing=bool(session.closing),
            is_closed=bool(session.closed),
            manifest_url=manifest_url,
            manifest_name=manifest_name,
            manifest_icon_url=manifest_icon_url,
            manifest_error=session.manifest_error,
        )
