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

from .add_collection_gifts import AddCollectionGifts
from .apply_gift_code import ApplyGiftCode
from .buy_gift_upgrade import BuyGiftUpgrade
from .check_gift_code import CheckGiftCode
from .convert_gift_to_stars import ConvertGiftToStars
from .craft_gift import CraftGift
from .create_gift_collection import CreateGiftCollection
from .delete_gift_collection import DeleteGiftCollection
from .drop_gift_original_details import DropGiftOriginalDetails
from .edit_star_subscription import EditStarSubscription
from .get_available_gifts import GetAvailableGifts
from .get_chat_gifts import GetChatGifts
from .get_chat_gifts_count import GetChatGiftsCount
from .get_gift_auction_state import GetGiftAuctionState
from .get_gift_collections import GetGiftCollections
from .get_gift_upgrade_preview import GetGiftUpgradePreview
from .get_gift_upgrade_variants import GetGiftUpgradeVariants
from .get_gifts_for_crafting import GetGiftsForCrafting
from .get_payment_form import GetPaymentForm
from .get_stars_balance import GetStarsBalance
from .get_stars_revenue_stats import GetStarsRevenueStats
from .get_stars_transactions import GetStarsTransactions
from .get_ton_balance import GetTonBalance
from .get_upgraded_gift import GetUpgradedGift
from .get_upgraded_gift_value_info import GetUpgradedGiftValueInfo
from .gift_premium_with_stars import GiftPremiumWithStars
from .hide_gift import HideGift
from .increase_gift_auction_bid import IncreaseGiftAuctionBid
from .place_gift_auction_bid import PlaceGiftAuctionBid
from .process_gift_purchase_offer import ProcessGiftPurchaseOffer
from .remove_collection_gifts import RemoveCollectionGifts
from .reorder_collection_gifts import ReorderCollectionGifts
from .reorder_gift_collections import ReorderGiftCollections
from .reuse_star_subscription import ReuseStarSubscription
from .search_gifts_for_resale import SearchGiftsForResale
from .send_gift import SendGift
from .send_gift_purchase_offer import SendGiftPurchaseOffer
from .send_payment_form import SendPaymentForm
from .send_resold_gift import SendResoldGift
from .set_gift_collection_name import SetGiftCollectionName
from .set_gift_resale_price import SetGiftResalePrice
from .set_pinned_gifts import SetPinnedGifts
from .show_gift import ShowGift
from .suggest_birthday import SuggestBirthday
from .transfer_gift import TransferGift
from .upgrade_gift import UpgradeGift
from .get_stars_subscriptions import GetStarsSubscriptions
from .get_stars_topup_options import GetStarsTopupOptions
from .get_stars_gift_options import GetStarsGiftOptions
from .get_stars_transactions_by_id import GetStarsTransactionsByID
from .get_stars_revenue_withdrawal_url import GetStarsRevenueWithdrawalUrl
from .get_stars_revenue_ads_account_url import GetStarsRevenueAdsAccountUrl
from .get_saved_star_gift import GetSavedStarGift
from .check_can_send_gift import CheckCanSendGift
from .get_star_gift_withdrawal_url import GetStarGiftWithdrawalUrl
from .get_star_gift_active_auctions import GetStarGiftActiveAuctions
from .get_star_gift_auction_acquired_gifts import GetStarGiftAuctionAcquiredGifts
from .toggle_chat_star_gift_notifications import ToggleChatStarGiftNotifications
from .get_giveaway_info import GetGiveawayInfo
from .get_stars_giveaway_options import GetStarsGiveawayOptions
from .launch_prepaid_giveaway import LaunchPrepaidGiveaway
from .get_premium_gift_code_options import GetPremiumGiftCodeOptions
from .connect_star_ref_bot import ConnectStarRefBot
from .edit_connected_star_ref_bot import EditConnectedStarRefBot
from .get_connected_star_ref_bot import GetConnectedStarRefBot
from .get_connected_star_ref_bots import GetConnectedStarRefBots
from .get_suggested_star_ref_bots import GetSuggestedStarRefBots
from .get_payment_receipt import GetPaymentReceipt
from .get_saved_info import GetSavedInfo
from .clear_saved_info import ClearSavedInfo
from .validate_requested_info import ValidateRequestedInfo
from .get_bank_card_data import GetBankCardData
from .can_purchase_store import CanPurchaseStore
from .assign_app_store_transaction import AssignAppStoreTransaction
from .assign_play_market_transaction import AssignPlayMarketTransaction


class Payments(
    AddCollectionGifts,
    ApplyGiftCode,
    BuyGiftUpgrade,
    CheckGiftCode,
    ConvertGiftToStars,
    CraftGift,
    CreateGiftCollection,
    DeleteGiftCollection,
    DropGiftOriginalDetails,
    EditStarSubscription,
    GetAvailableGifts,
    GetChatGifts,
    GetGiftAuctionState,
    GetChatGiftsCount,
    GetGiftCollections,
    GetGiftUpgradePreview,
    GetGiftUpgradeVariants,
    GetGiftsForCrafting,
    GetPaymentForm,
    GetStarsBalance,
    GetStarsRevenueStats,
    GetStarsTransactions,
    GetTonBalance,
    GetUpgradedGift,
    GetUpgradedGiftValueInfo,
    GiftPremiumWithStars,
    HideGift,
    IncreaseGiftAuctionBid,
    PlaceGiftAuctionBid,
    ProcessGiftPurchaseOffer,
    RemoveCollectionGifts,
    ReorderCollectionGifts,
    ReorderGiftCollections,
    ReuseStarSubscription,
    SearchGiftsForResale,
    SendGiftPurchaseOffer,
    SendGift,
    SendPaymentForm,
    SendResoldGift,
    SetGiftCollectionName,
    SetGiftResalePrice,
    SetPinnedGifts,
    ShowGift,
    SuggestBirthday,
    TransferGift,
    UpgradeGift,
    GetStarsSubscriptions,
    GetStarsTopupOptions,
    GetStarsGiftOptions,
    GetStarsTransactionsByID,
    GetStarsRevenueWithdrawalUrl,
    GetStarsRevenueAdsAccountUrl,
    GetSavedStarGift,
    CheckCanSendGift,
    GetStarGiftWithdrawalUrl,
    GetStarGiftActiveAuctions,
    GetStarGiftAuctionAcquiredGifts,
    ToggleChatStarGiftNotifications,
    GetGiveawayInfo,
    GetStarsGiveawayOptions,
    LaunchPrepaidGiveaway,
    GetPremiumGiftCodeOptions,
    ConnectStarRefBot,
    EditConnectedStarRefBot,
    GetConnectedStarRefBot,
    GetConnectedStarRefBots,
    GetSuggestedStarRefBots,
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
