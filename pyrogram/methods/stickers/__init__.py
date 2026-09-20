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

from .add_sticker_to_set import AddStickerToSet
from .change_sticker import ChangeSticker
from .check_sticker_set_name import CheckStickerSetName
from .create_sticker_set import CreateStickerSet
from .delete_sticker_set import DeleteStickerSet
from .get_custom_emoji_stickers import GetCustomEmojiStickers
from .get_my_stickers import GetMyStickers
from .get_sticker_set import GetStickerSet
from .get_stickers import GetStickers
from .remove_sticker_from_set import RemoveStickerFromSet
from .rename_sticker_set import RenameStickerSet
from .replace_sticker import ReplaceSticker
from .save_sticker_set import SaveStickerSet
from .set_sticker_position import SetStickerPosition
from .set_sticker_set_thumb import SetStickerSetThumb
from .suggest_sticker_set_name import SuggestStickerSetName
from .unsave_sticker_set import UnsaveStickerSet


class Stickers(
    AddStickerToSet,
    ChangeSticker,
    CheckStickerSetName,
    CreateStickerSet,
    DeleteStickerSet,
    GetCustomEmojiStickers,
    GetMyStickers,
    GetStickerSet,
    GetStickers,
    RemoveStickerFromSet,
    RenameStickerSet,
    ReplaceSticker,
    SaveStickerSet,
    SetStickerPosition,
    SetStickerSetThumb,
    SuggestStickerSetName,
    UnsaveStickerSet,
):
    pass
