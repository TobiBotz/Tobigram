Ephemeral Messages
==================

*Bot API 10.2 — July 2026*

An ephemeral message is sent into a group but shown to **one person**. Nobody else in the
chat sees it, and it is not part of the chat's history — there is no message id to fetch
later, no forwarding, no search.

It is what a bot should use for anything addressed to one member: an error, a private prompt,
a result nobody else asked for. Before this existed the choices were spamming the group or
starting a private chat the user may not have opened.

Ephemeral messages are sent by **bots**.


-----

Sending one
-----------

.. code-block:: python

    from pyrogram import Client, filters

    app = Client("my_bot")


    @app.on_message(filters.command("balance"))
    async def balance(client, message):
        await client.send_ephemeral_message(
            chat_id=message.chat.id,
            receiver_id=message.from_user.id,
            text=f"Your balance is {get_balance(message.from_user.id)} Stars.",
        )


    app.run()

``chat_id`` is the group it appears in; ``receiver_id`` is the only person who will see it.
Both are required — an ephemeral message with no receiver has nowhere to go.

Keyboards, replies and rich text
--------------------------------

The message is otherwise a normal one. It takes a ``reply_markup``, so a private prompt can
carry buttons; ``reply_parameters``, so it can quote the message that triggered it; and
``rich_text`` with ``rich_text_media`` for a full :doc:`rich message <rich-messages>`:

.. code-block:: python

    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    await app.send_ephemeral_message(
        chat_id=group_id,
        receiver_id=user_id,
        text="Only you can see this. Continue?",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Yes", callback_data="go"),
            InlineKeyboardButton("No", callback_data="stop"),
        ]]),
    )

``query_id`` answers a guest bot query with an ephemeral message — see
:doc:`guest-mode-and-managed-bots`.

Deleting one
------------

.. code-block:: python

    await app.delete_ephemeral_message(
        chat_id=group_id,
        receiver_id=user_id,
        message_id=sent.id,
    )

The receiver has to be named again, because the message only ever existed for them.

Gotchas
-------

- ``disable_web_page_preview`` is accepted and **ignored**. The RPC behind ephemeral
  messages has no link preview field; the parameter is kept so existing call sites do not
  break.
- These messages are not in the chat history. Do not expect
  :meth:`~pyrogram.Client.get_messages` to find one, and do not build a flow that needs to
  read it back — hold what you need in your own state.
- Everything about them is per-receiver. To tell three people something privately, send
  three messages.
