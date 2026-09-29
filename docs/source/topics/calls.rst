Voice & Video Calls
===================

Tobigram features native, high-level support for Telegram **Voice Chats**, **Video Streams**, and **Private Calls**.
Media streaming is executed directly through client methods without requiring manual WebRTC negotiation or third-party client instantiations.

-----

Requirements & Installation
---------------------------

Audio and video streaming requires WebRTC media engines. You can install Tobigram with the optional ``calls`` dependencies:

.. code-block:: bash

    # With pip
    pip install "tobigram[calls]"

    # Or with uv
    uv add "tobigram[calls]"

This installs:
- ``ntgcalls``: High-performance C++ WebRTC bindings for Telegram calls.
- ``py-tgcalls``: Stream pipeline and FFmpeg shell connector.

-----

Streaming in Groups and Channels
--------------------------------

Tobigram exposes high-level methods on the :class:`~pyrogram.Client` class to stream audio and video into any group voice chat or channel live stream.

1. Playing Video Streams
~~~~~~~~~~~~~~~~~~~~~~~~

You can stream local video files or live remote streams (e.g. MP4, HLS, RTMP, HTTP) directly into a voice chat:

.. code-block:: python

    from pyrogram import Client

    app = Client("my_account")

    async def main():
        async with app:
            chat_id = -1001234567890

            # Stream a 720p HD video file or URL
            call = await app.play_video(
                chat_id,
                "https://samplelib.com/mp4/sample-30s-720p.mp4"
            )
            print(f"Streaming video in call ID: {call.id}")

    app.run(main())

2. Playing Audio Streams
~~~~~~~~~~~~~~~~~~~~~~~~

To stream audio (music, radio, podcasts) with video automatically muted/disabled:

.. code-block:: python

    from pyrogram import Client

    app = Client("my_account")

    async def main():
        async with app:
            chat_id = -1001234567890

            # Stream a local MP3 or live Internet radio
            call = await app.play_audio(
                chat_id,
                "https://stream.zeno.fm/f3wvbbqmdg8uv"
            )
            print(f"Playing audio in: {chat_id}")

    app.run(main())

3. Joining without Media (Listener)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you only want the client to join an active voice chat as a listener (with microphone muted and without streaming any media file):

.. code-block:: python

    # Joins voice chat as a muted listener with auto-generated SSRC
    await app.join_group_call(chat_id, muted=True)

-----

Playback Controls
-----------------

While a call is active, you can control playback state and volume:

.. code-block:: python

    # Pause media stream
    await app.pause_stream(chat_id)

    # Resume media stream
    await app.resume_stream(chat_id)

    # Change playback volume (0 to 200%)
    await app.change_call_volume(chat_id, volume=150)

    # Leave the voice chat and stop streaming
    await app.leave_group_call(chat_id)

-----

Stream Lifecycle Events
-----------------------

Tobigram provides built-in update handlers and decorators for the complete streaming lifecycle:

1. When a Stream Starts (:meth:`~pyrogram.Client.on_stream_start`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Triggered as soon as an audio or video stream begins playing in a voice chat. Perfect for sending "Now Playing" messages or logging:

.. code-block:: python

    from pyrogram import Client
    from pyrogram.types import StreamStarted

    app = Client("music_bot")

    @app.on_stream_start()
    async def handle_stream_start(client: Client, update: StreamStarted):
        print(f"Started streaming {update.stream_type} in {update.chat_id}: {update.media_path}")
        await client.send_message(
            update.chat_id,
            f"🎶 **Now Playing:** `{update.media_path}`"
        )

2. When a Stream Finishes (:meth:`~pyrogram.Client.on_stream_end`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For music bots and playlist queues, the :meth:`~pyrogram.Client.on_stream_end` decorator automatically receives an update when a track or video reaches the end:

.. code-block:: python

    from pyrogram import Client
    from pyrogram.types import StreamEnded

    app = Client("music_bot")

    queue = ["song2.mp3", "song3.mp3"]

    @app.on_stream_end()
    async def handle_stream_end(client: Client, update: StreamEnded):
        print(f"Track finished in chat: {update.chat_id}")
        if queue:
            next_track = queue.pop(0)
            await client.play_audio(update.chat_id, next_track)

-----

Voice Chat Administration
-------------------------

Tobigram provides full coverage of Telegram's MTProto ``phone`` functions as clean, high-level methods:

=======================================================  ==============================================================
Method                                                   Description
=======================================================  ==============================================================
:meth:`~pyrogram.Client.create_group_call`               Create and start a new voice chat or live stream in a chat.
:meth:`~pyrogram.Client.discard_group_call`              Completely end and destroy an active voice chat for all members.
:meth:`~pyrogram.Client.edit_group_call_title`           Change the title of an active voice chat.
:meth:`~pyrogram.Client.edit_group_call_participant`     Mute, unmute, or adjust volume of a specific participant.
:meth:`~pyrogram.Client.export_group_call_invite`        Generate an invite link for the voice chat.
:meth:`~pyrogram.Client.toggle_group_call_record`        Start or stop server-side recording of the voice/video chat.
:meth:`~pyrogram.Client.toggle_group_call_settings`      Toggle permissions (e.g. only admins can speak).
:meth:`~pyrogram.Client.get_call_members`                List current participants in a voice chat.
=======================================================  ==============================================================

Ending a Call vs Leaving a Call
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is important to distinguish between **leaving** a call and **ending** a call:

- **Leave Call** (:meth:`~pyrogram.Client.leave_group_call`):
  Stops your client's media stream and disconnects your client from the voice chat. Other participants remain in the call.
- **End / Discard Call** (:meth:`~pyrogram.Client.discard_group_call`):
  Admin action (corresponds to *"End Video Chat"* in the Telegram UI). Completely closes and destroys the voice chat for all members.

-----

1-on-1 Private Calls
--------------------

For direct peer-to-peer (P2P) calls between two users:

.. code-block:: python

    # 1. Initiate an outgoing call
    call = await app.request_call(user_id=12345678, g_a_hash=b"...", protocol=protocol, video=False)

    # 2. Accept an incoming call
    await app.accept_call(call_id=call.id, access_hash=call.access_hash, g_b=b"...", protocol=protocol)

    # 3. Confirm encryption keys
    await app.confirm_call(call_id=call.id, access_hash=call.access_hash, g_a=b"...", key_fingerprint=123, protocol=protocol)

    # 4. Hang up / Decline a private call
    await app.discard_call(call_id=call.id, access_hash=call.access_hash)
