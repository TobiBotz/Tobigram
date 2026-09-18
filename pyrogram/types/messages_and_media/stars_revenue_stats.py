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


class StarsRevenueStatus(Object):
    """Contains information about Telegram Stars revenue and withdrawal status.

    Parameters:
        current_balance (``float``):
            Current total Stars balance.

        available_balance (``float``):
            Stars balance currently available for withdrawal.

        overall_revenue (``float``):
            Total all-time revenue earned in Stars.

        withdrawal_enabled (``bool``, *optional*):
            True, if withdrawals via Fragment/TON are enabled.

        next_withdrawal_at (:py:obj:`~datetime.datetime`, *optional*):
            Date and time when the next withdrawal will become available.

        raw_current_balance (:obj:`~pyrogram.types.StarAmount`, *optional*):
            Raw StarAmount object for current balance.

        raw_available_balance (:obj:`~pyrogram.types.StarAmount`, *optional*):
            Raw StarAmount object for available balance.

        raw_overall_revenue (:obj:`~pyrogram.types.StarAmount`, *optional*):
            Raw StarAmount object for overall revenue.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        current_balance: float,
        available_balance: float,
        overall_revenue: float,
        withdrawal_enabled: bool = False,
        next_withdrawal_at: datetime | None = None,
        raw_current_balance: types.StarAmount | None = None,
        raw_available_balance: types.StarAmount | None = None,
        raw_overall_revenue: types.StarAmount | None = None,
    ):
        super().__init__(client)

        self.current_balance = current_balance
        self.available_balance = available_balance
        self.overall_revenue = overall_revenue
        self.withdrawal_enabled = withdrawal_enabled
        self.next_withdrawal_at = next_withdrawal_at
        self.raw_current_balance = raw_current_balance
        self.raw_available_balance = raw_available_balance
        self.raw_overall_revenue = raw_overall_revenue

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        status: raw.types.StarsRevenueStatus,
    ) -> StarsRevenueStatus:
        def calc_stars(amount_obj: raw.types.StarsAmount | None) -> float:
            if amount_obj is None:
                return 0.0
            return amount_obj.amount + (getattr(amount_obj, "nanos", 0) or 0) / 1e9

        return StarsRevenueStatus(
            client=client,
            current_balance=calc_stars(status.current_balance),
            available_balance=calc_stars(status.available_balance),
            overall_revenue=calc_stars(status.overall_revenue),
            withdrawal_enabled=getattr(status, "withdrawal_enabled", False) or False,
            next_withdrawal_at=utils.timestamp_to_datetime(
                getattr(status, "next_withdrawal_at", None)
            ),
            raw_current_balance=types.StarAmount._parse(status.current_balance),
            raw_available_balance=types.StarAmount._parse(status.available_balance),
            raw_overall_revenue=types.StarAmount._parse(status.overall_revenue),
        )


class StarsRevenueStats(Object):
    """Contains monetization statistics and revenue graphs for a channel or bot.

    Parameters:
        status (:obj:`~pyrogram.types.StarsRevenueStatus`):
            Current revenue and withdrawal status.

        usd_rate (``float``):
            Current real-world conversion rate of 1 Telegram Star in USD.

        revenue_graph (:obj:`~pyrogram.raw.base.StatsGraph`):
            Graph containing revenue data over time.

        top_hours_graph (:obj:`~pyrogram.raw.base.StatsGraph`, *optional*):
            Graph containing revenue data by hour of day.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        status: StarsRevenueStatus,
        usd_rate: float,
        revenue_graph: raw.base.StatsGraph,
        top_hours_graph: raw.base.StatsGraph | None = None,
    ):
        super().__init__(client)

        self.status = status
        self.usd_rate = usd_rate
        self.revenue_graph = revenue_graph
        self.top_hours_graph = top_hours_graph

    @staticmethod
    def _parse(
        client: pyrogram.Client,
        stats: raw.types.payments.StarsRevenueStats,
    ) -> StarsRevenueStats:
        return StarsRevenueStats(
            client=client,
            status=StarsRevenueStatus._parse(client, stats.status),
            usd_rate=stats.usd_rate,
            revenue_graph=stats.revenue_graph,
            top_hours_graph=getattr(stats, "top_hours_graph", None),
        )
