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

from .accept_contact import AcceptContact
from .add_contact import AddContact
from .block_from_replies import BlockFromReplies
from .delete_contacts import DeleteContacts
from .delete_contacts_by_phones import DeleteContactsByPhones
from .edit_close_friends import EditCloseFriends
from .export_contact_token import ExportContactToken
from .get_birthdays import GetBirthdays
from .get_blocked_message_senders import GetBlockedMessageSenders
from .get_contact_ids import GetContactIDs
from .get_contact_statuses import GetContactStatuses
from .get_contacts import GetContacts
from .get_contacts_count import GetContactsCount
from .get_saved_contacts import GetSavedContacts
from .get_sponsored_peers import GetSponsoredPeers
from .import_contact_token import ImportContactToken
from .import_contacts import ImportContacts
from .reset_saved_contacts import ResetSavedContacts
from .reset_top_peer_rating import ResetTopPeerRating
from .resolve_phone import ResolvePhone
from .search_contacts import SearchContacts
from .set_blocked import SetBlocked
from .set_contact_note import SetContactNote
from .toggle_top_peers import ToggleTopPeers
from .upload_contact_profile_photo import UploadContactProfilePhoto


class Contacts(
    AcceptContact,
    AddContact,
    BlockFromReplies,
    DeleteContacts,
    DeleteContactsByPhones,
    EditCloseFriends,
    ExportContactToken,
    GetBirthdays,
    GetBlockedMessageSenders,
    GetContactIDs,
    GetContactStatuses,
    GetContacts,
    GetContactsCount,
    GetSavedContacts,
    GetSponsoredPeers,
    ImportContactToken,
    ImportContacts,
    ResetSavedContacts,
    ResetTopPeerRating,
    ResolvePhone,
    SearchContacts,
    SetBlocked,
    SetContactNote,
    ToggleTopPeers,
    UploadContactProfilePhoto,
):
    pass
