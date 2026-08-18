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


from .ask import Ask
from .listen import Listen
from .register_next_step_handler import RegisterNextStepHandler
from .stop_listening import StopListening
from .wait_for_callback_query import WaitForCallbackQuery
from .wait_for_message import WaitForMessage


class Listeners(
    Ask,
    Listen,
    RegisterNextStepHandler,
    StopListening,
    WaitForCallbackQuery,
    WaitForMessage,
):
    pass
