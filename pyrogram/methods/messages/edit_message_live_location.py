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

import pyrogram
from pyrogram import raw, types, utils


class EditMessageLiveLocation:
    async def edit_message_live_location(
        self: pyrogram.Client,
        chat_id: int | str | None = None,
        message_id: int | None = None,
        inline_message_id: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        live_period: int | None = None,
        horizontal_accuracy: float | None = None,
        heading: int | None = None,
        proximity_alert_radius: int | None = None,
        reply_markup: types.InlineKeyboardMarkup | None = None,
        business_connection_id: str | None = None,
    ) -> types.Message | bool:
        """Edit a live location message.

        A location can be edited until its ``live_period`` expires or editing is explicitly
        disabled by a call to :meth:`~Client.stop_message_live_location`.

        Either ``chat_id`` + ``message_id`` **or** ``inline_message_id`` must be provided.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``, *optional*):
                Identifier of the message to edit.

            inline_message_id (``str``, *optional*):
                Identifier of the inline message. Required when editing an inline live location.

            latitude (``float``, *optional*):
                New latitude of the location.

            longitude (``float``, *optional*):
                New longitude of the location.

            live_period (``int``, *optional*):
                New period in seconds during which the location can be updated, should be between
                60 and 86400, or 0x7FFFFFFF for live locations that can be edited indefinitely.

            horizontal_accuracy (``float``, *optional*):
                The radius of uncertainty for the location, measured in metres; 0-1500.

            heading (``int``, *optional*):
                Direction in which the user is moving, in degrees; 1-360.

            proximity_alert_radius (``int``, *optional*):
                The maximum distance for proximity alerts about approaching another chat member,
                in metres; 1-100000.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection.

        Returns:
            :obj:`~pyrogram.types.Message` | ``bool``: On success, the edited Message is returned.
            For inline messages, True is returned.

        Example:
            .. code-block:: python

                # Update a live location message
                await app.edit_message_live_location(chat_id, message_id, latitude=37.7, longitude=-122.4)
        """
        if inline_message_id is None:
            peer = await self.resolve_peer(chat_id)
            r = await self.invoke(
                raw.functions.messages.EditMessage(
                    peer=peer,
                    id=message_id,
                    media=raw.types.InputMediaGeoLive(
                        geo_point=raw.types.InputGeoPoint(
                            lat=latitude,
                            long=longitude,
                            accuracy_radius=int(horizontal_accuracy * 10)
                            if horizontal_accuracy is not None
                            else None,
                        )
                        if latitude is not None and longitude is not None
                        else raw.types.InputGeoPointEmpty(),
                        stopped=False,
                        heading=heading,
                        period=live_period,
                        proximity_notification_radius=proximity_alert_radius,
                    ),
                    reply_markup=await reply_markup.write(self) if reply_markup else None,
                ),
                business_connection_id=business_connection_id,
            )

            users = {i.id: i for i in r.users}
            chats = {i.id: i for i in r.chats}

            for i in r.updates:
                if isinstance(i, (raw.types.UpdateEditMessage, raw.types.UpdateEditChannelMessage)):
                    return await types.Message._parse(self, i.message, users, chats)

            return True
        else:
            await self.invoke(
                raw.functions.messages.EditInlineBotMessage(
                    id=utils.decode_inline_message_id(inline_message_id),
                    media=raw.types.InputMediaGeoLive(
                        geo_point=raw.types.InputGeoPoint(
                            lat=latitude,
                            long=longitude,
                            accuracy_radius=int(horizontal_accuracy * 10)
                            if horizontal_accuracy is not None
                            else None,
                        )
                        if latitude is not None and longitude is not None
                        else raw.types.InputGeoPointEmpty(),
                        stopped=False,
                        heading=heading,
                        period=live_period,
                        proximity_notification_radius=proximity_alert_radius,
                    ),
                    reply_markup=await reply_markup.write(self) if reply_markup else None,
                )
            )
            return True
