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

from .create_ai_tone import CreateAITone
from .get_ai_tones import GetAITones
from .get_ai_tone import GetAITone
from .get_ai_tone_example import GetAIToneExample
from .update_ai_tone import UpdateAITone
from .save_ai_tone import SaveAITone
from .delete_ai_tone import DeleteAITone


class AICompose(
    CreateAITone,
    GetAITones,
    GetAITone,
    GetAIToneExample,
    UpdateAITone,
    SaveAITone,
    DeleteAITone,
):
    pass
