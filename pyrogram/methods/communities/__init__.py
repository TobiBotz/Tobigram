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

from .create_community import CreateCommunity
from .get_joined_communities import GetJoinedCommunities
from .get_participant_joined_community_chats import GetParticipantJoinedCommunityChats
from .get_community_link_requests import GetCommunityLinkRequests
from .toggle_all_community_link_requests import ToggleAllCommunityLinkRequests
from .collapse_community import CollapseCommunity
from .ban_community_participant import BanCommunityParticipant
from .toggle_community_chat_link import ToggleCommunityChatLink
from .approve_community_link_request import ApproveCommunityLinkRequest


class Communities(
    CreateCommunity,
    GetJoinedCommunities,
    GetParticipantJoinedCommunityChats,
    GetCommunityLinkRequests,
    ToggleAllCommunityLinkRequests,
    CollapseCommunity,
    BanCommunityParticipant,
    ToggleCommunityChatLink,
    ApproveCommunityLinkRequest,
):
    pass
