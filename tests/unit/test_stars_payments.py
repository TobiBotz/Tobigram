from unittest.mock import AsyncMock
import pytest
from pyrogram import Client, raw, types


@pytest.mark.asyncio
async def test_get_stars_transactions_inbound():
    client = Client("test", in_memory=True)

    raw_tx = raw.types.StarsTransaction(
        id="tx_1001",
        amount=raw.types.StarsAmount(amount=50, nanos=500000000),
        date=1700000000,
        peer=raw.types.StarsTransactionPeer(peer=raw.types.PeerUser(user_id=123)),
        title="Exclusive Video",
        description="Access to private video",
        bot_payload=b"order_999",
        msg_id=42,
        reaction=False,
        gift=False,
    )
    raw_user = raw.types.User(
        id=123,
        first_name="Alice",
        usernames=[],
        restriction_reason=[],
    )

    client.invoke = AsyncMock(
        return_value=raw.types.payments.StarsStatus(
            balance=raw.types.StarsAmount(amount=500, nanos=0),
            history=[raw_tx],
            chats=[],
            users=[raw_user],
            next_offset=None,
        )
    )

    transactions = []
    async for tx in client.get_stars_transactions(inbound=True, limit=1):
        transactions.append(tx)

    assert len(transactions) == 1
    tx = transactions[0]
    assert isinstance(tx, types.StarsTransaction)
    assert tx.id == "tx_1001"
    assert tx.amount == 50.5
    assert tx.title == "Exclusive Video"
    assert tx.description == "Access to private video"
    assert tx.bot_payload == b"order_999"
    assert tx.msg_id == 42
    assert tx.user.id == 123
    assert tx.user.first_name == "Alice"

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.payments.GetStarsTransactions)
    assert call_arg.inbound is True
    assert isinstance(call_arg.peer, raw.types.InputPeerSelf)


@pytest.mark.asyncio
async def test_get_stars_transactions_peer_types():
    client = Client("test", in_memory=True)

    raw_tx_market = raw.types.StarsTransaction(
        id="tx_market",
        amount=raw.types.StarsAmount(amount=100, nanos=0),
        date=1700000000,
        peer=raw.types.StarsTransactionPeerPlayMarket(),
    )
    raw_tx_fragment = raw.types.StarsTransaction(
        id="tx_fragment",
        amount=raw.types.StarsAmount(amount=250, nanos=0),
        date=1700000000,
        peer=raw.types.StarsTransactionPeerFragment(),
    )

    client.invoke = AsyncMock(
        return_value=raw.types.payments.StarsStatus(
            balance=raw.types.StarsAmount(amount=1000, nanos=0),
            history=[raw_tx_market, raw_tx_fragment],
            chats=[],
            users=[],
            next_offset=None,
        )
    )

    txs = []
    async for tx in client.get_stars_transactions():
        txs.append(tx)

    assert len(txs) == 2
    assert txs[0].peer == "play_market"
    assert txs[0].amount == 100.0
    assert txs[1].peer == "fragment"
    assert txs[1].amount == 250.0


@pytest.mark.asyncio
async def test_get_stars_revenue_stats():
    client = Client("test", in_memory=True)
    client.resolve_peer = AsyncMock(
        return_value=raw.types.InputPeerChannel(channel_id=999, access_hash=123)
    )

    raw_status = raw.types.StarsRevenueStatus(
        current_balance=raw.types.StarsAmount(amount=1500, nanos=0),
        available_balance=raw.types.StarsAmount(amount=1200, nanos=0),
        overall_revenue=raw.types.StarsAmount(amount=10000, nanos=0),
        withdrawal_enabled=True,
        next_withdrawal_at=1705000000,
    )
    raw_graph = raw.types.StatsGraph(json=raw.types.DataJSON(data="{}"))

    client.invoke = AsyncMock(
        return_value=raw.types.payments.StarsRevenueStats(
            status=raw_status,
            usd_rate=0.013,
            revenue_graph=raw_graph,
        )
    )

    stats = await client.get_stars_revenue_stats(chat_id=999, dark=True)

    assert isinstance(stats, types.StarsRevenueStats)
    assert stats.usd_rate == 0.013
    assert stats.status.current_balance == 1500.0
    assert stats.status.available_balance == 1200.0
    assert stats.status.overall_revenue == 10000.0
    assert stats.status.withdrawal_enabled is True
    assert stats.status.next_withdrawal_at is not None

    call_arg = client.invoke.call_args[0][0]
    assert isinstance(call_arg, raw.functions.payments.GetStarsRevenueStats)
    assert call_arg.dark is True
