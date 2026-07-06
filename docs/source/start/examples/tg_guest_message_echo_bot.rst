guest_message_echo_bot
=======================

This simple echo bot replies to every guest message, where possible.

It uses the :meth:`~pyrogram.Client.on_message` decorator to register a :obj:`~pyrogram.handlers.MessageHandler` and applies one filter on it:
``filters.guest_message_query_id`` to make sure it will reply to guest messages only.

.. include:: /_includes/usable-by/bots.rst

.. code-block:: python

    from pyrogram import Client, filters

    app = Client("my_account")


    @app.on_message(filters.guest_message_query_id())
    async def echo(client, message):
        print(message)


    app.run()  # Automatically start() and idle()


You can explore more :doc:`advanced usages <../../topics/advanced-usage>` by directly working with the **raw Telegram API**.
