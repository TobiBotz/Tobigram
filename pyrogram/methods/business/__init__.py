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

from .delete_business_messages import DeleteBusinessMessages
from .get_business_account_gifts import GetBusinessAccountGifts
from .get_business_account_star_balance import GetBusinessAccountStarBalance
from .get_business_connection import GetBusinessConnection
from .transfer_business_account_stars import TransferBusinessAccountStars
from .update_business_work_hours import UpdateBusinessWorkHours
from .update_business_location import UpdateBusinessLocation
from .update_business_greeting_message import UpdateBusinessGreetingMessage
from .update_business_away_message import UpdateBusinessAwayMessage
from .update_business_intro import UpdateBusinessIntro
from .create_business_chat_link import CreateBusinessChatLink
from .delete_business_chat_link import DeleteBusinessChatLink
from .resolve_business_chat_link import ResolveBusinessChatLink
from .get_business_chat_links import GetBusinessChatLinks
from .get_connected_bots import GetConnectedBots


class Business(
    DeleteBusinessMessages,
    GetBusinessAccountGifts,
    GetBusinessAccountStarBalance,
    GetBusinessConnection,
    TransferBusinessAccountStars,
    UpdateBusinessWorkHours,
    UpdateBusinessLocation,
    UpdateBusinessGreetingMessage,
    UpdateBusinessAwayMessage,
    UpdateBusinessIntro,
    CreateBusinessChatLink,
    DeleteBusinessChatLink,
    ResolveBusinessChatLink,
    GetBusinessChatLinks,
    GetConnectedBots,
):
    pass

