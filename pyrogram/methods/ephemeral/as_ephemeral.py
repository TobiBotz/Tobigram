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

import logging
from typing import Optional

import pyrogram
from pyrogram import raw, types

log = logging.getLogger(__name__)

#: fields a send request can carry that ephemeral.sendMessage has no place for.
#: Bot API allows the combination, so this warns rather than raising, but it does
#: not pass silently — a dropped schedule_date is a message that never arrives.
UNSUPPORTED = (
    "silent",
    "background",
    "clear_draft",
    "schedule_date",
    "schedule_repeat_period",
    "send_as",
    "effect",
    "quick_reply_shortcut",
    "allow_paid_floodskip",
    "allow_paid_stars",
    "suggested_post",
    "update_stickersets_order",
    "no_webpage",
)


async def as_ephemeral(
    client: "pyrogram.Client",
    parameters: Optional["types.EphemeralMessageParameters"],
    request: "raw.core.TLObject"
) -> "raw.core.TLObject":
    """The ephemeral form of a send request, or the request unchanged.

    Bot API 10.3 sends an ephemeral message by adding ephemeral_message_parameters to
    an ordinary send method; MTProto has a separate RPC. Translating the request the
    method already built keeps the thirteen call sites to one line each, and leaves the
    media, reply and markup handling in the method that owns it.

    ``replace_callback_query_message`` maps to ``anchor``: the ephemeral message is
    anchored to the message the callback query came from, which is how the client shows
    one in place of another.
    """

    if parameters is None:
        return request

    dropped = [
        name for name in UNSUPPORTED
        if getattr(request, name, None) not in (None, False)
    ]

    if dropped:
        log.warning(
            "ephemeral.sendMessage has no field for %s, so %s dropped",
            ", ".join(dropped),
            "they were" if len(dropped) > 1 else "it was"
        )

    return raw.functions.ephemeral.SendMessage(
        peer=request.peer,
        receiver_id=await client.resolve_peer(parameters.receiver_user_id),
        query_id=(
            int(parameters.callback_query_id)
            if parameters.callback_query_id is not None
            else None
        ),
        anchor=parameters.replace_callback_query_message or None,
        message=getattr(request, "message", None) or "",
        entities=getattr(request, "entities", None) or None,
        media=getattr(request, "media", None),
        rich_message=getattr(request, "rich_message", None),
        reply_markup=request.reply_markup,
        reply_to=request.reply_to,
        random_id=request.random_id,
        invert_media=getattr(request, "invert_media", None),
        noforwards=getattr(request, "noforwards", None),
    )
