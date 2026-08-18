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


from typing import Any, List, Optional, Union

Scalar = Union[int, str]
Field = Optional[Union[Scalar, List[Scalar]]]

_FIELDS = ("chat_id", "user_id", "message_id", "inline_message_id")


class Identifier:
    """The set of criteria a listener waits for.

    A ``None`` field is a wildcard. A field may hold a single value or a list of
    values, in which case any of them matches.

    Parameters:
        chat_id (``int`` | ``str`` | List of ``int`` | ``str``, *optional*):
            Chat the awaited update must come from.

        user_id (``int`` | ``str`` | List of ``int`` | ``str``, *optional*):
            User the awaited update must come from.

        message_id (``int`` | List of ``int``, *optional*):
            Message the awaited update must belong to.

        inline_message_id (``str`` | List of ``str``, *optional*):
            Inline message the awaited update must belong to.
    """

    __slots__ = _FIELDS

    def __init__(
        self,
        chat_id: Field = None,
        user_id: Field = None,
        message_id: Optional[Union[int, List[int]]] = None,
        inline_message_id: Optional[Union[str, List[str]]] = None,
    ):
        self.chat_id = chat_id
        self.user_id = user_id
        self.message_id = message_id
        self.inline_message_id = inline_message_id

    def matches(self, data: "Identifier") -> bool:
        for field in _FIELDS:
            pattern = getattr(self, field)

            if pattern is None:
                continue

            value = getattr(data, field)

            if isinstance(value, list):
                if isinstance(pattern, list):
                    if not set(value).intersection(pattern):
                        return False
                elif pattern not in value:
                    return False
            elif isinstance(pattern, list):
                if value not in pattern:
                    return False
            elif value != pattern:
                return False

        return True

    def count_populated(self) -> int:
        return sum(getattr(self, field) is not None for field in _FIELDS)

    def __repr__(self) -> str:
        return "pyrogram.types.Identifier({})".format(
            ", ".join(
                f"{field}={getattr(self, field)!r}"
                for field in _FIELDS
                if getattr(self, field) is not None
            )
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Identifier):
            return NotImplemented

        return all(
            getattr(self, field) == getattr(other, field) for field in _FIELDS
        )
