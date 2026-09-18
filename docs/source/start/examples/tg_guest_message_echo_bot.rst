guest_message_echo_bot
=======================

This simple echo bot replies to every guest message, where possible.

It uses the :meth:`~pyrogram.Client.on_guest_message` decorator to register a
:obj:`~pyrogram.handlers.GuestMessageHandler`, which only receives guest messages.

.. include:: /_includes/usable-by/bots.rst

.. code-block:: python

    from pyrogram import Client

    app = Client("my_account")


    @app.on_guest_message()
    async def echo(client, message):
        print(message)


    app.run()  # Automatically start() and idle()


You can explore more :doc:`advanced usages <../../topics/advanced-usage>` by directly working with the **raw Telegram API**.
