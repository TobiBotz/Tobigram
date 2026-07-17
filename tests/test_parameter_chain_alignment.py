"""Verify parameters are correctly chained across the call stack.

Tests that every parameter a shortcut method passes to a client send_*
method actually exists in the target method's signature. Catches bugs
where a parameter was added to the shortcut but never propagated to the
underlying method or MTProto raw type.
"""

import ast
import inspect
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyrogram


# ---------------------------------------------------------------------------
# Layer A:  Shortcut methods (reply_*, answer_*)  →  Client send_* methods
# ---------------------------------------------------------------------------

SHORTCUT_CALLS = {
    # (Module, ShortcutMethod)  →  ("client.send_*")
    ("messages_and_media.message", "reply_video"): "send_video",
    ("messages_and_media.message", "answer_video"): "send_video",
    ("messages_and_media.message", "reply_animation"): "send_animation",
    ("messages_and_media.message", "answer_animation"): "send_animation",
    ("messages_and_media.message", "reply_photo"): "send_photo",
    ("messages_and_media.message", "answer_photo"): "send_photo",
    ("messages_and_media.message", "reply_voice"): "send_voice",
    ("messages_and_media.message", "answer_voice"): "send_voice",
    ("messages_and_media.message", "reply_video_note"): "send_video_note",
    ("messages_and_media.message", "answer_video_note"): "send_video_note",
    ("messages_and_media.message", "reply_audio"): "send_audio",
    ("messages_and_media.message", "answer_audio"): "send_audio",
    ("messages_and_media.message", "reply_document"): "send_document",
    ("messages_and_media.message", "answer_document"): "send_document",
    ("messages_and_media.message", "reply_sticker"): "send_sticker",
    ("messages_and_media.message", "answer_sticker"): "send_sticker",
    ("messages_and_media.message", "reply_media_group"): "send_media_group",
    ("messages_and_media.message", "answer_media_group"): "send_media_group",
    ("messages_and_media.message", "reply_dice"): "send_dice",
    ("messages_and_media.message", "answer_dice"): "send_dice",
    ("messages_and_media.message", "reply_text"): "send_message",
    ("messages_and_media.message", "answer_text"): "send_message",
    ("messages_and_media.message", "reply_contact"): "send_contact",
    ("messages_and_media.message", "answer_contact"): "send_contact",
    ("messages_and_media.message", "reply_location"): "send_location",
    ("messages_and_media.message", "answer_location"): "send_location",
    ("messages_and_media.message", "reply_venue"): "send_venue",
    ("messages_and_media.message", "answer_venue"): "send_venue",
    ("messages_and_media.message", "reply_poll"): "send_poll",
    ("messages_and_media.message", "answer_poll"): "send_poll",
    ("messages_and_media.story", "reply_text"): "send_message",
    ("messages_and_media.story", "reply_photo"): "send_photo",
    ("messages_and_media.story", "reply_video"): "send_video",
    ("messages_and_media.story", "reply_video_note"): "send_video_note",
    ("messages_and_media.story", "reply_voice"): "send_voice",
    ("messages_and_media.story", "reply_animation"): "send_animation",
    ("messages_and_media.story", "reply_audio"): "send_audio",
    ("messages_and_media.story", "reply_sticker"): "send_sticker",
    ("messages_and_media.story", "reply_cached_media"): "send_cached_media",
    ("messages_and_media.story", "reply_media_group"): "send_media_group",
}

# Parameters that shortcut methods compute/hardcode, not passed by user
SKIP_PARAMS = {
    "chat_id", "message_thread_id", "direct_messages_topic_id",
    "business_connection_id",
}


def _get_client_send_params(target_method_name: str) -> set:
    """Return the set of parameter names for a client send_* method."""
    import importlib
    
    # Load from the messages module dynamically
    try:
        mod = importlib.import_module("pyrogram.methods.messages")
    except ImportError:
        return set()
    
    # Get the actual classes that contain the methods
    # send_video is in SendVideo class, etc.
    # But we need the bound method from the Client-like class
    # The methods module uses classes as mixins
    for name in dir(mod):
        obj = getattr(mod, name)
        if isinstance(obj, type) and hasattr(obj, target_method_name):
            method = getattr(obj, target_method_name)
            sig = inspect.signature(method)
            return {n for n in sig.parameters if n != "self"}
    
    return set()


def _get_shortcut_passed_params(source_code: str, target_name: str) -> set:
    """Parse the shortcut method source and extract kwargs passed to the client call."""
    import re
    
    call_start = source_code.find(f"self._client.{target_name}(")
    if call_start == -1:
        return set()
    
    # Find matching closing paren
    depth = 0
    call_end = call_start
    started = False
    for i in range(call_start, len(source_code)):
        if source_code[i] == "(":
            depth += 1
            started = True
        elif source_code[i] == ")":
            depth -= 1
            if started and depth == 0:
                call_end = i + 1
                break
    
    call_text = source_code[call_start:call_end]
    
    # Extract keyword=value patterns only at depth 1 (top-level kwargs)
    params = set()
    i = 0
    depth = 0
    while i < len(call_text):
        if call_text[i] == "(":
            depth += 1
        elif call_text[i] == ")":
            depth -= 1
        elif depth == 1 and call_text[i].isalpha():
            # Potential keyword name at top level
            m = re.match(r'(\w+)=', call_text[i:])
            if m:
                kw = m.group(1)
                if kw != "self" and not kw.startswith("_"):
                    params.add(kw)
                i += m.end() - 1
        i += 1
    
    return params


def _get_shortcut_source(module_name: str, method_name: str) -> str:
    """Get the source code of a shortcut method."""
    import importlib
    mod = importlib.import_module(f"pyrogram.types.{module_name}")
    
    # Find the class that contains this method
    from pyrogram.types.messages_and_media.message import Message
    from pyrogram.types.messages_and_media.story import Story
    
    if mod is None:
        return ""
    
    cls = None
    for name in dir(mod):
        obj = getattr(mod, name)
        if isinstance(obj, type) and hasattr(obj, method_name):
            cls = obj
            break
    
    if cls is None:
        return ""
    
    return inspect.getsource(getattr(cls, method_name))


@pytest.mark.parametrize(
    "module_name,shortcut_name,target_send",
    [(m, s, t) for (m, s), t in SHORTCUT_CALLS.items()],
    ids=[f"{m.split('.')[-1]}.{s}->{t}" for (m, s), t in SHORTCUT_CALLS.items()],
)
def test_shortcut_params_in_send(module_name, shortcut_name, target_send):
    """Every kwarg the shortcut passes to client.send_* exists in its signature."""
    # Get shortcut passed params
    source = _get_shortcut_source(module_name, shortcut_name)
    if not source:
        pytest.skip(f"Could not find source for {module_name}.{shortcut_name}")
    
    passed = _get_shortcut_passed_params(source, target_send) - SKIP_PARAMS
    
    # Get target method signature params
    target_params = _get_client_send_params(target_send)
    if not target_params:
        pytest.skip(f"Could not resolve signature for {target_send}")
    
    # Check every passed param exists in the target
    missing = passed - target_params
    if missing:
        pytest.fail(
            f"{module_name}.{shortcut_name} passes kwargs not in "
            f"{target_send}(): {missing}"
        )


# ---------------------------------------------------------------------------
# Layer B:  Client send_* methods  →  Raw MTProto type parameters
# ---------------------------------------------------------------------------

# Mapping of client method → (raw type, list of kwarg names passed to it)
# This is manually curated based on the code in each send method.
# Each entry is: (client_method_name, raw_type_name, expected_kwargs_set)
CLIENT_TO_RAW_MAP = [
    # send_video
    ("send_video", "InputMediaUploadedDocument",
     {"mime_type", "file", "nosound_video", "spoiler", "thumb",
      "video_cover", "video_timestamp", "ttl_seconds"}),
    ("send_video", "DocumentAttributeVideo",
     {"supports_streaming", "duration", "w", "h", "nosound", "video_start_ts"}),
    ("send_video", "DocumentAttributeFilename", {"file_name"}),
    ("send_video", "InputMediaDocumentExternal",
     {"url", "ttl_seconds", "spoiler", "video_cover", "video_timestamp"}),
    
    # send_photo
    ("send_photo", "InputMediaUploadedPhoto",
     {"file", "ttl_seconds", "spoiler"}),
    ("send_photo", "InputMediaPhotoExternal",
     {"url", "ttl_seconds", "spoiler"}),
    
    # send_animation
    ("send_animation", "InputMediaUploadedDocument",
     {"mime_type", "file", "thumb", "spoiler", "ttl_seconds"}),
    ("send_animation", "DocumentAttributeVideo",
     {"supports_streaming", "duration", "w", "h"}),
    ("send_animation", "DocumentAttributeFilename", {"file_name"}),
    ("send_animation", "DocumentAttributeAnimated", set()),
    ("send_animation", "InputMediaDocumentExternal",
     {"url", "ttl_seconds", "spoiler"}),
    
    # send_voice
    ("send_voice", "InputMediaUploadedDocument",
     {"mime_type", "file"}),
    ("send_voice", "DocumentAttributeAudio", {"voice", "duration"}),
    ("send_voice", "InputMediaDocumentExternal", {"url"}),
    
    # send_video_note
    ("send_video_note", "InputMediaUploadedDocument",
     {"mime_type", "file", "thumb"}),
    ("send_video_note", "DocumentAttributeVideo",
     {"round_message", "duration", "w", "h"}),
    
    # send_audio
    ("send_audio", "InputMediaUploadedDocument",
     {"mime_type", "file", "thumb", "spoiler", "ttl_seconds"}),
    ("send_audio", "DocumentAttributeAudio",
     {"duration", "performer", "title"}),
    ("send_audio", "DocumentAttributeFilename", {"file_name"}),
    ("send_audio", "InputMediaDocumentExternal",
     {"url", "ttl_seconds", "spoiler"}),
    
    # send_document
    ("send_document", "InputMediaUploadedDocument",
     {"mime_type", "file", "force_file", "thumb"}),
    ("send_document", "DocumentAttributeFilename", {"file_name"}),
    ("send_document", "InputMediaDocumentExternal", {"url"}),
    
    # send_sticker
    ("send_sticker", "InputMediaUploadedDocument",
     {"mime_type", "file", "spoiler", "ttl_seconds"}),
    ("send_sticker", "DocumentAttributeFilename", {"file_name"}),
    ("send_sticker", "InputMediaDocumentExternal",
     {"url", "ttl_seconds", "spoiler"}),
    
    # send_media_group (each item)
    ("send_media_group", "InputMediaUploadedPhoto", {"file", "spoiler"}),
    ("send_media_group", "InputMediaPhotoExternal", {"url", "spoiler"}),
    ("send_media_group", "InputMediaUploadedDocument",
     {"mime_type", "file", "thumb", "spoiler", "nosound_video",
      "video_cover", "video_timestamp"}),
    ("send_media_group", "InputMediaDocumentExternal",
     {"url", "spoiler", "video_cover", "video_timestamp"}),
    
    # Common: messages.SendMedia
    ("send_video", "messages.SendMedia",
     {"peer", "media", "message", "entities", "silent", "reply_to",
      "random_id", "schedule_date", "noforwards", "effect",
      "invert_media", "schedule_repeat_period", "allow_paid_floodskip",
      "allow_paid_stars", "background", "clear_draft",
      "update_stickersets_order", "send_as", "quick_reply_shortcut",
      "reply_markup", "suggested_post"}),
    
    # send_poll internal raw types
    ("send_poll", "InputMediaPoll",
     {"poll", "correct_answers", "solution", "solution_entities"}),
    ("send_poll", "Poll",
     {"id", "question", "answers", "hash", "closed", "public_voters",
      "multiple_choice", "quiz", "close_period", "close_date",
      "open_answers", "revoting_disabled", "shuffle_answers",
      "hide_results_until_close", "subscribers_only", "countries_iso2"}),
    
    # send_media_group internal: InputSingleMedia
    ("send_media_group", "InputSingleMedia",
     {"media", "random_id", "message", "entities"}),
    
    # send_location internal
    ("send_location", "InputMediaGeoPoint",
     {"geo_point"}),
    ("send_location", "InputMediaGeoLive",
     {"geo_point", "heading", "period", "proximity_notification_radius"}),
    ("send_location", "InputGeoPoint",
     {"lat", "long", "accuracy_radius"}),
]


def _get_raw_type_params(raw_type_name: str) -> set:
    """Return parameter names for a raw MTProto type."""
    import importlib
    
    # Handle namespaced types like messages.SendMedia
    if '.' in raw_type_name:
        parts = raw_type_name.split('.')
        # Try both namespaces: raw.<namespace> and raw.functions.<namespace>
        for prefix in ("pyrogram.raw.", "pyrogram.raw.functions."):
            try:
                mod = importlib.import_module(f"{prefix}{parts[0]}")
                cls = getattr(mod, parts[1])
                sig = inspect.signature(cls.__init__)
                return {name for name in sig.parameters if name != "self"}
            except (ImportError, AttributeError):
                continue
        return set()
    
    # Regular types from pyrogram.raw.types
    try:
        mod = importlib.import_module("pyrogram.raw.types")
        cls = getattr(mod, raw_type_name)
        sig = inspect.signature(cls.__init__)
        return {name for name in sig.parameters if name != "self"}
    except (ImportError, AttributeError):
        return set()


def test_send_method_params_in_raw_types():
    """Every parameter a send method passes to a raw type exists in its constructor."""
    failures = []
    
    for client_method, raw_type_name, expected_kwargs in CLIENT_TO_RAW_MAP:
        actual_params = _get_raw_type_params(raw_type_name)
        if not actual_params and expected_kwargs:
            failures.append(f"{raw_type_name}: could not resolve parameters")
            continue
        
        missing = expected_kwargs - actual_params
        if missing:
            # Some params are computed/hardcoded (like mime_type, file)
            # but if they're passed explicitly, they must exist
            failures.append(
                f"{client_method} → {raw_type_name}: params {missing} "
                f"not in constructor. Actual params: {sorted(actual_params)}"
            )
    
    if failures:
        pytest.fail("\n".join(failures))


def test_kwargs_guard_on_all_send_methods():
    """Every send_* method must have the **kwargs guard."""
    methods_to_check = [
        "send_video", "send_photo", "send_animation", "send_voice",
        "send_video_note", "send_audio", "send_document", "send_sticker",
        "send_media_group",
    ]
    
    import importlib
    mod = importlib.import_module("pyrogram.methods.messages")
    
    failures = []
    for name in methods_to_check:
        method = None
        for cls_name in dir(mod):
            cls = getattr(mod, cls_name)
            if isinstance(cls, type) and hasattr(cls, name):
                method = getattr(cls, name)
                break
        
        if method is None:
            failures.append(f"{name}: method not found")
            continue
        
        sig = inspect.signature(method)
        if "kwargs" not in sig.parameters:
            failures.append(f"{name}: missing **kwargs guard")
            continue
        
        source = inspect.getsource(method)
        if "if kwargs:" not in source:
            failures.append(f"{name}: has **kwargs but no check")
    
    if failures:
        pytest.fail("\n".join(failures))
