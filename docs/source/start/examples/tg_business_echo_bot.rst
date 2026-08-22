business_echo_bot
==================

This simple echo bot replies to every private business message.

It uses the :meth:`~pyrogram.Client.on_business_message` decorator to register a
:obj:`~pyrogram.handlers.BusinessMessageHandler`. Business messages have their own handler:
they never reach :meth:`~pyrogram.Client.on_message`, so a bot can serve its own chats and a
connected account's chats without the two streams mixing.

.. include:: /_includes/usable-by/bots.rst

.. code-block:: python

    from pyrogram import Client, filters

    app = Client("my_account")


    @app.on_business_message(filters.private)
    async def echo(client, message):
        await message.copy(message.chat.id)


    app.run()  # Automatically start() and idle()


See :doc:`/features/business-accounts` for connections, permissions and account management.
