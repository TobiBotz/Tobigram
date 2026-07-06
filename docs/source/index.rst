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
    :caption: Introduction

    intro/install
    intro/quickstart

.. toctree::
    :maxdepth: 2
    :caption: Getting Started

    start/setup
    start/auth
    start/invoking
    start/updates
    start/errors
    start/examples/index

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
    topics/client-settings
    topics/comparison-with-other-forks
    topics/faq
    topics/create-filters
    topics/debugging
    topics/message-identifiers
    topics/more-on-updates
    topics/mtproto-vs-botapi
    topics/proxy
    topics/scheduling
    topics/serializing
    topics/smart-plugins
    topics/speedups
    topics/storage-engines
    topics/synchronous
    topics/test-servers
    topics/text-formatting
    topics/use-filters
    topics/voice-calls

.. _wzgram: https://github.com/rjriajul/wzgram
