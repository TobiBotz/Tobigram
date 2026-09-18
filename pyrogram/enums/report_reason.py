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
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>

from __future__ import annotations

from enum import auto

from .auto_name import AutoName


class ReportReason(AutoName):
    """Report reason enumeration used in report methods."""

    SPAM = auto()
    "Spam, unsolicited advertisements, or scams"

    VIOLENCE = auto()
    "Violence, physical harm, or illegal threats"

    PORNOGRAPHY = auto()
    "Pornography or adult content"

    CHILD_ABUSE = auto()
    "Child abuse or child sexual exploitation"

    COPYRIGHT = auto()
    "Copyright or intellectual property infringement"

    GEO_IRRELEVANT = auto()
    "Geographically irrelevant content"

    FAKE = auto()
    "Fake account, impersonation, or fraud"

    ILLEGAL_DRUGS = auto()
    "Illegal drugs or prohibited substances"

    PERSONAL_DETAILS = auto()
    "Personal details, private data leaks, or doxxing"

    OTHER = auto()
    "Other reasons with custom message"
