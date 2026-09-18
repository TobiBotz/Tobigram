ephemeral_message_bot
=====================

This bot answers in a group, but only the person who asked can see the reply.

An ephemeral message is delivered to one user and is not part of the chat history — no
message id to fetch later, nothing for anyone else to read.

.. include:: /_includes/usable-by/bots.rst

.. code-block:: python

    from pyrogram import Client, filters
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    app = Client("my_bot")


    @app.on_message(filters.command("balance") & filters.group)
    async def balance(client, message):
        await client.send_ephemeral_message(
            chat_id=message.chat.id,
            receiver_id=message.from_user.id,
            text=f"Your balance is {lookup_balance(message.from_user.id)} Stars.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Top up", callback_data="topup"),
            ]]),
        )


    app.run()

``chat_id`` is the group the message appears in and ``receiver_id`` is the only user who
sees it. Both are required.

See :doc:`/features/ephemeral-messages`.
