Voice Calls
===========

.. note::
    **Tobigram now provides native voice and video streaming!**
    You no longer need external setup to stream audio and video. See the comprehensive :doc:`calls` guide for full examples.

pyrogram historically did not implement media streaming for calls. The MTProto call layer needs a media stack —
WebRTC, codecs, encryption negotiation — that is a different project from an API framework.


-----

Libraries
---------

- `ntgcalls <https://github.com/pytgcalls/ntgcalls>`_ — modern C++ WebRTC bindings for
  group video chats and voice calls.
- `py-tgcalls <https://github.com/pytgcalls/pytgcalls>`_ — high-level streaming pipeline
  built on top of ntgcalls, integrated natively into Tobigram.

Because pyrogram is a drop-in replacement for Pyrogram, a library that takes a Pyrogram client
takes a pyrogram one.

What pyrogram does cover
------------------------

The *signalling* around calls is ordinary API surface, so pyrogram handles it:

- video chats starting and ending arrive as service messages —
  ``filters.video_chat_started``, ``filters.video_chat_ended`` and
  ``filters.video_chat_members_invited``
- :meth:`~pyrogram.Client.get_call_members` lists who is in a group call
- everything else in Telegram's ``phone`` namespace is reachable as a raw function through
  :meth:`~pyrogram.Client.invoke` — see :doc:`advanced-usage`

An older implementation, `pylibtgvoip <https://github.com/bakatrouble/pylibtgvoip>`_, is
outdated: the Telegram VoIP library underneath it was deprecated.
