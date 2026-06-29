Welcome to wzgram's documentation!
===================================

`wzgram`_ is an elegant, modern and asynchronous Telegram MTProto API framework
for Python. It is a fork of Pyrogram with support for the latest Telegram features
including **Gifts**, **Stories**, **Topics**, **Business Accounts**, and more.

.. code-block:: python

    from pyrogram import Client, filters

    app = Client("my_account")

    @app.on_message(filters.private)
    async def hello(client, message):
        await message.reply("Hello from wzgram!")

    app.run()

.. toctree::
    :maxdepth: 2
    :caption: Getting Started

    topics/quickstart
    topics/faq

.. toctree::
    :maxdepth: 2
    :caption: API Reference

    api/methods/index
    api/types/index
    api/bound-methods/index

.. toctree::
    :maxdepth: 2
    :caption: Topics

    topics/advanced-usage
    topics/more-on-updates
    topics/storage-engines

.. _wzgram: https://github.com/rjriajul/wzgram
