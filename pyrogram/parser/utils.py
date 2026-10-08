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

import re
from struct import unpack

# SMP = Supplementary Multilingual Plane: https://en.wikipedia.org/wiki/Plane_(Unicode)#Overview
SMP_RE = re.compile(r"[\U00010000-\U0010FFFF]")


def add_surrogates(text):
    # Replace each SMP code point with a surrogate pair
    return SMP_RE.sub(
        lambda match: (  # Split SMP in two surrogates
            "".join(chr(i) for i in unpack("<HH", match.group().encode("utf-16le")))
        ),
        text,
    )


def remove_surrogates(text):
    # Replace each surrogate pair with a SMP code point
    return text.encode("utf-16", "surrogatepass").decode("utf-16")


def _is_high_surrogate(char: str) -> bool:
    return 0xD800 <= ord(char) <= 0xDBFF


def _is_low_surrogate(char: str) -> bool:
    return 0xDC00 <= ord(char) <= 0xDFFF


def clamp_to_code_point(text: str, offset: int, *, start: bool) -> int:
    """Widen *offset* so it never splits a surrogate pair.

    :func:`add_surrogates` turns every code point outside the Basic Multilingual
    Plane into a high surrogate followed by a low surrogate.  An entity offset
    that lands between those two would tear an emoji in half when a tag is
    inserted there, and :func:`remove_surrogates` would then raise a
    ``UnicodeDecodeError``.  Match the behaviour of the ``Str`` type, which
    widens outward to the whole code point: a start offset moves left, an end
    offset moves right.
    """
    while 0 < offset < len(text):
        if _is_high_surrogate(text[offset - 1]) and _is_low_surrogate(text[offset]):
            offset += -1 if start else 1
        else:
            break

    return offset


def split_crossing_spans(text: str, entities: list):
    def sort_key(span):
        return span[0], -span[1]

    spans = [
        (
            clamp_to_code_point(text, e.offset, start=True),
            clamp_to_code_point(text, e.offset + e.length, start=False),
            e,
        )
        for e in entities
    ]

    spans.sort(key=sort_key)

    crossing = True

    while crossing:
        crossing = False

        for a_start, a_end, _ in spans:
            for k, (b_start, b_end, b_entity) in enumerate(spans):
                if a_start < b_start < a_end < b_end:
                    spans[k : k + 1] = [(b_start, a_end, b_entity), (a_end, b_end, b_entity)]
                    spans.sort(key=sort_key)
                    crossing = True
                    break

            if crossing:
                break

    return spans


def replace_once(source: str, old: str, new: str, start: int):
    return source[:start] + source[start:].replace(old, new, 1)
