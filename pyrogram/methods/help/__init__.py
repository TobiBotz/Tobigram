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

from .dismiss_suggestion import DismissSuggestion
from .edit_user_info import EditUserInfo
from .get_app_config import GetAppConfig
from .get_app_update import GetAppUpdate
from .get_cdn_config import GetCdnConfig
from .get_countries_list import GetCountriesList
from .get_deep_link_info import GetDeepLinkInfo
from .get_invite_text import GetInviteText
from .get_nearest_dc import GetNearestDc
from .get_passport_config import GetPassportConfig
from .get_peer_colors import GetPeerColors
from .get_peer_profile_colors import GetPeerProfileColors
from .get_premium_promo import GetPremiumPromo
from .get_promo_data import GetPromoData
from .get_recent_me_urls import GetRecentMeUrls
from .get_support import GetSupport
from .get_support_name import GetSupportName
from .get_terms_of_service_update import GetTermsOfServiceUpdate
from .get_timezones_list import GetTimezonesList
from .get_user_info import GetUserInfo
from .hide_promo_data import HidePromoData
from .save_app_log import SaveAppLog
from .set_bot_updates_status import SetBotUpdatesStatus


class Help(
    DismissSuggestion,
    EditUserInfo,
    GetAppConfig,
    GetAppUpdate,
    GetCdnConfig,
    GetCountriesList,
    GetDeepLinkInfo,
    GetInviteText,
    GetNearestDc,
    GetPassportConfig,
    GetPeerColors,
    GetPeerProfileColors,
    GetPremiumPromo,
    GetPromoData,
    GetRecentMeUrls,
    GetSupport,
    GetSupportName,
    GetTermsOfServiceUpdate,
    GetTimezonesList,
    GetUserInfo,
    HidePromoData,
    SaveAppLog,
    SetBotUpdatesStatus,
):
    pass
