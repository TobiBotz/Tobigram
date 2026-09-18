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

from datetime import datetime

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object


class StarsTransaction(Object):
    """Contains information about a Telegram Stars transaction.

    Parameters:
        id (``str``):
            Unique identifier of the transaction.

        amount (``float``):
            Amount of Stars credited (+) or debited (-).

        date (:py:obj:`~datetime.datetime`):
            Date the transaction took place.

        raw_amount (:obj:`~pyrogram.types.StarAmount`, *optional*):
            Raw StarAmount object containing whole stars and nano fractions.

        peer (``str`` | :obj:`~pyrogram.types.User` | :obj:`~pyrogram.types.Chat`, *optional*):
            Source or destination of the transaction. Can be a string ("play_market",
            "fragment", "premium_bot", "ads", "api") or a resolved User/Chat.

        user (:obj:`~pyrogram.types.User`, *optional*):
            The user involved in the transaction, if applicable.

        chat (:obj:`~pyrogram.types.Chat`, *optional*):
            The chat / channel involved in the transaction, if applicable.

        refund (``bool``, *optional*):
            True, if the transaction was refunded.

        pending (``bool``, *optional*):
            True, if the transaction is currently pending.

        failed (``bool``, *optional*):
            True, if the transaction failed.

        gift (``bool``, *optional*):
            True, if the transaction is related to a Star gift.

        reaction (``bool``, *optional*):
            True, if the transaction is for a paid reaction.

        title (``str``, *optional*):
            Title of the purchased digital goods or service.

        description (``str``, *optional*):
            Description of the transaction.

        bot_payload (``bytes``, *optional*):
            Bot-specified invoice payload.

        msg_id (``int``, *optional*):
            Identifier of the message containing the paid media or invoice.

        transaction_date (:py:obj:`~datetime.datetime`, *optional*):
            Date of the external transaction (e.g. app store or Fragment).

        transaction_url (``str``, *optional*):
            URL of the external transaction receipt.

        subscription_period (``int``, *optional*):
            The subscription period in seconds, if this transaction was for a star subscription.

        giveaway_post_id (``int``, *optional*):
            The message ID of the giveaway in the chat, if applicable.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        id: str,
        amount: float,
        date: datetime,
        raw_amount: types.StarAmount | None = None,
        peer: str | types.User | types.Chat | None = None,
        user: types.User | None = None,
        chat: types.Chat | None = None,
        refund: bool = False,
        pending: bool = False,
        failed: bool = False,
        gift: bool = False,
        reaction: bool = False,
        title: str | None = None,
        description: str | None = None,
        bot_payload: bytes | None = None,
        msg_id: int | None = None,
        transaction_date: datetime | None = None,
        transaction_url: str | None = None,
        subscription_period: int | None = None,
        giveaway_post_id: int | None = None,
    ):
        super().__init__(client)

        self.id = id
        self.amount = amount
        self.date = date
        self.raw_amount = raw_amount
        self.peer = peer
        self.user = user
        self.chat = chat
        self.refund = refund
        self.pending = pending
        self.failed = failed
        self.gift = gift
        self.reaction = reaction
        self.title = title
        self.description = description
        self.bot_payload = bot_payload
        self.msg_id = msg_id
        self.transaction_date = transaction_date
        self.transaction_url = transaction_url
        self.subscription_period = subscription_period
        self.giveaway_post_id = giveaway_post_id

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        transaction: raw.types.StarsTransaction,
        users: dict[int, raw.types.User],
        chats: dict[int, raw.types.Chat],
    ) -> StarsTransaction:
        user = None
        chat = None
        parsed_peer = None

        raw_peer = transaction.peer
        if isinstance(raw_peer, raw.types.StarsTransactionPeer):
            peer_id = utils.get_raw_peer_id(raw_peer.peer)
            if peer_id in users:
                user = types.User._parse(client, users[peer_id])
                parsed_peer = user
            elif peer_id in chats:
                chat = types.Chat._parse_chat(client, chats[peer_id])
                parsed_peer = chat
        elif isinstance(raw_peer, raw.types.StarsTransactionPeerPlayMarket):
            parsed_peer = "play_market"
        elif isinstance(raw_peer, raw.types.StarsTransactionPeerPremiumBot):
            parsed_peer = "premium_bot"
        elif isinstance(raw_peer, raw.types.StarsTransactionPeerFragment):
            parsed_peer = "fragment"
        elif isinstance(raw_peer, raw.types.StarsTransactionPeerAds):
            parsed_peer = "ads"
        elif isinstance(raw_peer, raw.types.StarsTransactionPeerAPI):
            parsed_peer = "api"

        amount_val = 0.0
        if getattr(transaction, "amount", None) is not None:
            amount_val = transaction.amount.amount + (transaction.amount.nanos or 0) / 1e9

        return StarsTransaction(
            client=client,
            id=transaction.id,
            amount=amount_val,
            date=utils.timestamp_to_datetime(transaction.date),
            raw_amount=types.StarAmount._parse(transaction.amount),
            peer=parsed_peer,
            user=user,
            chat=chat,
            refund=getattr(transaction, "refund", False) or False,
            pending=getattr(transaction, "pending", False) or False,
            failed=getattr(transaction, "failed", False) or False,
            gift=getattr(transaction, "gift", False) or False,
            reaction=getattr(transaction, "reaction", False) or False,
            title=getattr(transaction, "title", None),
            description=getattr(transaction, "description", None),
            bot_payload=getattr(transaction, "bot_payload", None),
            msg_id=getattr(transaction, "msg_id", None),
            transaction_date=utils.timestamp_to_datetime(
                getattr(transaction, "transaction_date", None)
            ),
            transaction_url=getattr(transaction, "transaction_url", None),
            subscription_period=getattr(transaction, "subscription_period", None),
            giveaway_post_id=getattr(transaction, "giveaway_post_id", None),
        )
