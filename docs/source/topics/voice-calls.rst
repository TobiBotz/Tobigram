Voice Calls
===========

wzgram does not implement voice or video calls. The MTProto call layer needs a media stack —
WebRTC, codecs, encryption negotiation — that is a different project from an API framework,
so it is handled by external libraries built on top of wzgram.


-----

Libraries
---------

- `pytgcalls <https://github.com/pytgcalls/pytgcalls>`_ — group voice chats and private
  calls, actively maintained, and the one most projects use.
- `tgcalls <https://github.com/MarshalX/tgcalls>`_ — the Python bindings pytgcalls is built
  on, usable directly for lower-level control.

Because wzgram is a drop-in replacement for Pyrogram, a library that takes a Pyrogram client
takes a wzgram one.

What wzgram does cover
----------------------

The *signalling* around calls is ordinary API surface, so wzgram handles it:

- video chats starting and ending arrive as service messages —
  ``filters.video_chat_started``, ``filters.video_chat_ended`` and
  ``filters.video_chat_members_invited``
- :meth:`~pyrogram.Client.get_call_members` lists who is in a group call
- everything else in Telegram's ``phone`` namespace is reachable as a raw function through
  :meth:`~pyrogram.Client.invoke` — see :doc:`advanced-usage`

An older implementation, `pylibtgvoip <https://github.com/bakatrouble/pylibtgvoip>`_, is
outdated: the Telegram VoIP library underneath it was deprecated.
