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

from .create_business_chat_link import CreateBusinessChatLink
from .delete_business_chat_link import DeleteBusinessChatLink
from .delete_business_messages import DeleteBusinessMessages
from .get_business_account_gifts import GetBusinessAccountGifts
from .get_business_account_star_balance import GetBusinessAccountStarBalance
from .get_business_chat_links import GetBusinessChatLinks
from .get_business_connection import GetBusinessConnection
from .get_connected_bots import GetConnectedBots
from .read_business_message import ReadBusinessMessage
from .remove_business_account_profile_photo import RemoveBusinessAccountProfilePhoto
from .resolve_business_chat_link import ResolveBusinessChatLink
from .set_business_account_bio import SetBusinessAccountBio
from .set_business_account_gift_settings import SetBusinessAccountGiftSettings
from .set_business_account_name import SetBusinessAccountName
from .set_business_account_profile_photo import SetBusinessAccountProfilePhoto
from .set_business_account_username import SetBusinessAccountUsername
from .transfer_business_account_stars import TransferBusinessAccountStars
from .update_business_away_message import UpdateBusinessAwayMessage
from .update_business_greeting_message import UpdateBusinessGreetingMessage
from .update_business_intro import UpdateBusinessIntro
from .update_business_location import UpdateBusinessLocation
from .update_business_work_hours import UpdateBusinessWorkHours


class Business(
    CreateBusinessChatLink,
    DeleteBusinessChatLink,
    DeleteBusinessMessages,
    GetBusinessAccountGifts,
    GetBusinessAccountStarBalance,
    GetBusinessChatLinks,
    GetBusinessConnection,
    GetConnectedBots,
    ReadBusinessMessage,
    RemoveBusinessAccountProfilePhoto,
    ResolveBusinessChatLink,
    SetBusinessAccountBio,
    SetBusinessAccountGiftSettings,
    SetBusinessAccountName,
    SetBusinessAccountProfilePhoto,
    SetBusinessAccountUsername,
    TransferBusinessAccountStars,
    UpdateBusinessAwayMessage,
    UpdateBusinessGreetingMessage,
    UpdateBusinessIntro,
    UpdateBusinessLocation,
    UpdateBusinessWorkHours,
):
    pass
