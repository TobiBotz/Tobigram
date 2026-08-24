Business Accounts
=================

*Bot API 7.2 — March 2024, extended in 7.3 and 9.0*

Telegram Business lets a user connect a bot to their **personal** account. Once connected,
the bot sees the messages that arrive in that user's private chats and can answer them as
the user, not as itself. The customer never sees a bot: they see the person they wrote to.

This is the only part of the API where a bot acts *on behalf of* a human account, which is
why nearly every send method carries a ``business_connection_id`` parameter.


-----

The connection
--------------

The user connects your bot from **Settings → Business → Chatbots**. Your bot is told about
it through :meth:`~pyrogram.Client.on_business_connection`:

.. code-block:: python

    from wzgram import Client

    app = Client("my_bot")

    connections = {}


    @app.on_business_connection()
    async def connected(client, connection):
        connections[connection.user.id] = connection.id
        print(f"{connection.user.first_name} connected, enabled: {connection.is_enabled}")
        print(f"can reply: {connection.rights.can_reply}")


    app.run()

The connection id is what you store. Everything else flows from it. You can also fetch a
connection you already know the id of with :meth:`~pyrogram.Client.get_business_connection`.

Handling business messages
--------------------------

Business updates come through their own handlers, separate from the bot's own messages, so
a bot can serve both roles without the two streams mixing:

.. code-block:: python

    @app.on_business_message()
    async def answer(client, message):
        await message.reply("Thanks for writing! We'll be with you shortly.")

- :meth:`~pyrogram.Client.on_business_message` — a message arrived in a connected chat
- :meth:`~pyrogram.Client.on_edited_business_message` — one was edited
- :meth:`~pyrogram.Client.on_deleted_business_messages` — one or more were deleted

A reply sent from inside these handlers is sent as the user. Under the hood the bound method
carries the connection id for you; when you call a client method directly, pass it yourself:

.. code-block:: python

    await app.send_message(
        chat_id=customer_id,
        text="Your order is ready.",
        business_connection_id=connection_id,
    )

Every ``send_*`` method accepts ``business_connection_id``, as do
:meth:`~pyrogram.Client.edit_message_text`, :meth:`~pyrogram.Client.send_reaction` and
:meth:`~pyrogram.Client.delete_business_messages`.

Managing the account
--------------------

Bot API 9.0 opened up the business account's own settings. With the user's permission a bot
can change the things a business owner would otherwise set by hand:

- :meth:`~pyrogram.Client.update_business_intro` — the greeting card shown in an empty chat
- :meth:`~pyrogram.Client.update_business_greeting_message` — the automatic first reply
- :meth:`~pyrogram.Client.update_business_away_message` — what to say outside work hours
- :meth:`~pyrogram.Client.update_business_work_hours` — those work hours
- :meth:`~pyrogram.Client.update_business_location` — the address on the profile

Business chat links are deep links that open a chat with a message already typed:

.. code-block:: python

    from wzgram import raw

    link = await app.create_business_chat_link(
        raw.types.InputBusinessChatLink(
            message="I'd like to book a table",
            title="Reservations",
        )
    )

    print(link.link)

See also :meth:`~pyrogram.Client.get_business_chat_links`,
:meth:`~pyrogram.Client.resolve_business_chat_link` and
:meth:`~pyrogram.Client.delete_business_chat_link`.

.. note::

    The account-management methods above are the *user* side of Telegram Business: they are
    what the business owner's own client calls, so they are usable by user sessions, not by
    bots. A bot connected to that account works through the connection id instead.

Stars and gifts held by the account
-----------------------------------

A connected business account has its own Stars balance and its own gifts, distinct from the
bot's:

.. code-block:: python

    gifts = await app.get_business_account_gifts(
        business_connection_id=connection_id,
        exclude_unsaved=True,
    )

    balance = await app.get_business_account_star_balance(connection_id)

    await app.transfer_business_account_stars(connection_id, star_count=100)

Gotchas
-------

- Check :obj:`~pyrogram.types.BusinessConnection`'s ``rights`` before sending. A connection
  whose ``rights.can_reply`` is ``False`` was made in read-only mode and every send will be
  rejected; ``is_enabled`` going ``False`` means the user paused it. ``rights`` also gates
  gifts, stories and profile edits separately.
- The connection id is per user, not per chat. One id covers every private chat that user
  has.
- A business message is not a bot message: filters like ``filters.command`` still work, but
  the update arrives through :meth:`~pyrogram.Client.on_business_message`, so a handler
  registered with :meth:`~pyrogram.Client.on_message` will never see it.
