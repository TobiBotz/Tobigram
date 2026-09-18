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
from pyrogram import raw

from ..object import Object

# ==========================================
# Background Fills
# ==========================================


class BackgroundFillSolid(Object):
    """The background is filled using the selected color."""

    def __init__(self, *, color: int, client: pyrogram.Client = None):
        super().__init__(client)
        self.color = color

    @staticmethod
    def _parse(client, fill: raw.types.WallPaperSettings) -> BackgroundFillSolid:
        return BackgroundFillSolid(color=fill.background_color, client=client)


class BackgroundFillGradient(Object):
    """The background is a gradient fill."""

    def __init__(
        self,
        *,
        top_color: int,
        bottom_color: int,
        rotation_angle: int,
        client: pyrogram.Client = None,
    ):
        super().__init__(client)
        self.top_color = top_color
        self.bottom_color = bottom_color
        self.rotation_angle = rotation_angle

    @staticmethod
    def _parse(client, fill: raw.types.WallPaperSettings) -> BackgroundFillGradient:
        return BackgroundFillGradient(
            top_color=fill.background_color,
            bottom_color=fill.second_background_color,
            rotation_angle=getattr(fill, "rotation", 0) or 0,
            client=client,
        )


class BackgroundFillFreeformGradient(Object):
    """The background is a freeform gradient that rotates after every message."""

    def __init__(self, *, colors: list[int], client: pyrogram.Client = None):
        super().__init__(client)
        self.colors = colors

    @staticmethod
    def _parse(client, fill: raw.types.WallPaperSettings) -> BackgroundFillFreeformGradient:
        colors = [fill.background_color, fill.second_background_color]
        if fill.third_background_color:
            colors.append(fill.third_background_color)
        if fill.fourth_background_color:
            colors.append(fill.fourth_background_color)
        return BackgroundFillFreeformGradient(colors=colors, client=client)


BackgroundFill = BackgroundFillSolid | BackgroundFillGradient | BackgroundFillFreeformGradient


# ==========================================
# Background Types
# ==========================================


class BackgroundTypeFill(Object):
    """The background is automatically filled based on the selected colors."""

    def __init__(
        self, *, fill: BackgroundFill, dark_theme_dimming: int = 0, client: pyrogram.Client = None
    ):
        super().__init__(client)
        self.fill = fill
        self.dark_theme_dimming = dark_theme_dimming


class BackgroundTypeWallpaper(Object):
    """The background is a PNG or JPEG image."""

    def __init__(
        self,
        *,
        document: pyrogram.types.Document,
        dark_theme_dimming: int = 0,
        is_blurred: bool | None = None,
        is_moving: bool | None = None,
        client: pyrogram.Client = None,
    ):
        super().__init__(client)
        self.document = document
        self.dark_theme_dimming = dark_theme_dimming
        self.is_blurred = is_blurred
        self.is_moving = is_moving


class BackgroundTypePattern(Object):
    """The background is a PNG or TGV pattern."""

    def __init__(
        self,
        *,
        document: pyrogram.types.Document,
        fill: BackgroundFill,
        intensity: int,
        is_inverted: bool | None = None,
        is_moving: bool | None = None,
        client: pyrogram.Client = None,
    ):
        super().__init__(client)
        self.document = document
        self.fill = fill
        self.intensity = intensity
        self.is_inverted = is_inverted
        self.is_moving = is_moving


class BackgroundTypeChatTheme(Object):
    """The background is taken directly from a built-in chat theme."""

    def __init__(self, *, theme_name: str, client: pyrogram.Client = None):
        super().__init__(client)
        self.theme_name = theme_name


BackgroundType = (
    BackgroundTypeFill | BackgroundTypeWallpaper | BackgroundTypePattern | BackgroundTypeChatTheme
)
