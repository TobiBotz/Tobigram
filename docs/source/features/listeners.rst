Listeners
=========

*A wzgram extension*

A listener waits for the next update inline, inside the code that asked for it. Instead of
registering a handler, storing state keyed by user id and picking the conversation back up
in a second function, you write the conversation as a conversation.

.. code-block:: python

    @app.on_message(filters.command("setup"))
    async def setup(client, message):
        answer = await message.chat.ask("What should I call you?")
        await answer.reply(f"Nice to meet you, {answer.text}.")


-----

listen and ask
--------------

:meth:`~pyrogram.Client.ask` sends a question and waits for the reply.
:meth:`~pyrogram.Client.listen` only waits:

.. code-block:: python

    from wzgram import filters

    reply = await app.ask(
        chat_id=user_id,
        text="Send me the file now.",
        filters=filters.document,
        timeout=120,
    )

    await app.download_media(reply)

Both accept the criteria that decide which update counts: ``chat_id``, ``user_id``,
``message_id``, ``inline_message_id`` — each taking a single value or a list — plus any
``filters.Filter``.

``listener_type`` chooses what to wait for: :obj:`~pyrogram.enums.ListenerTypes`'s
``MESSAGE`` (the default) or ``CALLBACK_QUERY``.

.. code-block:: python

    query = await app.listen(
        chat_id=chat_id,
        user_id=user_id,
        listener_type=enums.ListenerTypes.CALLBACK_QUERY,
        timeout=60,
    )

    await query.answer("Got it")

:meth:`~pyrogram.Client.wait_for_message` and
:meth:`~pyrogram.Client.wait_for_callback_query` are thin shortcuts over the same thing, and
:meth:`~pyrogram.Client.register_next_step_handler` runs a callback on the next matching
update instead of returning it.

Bound versions live on :meth:`Chat.listen() <pyrogram.types.Chat.listen>`,
:meth:`Chat.ask() <pyrogram.types.Chat.ask>` and
:meth:`Chat.stop_listening() <pyrogram.types.Chat.stop_listening>`.

Timeouts and cancellation
-------------------------

Two errors end a wait, and the difference matters:

- ``ListenerTimeout`` — nobody answered in time. Retrying is reasonable.
- ``ListenerStopped`` — the wait was cancelled, by
  :meth:`~pyrogram.Client.stop_listening` or by the client shutting down. Retrying is not.

.. code-block:: python

    from wzgram.errors import ListenerTimeout

    try:
        answer = await message.chat.ask("Still there?", timeout=30)
    except ListenerTimeout:
        await message.reply("Never mind, I'll ask later.")

``timeout`` defaults to the client's ``listener_timeout``, 300 seconds. Passing ``None``
waits forever, which leaks one listener per person who wanders off — do that only when
something else is guaranteed to end the wait.

What it does to updates
-----------------------

A consumed update does **not** reach your handlers. That is the point: the message answering
a question should not also run the command handler. Raw update handlers still see it, since
they are a different contract.

The hook lives in the dispatcher rather than in the handlers, so an update probes at most
three buckets keyed by peer id, and a client with no listeners pays one dictionary length
check per update.

Conversations inside handlers
-----------------------------

Handler callbacks are awaited inline in their dispatcher worker, so a handler parked in
``await listen()`` is holding a worker. wzgram covers each parked worker with a relief
worker for as long as it is parked — without that, the worker-th concurrent conversation
would exhaust the pool, and the workers left would be exactly the ones needed to deliver the
updates everyone is waiting for.

You do not have to do anything for this. It is why nesting conversations works.

Limits
------

``WZGRAM_MAX_LISTENERS`` (1000) is the process-wide ceiling on outstanding waiters, shared by
every client in the process — like every other budget in wzgram, see :doc:`performance`. It
can also be set per client with ``max_listeners``.

Expiry is one deadline heap and one reaper task per client rather than a timer per listener,
which is what makes ten thousand waiters affordable.

Gotchas
-------

- A listener registered for a chat the client has never met takes an ``int`` id as given —
  usernames are resolved at registration, ints are not. Pass a username if the peer may be
  unknown.
- ``stop_listening`` with no arguments stops every listener on that client. Narrow it with
  ``chat_id`` / ``user_id`` unless you mean all of them.
- Under ``workers > 1`` two workers can race for the same listener. Only one wins, and the
  loser's update falls through to the handlers rather than vanishing — so a handler may see
  an update you expected a listener to swallow.
