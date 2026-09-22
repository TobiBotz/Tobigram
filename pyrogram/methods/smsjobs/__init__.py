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

from .finish_sms_job import FinishSmsJob
from .get_sms_job import GetSmsJob
from .get_sms_jobs_status import GetSmsJobsStatus
from .is_eligible_to_join_sms_jobs import IsEligibleToJoinSmsJobs
from .join_sms_jobs import JoinSmsJobs
from .leave_sms_jobs import LeaveSmsJobs
from .update_sms_jobs_settings import UpdateSmsJobsSettings


class Smsjobs(
    FinishSmsJob,
    GetSmsJob,
    GetSmsJobsStatus,
    IsEligibleToJoinSmsJobs,
    JoinSmsJobs,
    LeaveSmsJobs,
    UpdateSmsJobsSettings,
):
    pass
