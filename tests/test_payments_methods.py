import pytest

import pyrogram
from pyrogram import raw, types


class _Recorder:
    def __init__(self, result=True):
        self.calls = []
        self.result = result

    async def invoke(self, query, *args, **kwargs):
        self.calls.append(query)
        return self.result

    async def resolve_peer(self, peer_id):
        if peer_id == "me" or peer_id == 111:
            return raw.types.InputPeerSelf()
        return raw.types.InputPeerChannel(
            channel_id=int(peer_id) if isinstance(peer_id, int) else 999,
            access_hash=123,
        )

    async def check_password(self, password):
        return raw.types.InputCheckPasswordEmpty()


@pytest.mark.asyncio
async def test_get_stars_subscriptions_dispatches_query():
    from pyrogram.methods.payments.get_stars_subscriptions import GetStarsSubscriptions

    class _Client(_Recorder, GetStarsSubscriptions):
        pass

    client = _Client()
    await client.get_stars_subscriptions("me", offset="abc", missing_balance=True)

    call = client.calls[0]
    assert isinstance(call, raw.functions.payments.GetStarsSubscriptions)
    assert call.offset == "abc"
    assert call.missing_balance is True


@pytest.mark.asyncio
async def test_get_stars_topup_options_dispatches_query():
    from pyrogram.methods.payments.get_stars_topup_options import GetStarsTopupOptions

    class _Client(_Recorder, GetStarsTopupOptions):
        pass

    client = _Client(result=[])
    await client.get_stars_topup_options()
    assert isinstance(client.calls[0], raw.functions.payments.GetStarsTopupOptions)


@pytest.mark.asyncio
async def test_get_stars_gift_options_dispatches_query():
    from pyrogram.methods.payments.get_stars_gift_options import GetStarsGiftOptions

    class _Client(_Recorder, GetStarsGiftOptions):
        pass

    client = _Client(result=[])
    await client.get_stars_gift_options(123)
    call = client.calls[0]
    assert isinstance(call, raw.functions.payments.GetStarsGiftOptions)


@pytest.mark.asyncio
async def test_get_stars_transactions_by_id_dispatches_query():
    from pyrogram.methods.payments.get_stars_transactions_by_id import GetStarsTransactionsByID

    class _Client(_Recorder, GetStarsTransactionsByID):
        pass

    client = _Client()
    tx_id = raw.types.InputStarsTransaction(id="tx_123")
    await client.get_stars_transactions_by_id("me", [tx_id], ton=True)

    call = client.calls[0]
    assert isinstance(call, raw.functions.payments.GetStarsTransactionsByID)
    assert call.ton is True
    assert call.id == [tx_id]


@pytest.mark.asyncio
async def test_get_stars_revenue_withdrawal_url_dispatches_query():
    from pyrogram.methods.payments.get_stars_revenue_withdrawal_url import (
        GetStarsRevenueWithdrawalUrl,
    )

    class _Client(_Recorder, GetStarsRevenueWithdrawalUrl):
        pass

    client = _Client(
        result=raw.types.payments.StarsRevenueWithdrawalUrl(url="https://fragment.com/withdraw")
    )
    res = await client.get_stars_revenue_withdrawal_url(123, "password", ton=True, amount=1000)

    assert isinstance(res, raw.types.payments.StarsRevenueWithdrawalUrl)
    call = client.calls[0]
    assert isinstance(call, raw.functions.payments.GetStarsRevenueWithdrawalUrl)
    assert call.ton is True
    assert call.amount == 1000


@pytest.mark.asyncio
async def test_get_stars_revenue_ads_account_url_dispatches_query():
    from pyrogram.methods.payments.get_stars_revenue_ads_account_url import (
        GetStarsRevenueAdsAccountUrl,
    )

    class _Client(_Recorder, GetStarsRevenueAdsAccountUrl):
        pass

    client = _Client(
        result=raw.types.payments.StarsRevenueAdsAccountUrl(url="https://ads.telegram.org")
    )
    url = await client.get_stars_revenue_ads_account_url(123)

    assert url == "https://ads.telegram.org"
    call = client.calls[0]
    assert isinstance(call, raw.functions.payments.GetStarsRevenueAdsAccountUrl)


@pytest.mark.asyncio
async def test_get_saved_star_gift_dispatches_query():
    from pyrogram.methods.payments.get_saved_star_gift import GetSavedStarGift

    class _Client(_Recorder, GetSavedStarGift):
        pass

    client = _Client()
    gift = raw.types.InputSavedStarGiftUser(msg_id=42)
    await client.get_saved_star_gift(gift)

    call = client.calls[0]
    assert isinstance(call, raw.functions.payments.GetSavedStarGift)
    assert call.stargift == [gift]


@pytest.mark.asyncio
async def test_check_can_send_gift_dispatches_query():
    from pyrogram.methods.payments.check_can_send_gift import CheckCanSendGift

    class _Client(_Recorder, CheckCanSendGift):
        pass

    client = _Client()
    await client.check_can_send_gift(999)
    call = client.calls[0]
    assert isinstance(call, raw.functions.payments.CheckCanSendGift)
    assert call.gift_id == 999


@pytest.mark.asyncio
async def test_get_star_gift_withdrawal_url_dispatches_query():
    from pyrogram.methods.payments.get_star_gift_withdrawal_url import GetStarGiftWithdrawalUrl

    class _Client(_Recorder, GetStarGiftWithdrawalUrl):
        pass

    client = _Client(
        result=raw.types.payments.StarGiftWithdrawalUrl(url="https://fragment.com/gift")
    )
    stargift = raw.types.InputSavedStarGiftUser(msg_id=77)
    url = await client.get_star_gift_withdrawal_url(stargift, "password")

    assert url == "https://fragment.com/gift"
    call = client.calls[0]
    assert isinstance(call, raw.functions.payments.GetStarGiftWithdrawalUrl)


@pytest.mark.asyncio
async def test_get_star_gift_active_auctions_dispatches_query():
    from pyrogram.methods.payments.get_star_gift_active_auctions import GetStarGiftActiveAuctions

    class _Client(_Recorder, GetStarGiftActiveAuctions):
        pass

    client = _Client()
    await client.get_star_gift_active_auctions(hash=123)
    call = client.calls[0]
    assert isinstance(call, raw.functions.payments.GetStarGiftActiveAuctions)
    assert call.hash == 123


@pytest.mark.asyncio
async def test_get_star_gift_auction_acquired_gifts_dispatches_query():
    from pyrogram.methods.payments.get_star_gift_auction_acquired_gifts import (
        GetStarGiftAuctionAcquiredGifts,
    )

    class _Client(_Recorder, GetStarGiftAuctionAcquiredGifts):
        pass

    client = _Client()
    await client.get_star_gift_auction_acquired_gifts(456)
    call = client.calls[0]
    assert isinstance(call, raw.functions.payments.GetStarGiftAuctionAcquiredGifts)
    assert call.gift_id == 456


@pytest.mark.asyncio
async def test_toggle_chat_star_gift_notifications_dispatches_query():
    from pyrogram.methods.payments.toggle_chat_star_gift_notifications import (
        ToggleChatStarGiftNotifications,
    )

    class _Client(_Recorder, ToggleChatStarGiftNotifications):
        pass

    client = _Client()
    await client.toggle_chat_star_gift_notifications(123, enabled=True)
    call = client.calls[0]
    assert isinstance(call, raw.functions.payments.ToggleChatStarGiftNotifications)
    assert call.enabled is True


@pytest.mark.asyncio
async def test_get_giveaway_info_dispatches_query():
    from pyrogram.methods.payments.get_giveaway_info import GetGiveawayInfo

    class _Client(_Recorder, GetGiveawayInfo):
        pass

    client = _Client()
    await client.get_giveaway_info(123, 777)
    call = client.calls[0]
    assert isinstance(call, raw.functions.payments.GetGiveawayInfo)
    assert call.msg_id == 777


@pytest.mark.asyncio
async def test_get_stars_giveaway_options_dispatches_query():
    from pyrogram.methods.payments.get_stars_giveaway_options import GetStarsGiveawayOptions

    class _Client(_Recorder, GetStarsGiveawayOptions):
        pass

    client = _Client(result=[])
    await client.get_stars_giveaway_options()
    assert isinstance(client.calls[0], raw.functions.payments.GetStarsGiveawayOptions)


@pytest.mark.asyncio
async def test_launch_prepaid_giveaway_dispatches_query():
    from pyrogram.methods.payments.launch_prepaid_giveaway import LaunchPrepaidGiveaway

    class _Client(_Recorder, LaunchPrepaidGiveaway):
        pass

    client = _Client()
    purpose = raw.types.InputStorePaymentPremiumGiveaway(
        only_new_subscribers=True,
        winners_are_visible=True,
        boost_peer=raw.types.InputPeerSelf(),
        additional_peers=[],
        countries_iso2=[],
        prize_description="",
        random_id=1,
        until_date=1700000000,
        currency="USD",
        amount=1000,
    )
    await client.launch_prepaid_giveaway(123, giveaway_id=888, purpose=purpose)

    call = client.calls[0]
    assert isinstance(call, raw.functions.payments.LaunchPrepaidGiveaway)
    assert call.giveaway_id == 888


@pytest.mark.asyncio
async def test_get_premium_gift_code_options_dispatches_query():
    from pyrogram.methods.payments.get_premium_gift_code_options import GetPremiumGiftCodeOptions

    class _Client(_Recorder, GetPremiumGiftCodeOptions):
        pass

    client = _Client(result=[])
    await client.get_premium_gift_code_options(123)
    call = client.calls[0]
    assert isinstance(call, raw.functions.payments.GetPremiumGiftCodeOptions)


@pytest.mark.asyncio
async def test_star_referral_bot_methods():
    from pyrogram.methods.payments.connect_star_ref_bot import ConnectStarRefBot
    from pyrogram.methods.payments.edit_connected_star_ref_bot import EditConnectedStarRefBot
    from pyrogram.methods.payments.get_connected_star_ref_bot import GetConnectedStarRefBot
    from pyrogram.methods.payments.get_connected_star_ref_bots import GetConnectedStarRefBots
    from pyrogram.methods.payments.get_suggested_star_ref_bots import GetSuggestedStarRefBots

    class _Client(
        _Recorder,
        ConnectStarRefBot,
        EditConnectedStarRefBot,
        GetConnectedStarRefBot,
        GetConnectedStarRefBots,
        GetSuggestedStarRefBots,
    ):
        pass

    client = _Client()
    await client.connect_star_ref_bot(123, 456)
    assert isinstance(client.calls[0], raw.functions.payments.ConnectStarRefBot)

    await client.edit_connected_star_ref_bot(123, "https://t.me/ref", revoked=True)
    assert isinstance(client.calls[1], raw.functions.payments.EditConnectedStarRefBot)
    assert client.calls[1].revoked is True

    await client.get_connected_star_ref_bot(123, 456)
    assert isinstance(client.calls[2], raw.functions.payments.GetConnectedStarRefBot)

    await client.get_connected_star_ref_bots(123, limit=50)
    assert isinstance(client.calls[3], raw.functions.payments.GetConnectedStarRefBots)
    assert client.calls[3].limit == 50

    await client.get_suggested_star_ref_bots(123, limit=30, order_by_revenue=True)
    assert isinstance(client.calls[4], raw.functions.payments.GetSuggestedStarRefBots)
    assert client.calls[4].order_by_revenue is True


@pytest.mark.asyncio
async def test_invoice_and_store_methods():
    from pyrogram.methods.payments.get_payment_receipt import GetPaymentReceipt
    from pyrogram.methods.payments.get_saved_info import GetSavedInfo
    from pyrogram.methods.payments.clear_saved_info import ClearSavedInfo
    from pyrogram.methods.payments.validate_requested_info import ValidateRequestedInfo
    from pyrogram.methods.payments.get_bank_card_data import GetBankCardData
    from pyrogram.methods.payments.can_purchase_store import CanPurchaseStore
    from pyrogram.methods.payments.assign_app_store_transaction import AssignAppStoreTransaction
    from pyrogram.methods.payments.assign_play_market_transaction import AssignPlayMarketTransaction

    class _Client(
        _Recorder,
        GetPaymentReceipt,
        GetSavedInfo,
        ClearSavedInfo,
        ValidateRequestedInfo,
        GetBankCardData,
        CanPurchaseStore,
        AssignAppStoreTransaction,
        AssignPlayMarketTransaction,
    ):
        pass

    client = _Client()
    await client.get_payment_receipt(123, 456)
    assert isinstance(client.calls[0], raw.functions.payments.GetPaymentReceipt)

    await client.get_saved_info()
    assert isinstance(client.calls[1], raw.functions.payments.GetSavedInfo)

    await client.clear_saved_info(credentials=True, info=True)
    assert isinstance(client.calls[2], raw.functions.payments.ClearSavedInfo)

    inv = raw.types.InputInvoiceMessage(peer=raw.types.InputPeerSelf(), msg_id=1)
    req_info = raw.types.PaymentRequestedInfo()
    await client.validate_requested_info(inv, req_info, save=True)
    assert isinstance(client.calls[3], raw.functions.payments.ValidateRequestedInfo)

    await client.get_bank_card_data("424242")
    assert isinstance(client.calls[4], raw.functions.payments.GetBankCardData)

    purpose = raw.types.InputStorePaymentStarsTopup(stars=100, currency="USD", amount=100)
    await client.can_purchase_store(purpose)
    assert isinstance(client.calls[5], raw.functions.payments.CanPurchaseStore)

    await client.assign_app_store_transaction(b"receipt", purpose)
    assert isinstance(client.calls[6], raw.functions.payments.AssignAppStoreTransaction)

    await client.assign_play_market_transaction("json_receipt", purpose)
    assert isinstance(client.calls[7], raw.functions.payments.AssignPlayMarketTransaction)
