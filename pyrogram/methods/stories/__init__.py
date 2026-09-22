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

from .can_post_stories import CanPostStories
from .copy_story import CopyStory
from .copy_story_album import CopyStoryAlbum
from .create_story_album import CreateStoryAlbum
from .delete_stories import DeleteStories
from .delete_story_album import DeleteStoryAlbum
from .edit_story_caption import EditStoryCaption
from .edit_story_media import EditStoryMedia
from .edit_story_privacy import EditStoryPrivacy
from .enable_stealth_mode import EnableStealthMode
from .export_story_link import ExportStoryLink
from .forward_story import ForwardStory
from .get_all_stories import GetAllStories
from .get_archived_stories import GetArchivedStories
from .get_chat_stories import GetChatStories
from .get_pinned_stories import GetPinnedStories
from .get_stories import GetStories
from .get_story_album_stories import GetStoryAlbumStories
from .get_story_albums import GetStoryAlbums
from .get_story_views import GetStoryViews
from .hide_chat_stories import HideChatStories
from .pin_chat_stories import PinChatStories
from .read_chat_stories import ReadChatStories
from .reorder_story_albums import ReorderStoryAlbums
from .report_story import ReportStory
from .send_story import SendStory
from .send_story_reaction import SendStoryReaction
from .show_chat_stories import ShowChatStories
from .unpin_chat_stories import UnpinChatStories
from .update_story_album import UpdateStoryAlbum
from .view_stories import ViewStories
from .get_stories_views import GetStoriesViews
from .get_story_reactions_list import GetStoryReactionsList
from .get_chats_to_send_stories import GetChatsToSendStories
from .search_stories import SearchStories
from .start_live_story import StartLiveStory
from .toggle_stories_pinned_to_top import ToggleStoriesPinnedToTop
from .toggle_all_stories_hidden import ToggleAllStoriesHidden
from .get_all_read_peer_stories import GetAllReadPeerStories
from .get_peer_max_story_ids import GetPeerMaxStoryIDs


class Stories(
    CanPostStories,
    CopyStory,
    CopyStoryAlbum,
    CreateStoryAlbum,
    DeleteStories,
    DeleteStoryAlbum,
    EditStoryCaption,
    EditStoryMedia,
    EditStoryPrivacy,
    EnableStealthMode,
    ExportStoryLink,
    ForwardStory,
    GetAllStories,
    GetArchivedStories,
    GetChatStories,
    GetPinnedStories,
    GetStories,
    GetStoryAlbumStories,
    GetStoryAlbums,
    GetStoryViews,
    HideChatStories,
    PinChatStories,
    ReadChatStories,
    ReorderStoryAlbums,
    ReportStory,
    SendStory,
    SendStoryReaction,
    ShowChatStories,
    UnpinChatStories,
    UpdateStoryAlbum,
    ViewStories,
    GetStoriesViews,
    GetStoryReactionsList,
    GetChatsToSendStories,
    SearchStories,
    StartLiveStory,
    ToggleStoriesPinnedToTop,
    ToggleAllStoriesHidden,
    GetAllReadPeerStories,
    GetPeerMaxStoryIDs,
):
    pass
