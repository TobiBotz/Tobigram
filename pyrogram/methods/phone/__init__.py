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

from .accept_call import AcceptCall
from .change_call_volume import ChangeCallVolume
from .check_group_call import CheckGroupCall
from .confirm_call import ConfirmCall
from .create_conference_call import CreateConferenceCall
from .create_group_call import CreateGroupCall
from .decline_conference_call_invite import DeclineConferenceCallInvite
from .delete_conference_call_participants import DeleteConferenceCallParticipants
from .delete_group_call_messages import DeleteGroupCallMessages
from .delete_group_call_participant_messages import DeleteGroupCallParticipantMessages
from .discard_call import DiscardCall
from .discard_group_call import DiscardGroupCall
from .edit_group_call_participant import EditGroupCallParticipant
from .edit_group_call_title import EditGroupCallTitle
from .export_group_call_invite import ExportGroupCallInvite
from .get_call_config import GetCallConfig
from .get_call_members import GetCallMembers
from .get_group_call import GetGroupCall
from .get_group_call_chain_blocks import GetGroupCallChainBlocks
from .get_group_call_join_as import GetGroupCallJoinAs
from .get_group_call_stars import GetGroupCallStars
from .get_group_call_stream_channels import GetGroupCallStreamChannels
from .get_group_call_stream_rtmp_url import GetGroupCallStreamRtmpUrl
from .invite_conference_call_participant import InviteConferenceCallParticipant
from .invite_to_group_call import InviteToGroupCall
from .join_group_call import JoinGroupCall
from .join_group_call_presentation import JoinGroupCallPresentation
from .leave_group_call import LeaveGroupCall
from .leave_group_call_presentation import LeaveGroupCallPresentation
from .pause_stream import PauseStream
from .play_audio import PlayAudio
from .play_video import PlayVideo
from .received_call import ReceivedCall
from .request_call import RequestCall
from .resume_stream import ResumeStream
from .save_call_debug import SaveCallDebug
from .save_call_log import SaveCallLog
from .save_default_group_call_join_as import SaveDefaultGroupCallJoinAs
from .save_default_send_as import SaveDefaultSendAs
from .send_conference_call_broadcast import SendConferenceCallBroadcast
from .send_group_call_encrypted_message import SendGroupCallEncryptedMessage
from .send_group_call_message import SendGroupCallMessage
from .send_signaling_data import SendSignalingData
from .set_call_rating import SetCallRating
from .start_scheduled_group_call import StartScheduledGroupCall
from .toggle_group_call_record import ToggleGroupCallRecord
from .toggle_group_call_settings import ToggleGroupCallSettings
from .toggle_group_call_start_subscription import ToggleGroupCallStartSubscription


class Phone(
    AcceptCall,
    ChangeCallVolume,
    CheckGroupCall,
    ConfirmCall,
    CreateConferenceCall,
    CreateGroupCall,
    DeclineConferenceCallInvite,
    DeleteConferenceCallParticipants,
    DeleteGroupCallMessages,
    DeleteGroupCallParticipantMessages,
    DiscardCall,
    DiscardGroupCall,
    EditGroupCallParticipant,
    EditGroupCallTitle,
    ExportGroupCallInvite,
    GetCallConfig,
    GetCallMembers,
    GetGroupCall,
    GetGroupCallChainBlocks,
    GetGroupCallJoinAs,
    GetGroupCallStars,
    GetGroupCallStreamChannels,
    GetGroupCallStreamRtmpUrl,
    InviteConferenceCallParticipant,
    InviteToGroupCall,
    JoinGroupCall,
    JoinGroupCallPresentation,
    LeaveGroupCall,
    LeaveGroupCallPresentation,
    PauseStream,
    PlayAudio,
    PlayVideo,
    ReceivedCall,
    RequestCall,
    ResumeStream,
    SaveCallDebug,
    SaveCallLog,
    SaveDefaultGroupCallJoinAs,
    SaveDefaultSendAs,
    SendConferenceCallBroadcast,
    SendGroupCallEncryptedMessage,
    SendGroupCallMessage,
    SendSignalingData,
    SetCallRating,
    StartScheduledGroupCall,
    ToggleGroupCallRecord,
    ToggleGroupCallSettings,
    ToggleGroupCallStartSubscription,
):
    pass
