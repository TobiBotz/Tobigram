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
    :caption: Features

    features/index

.. toctree::
    :maxdepth: 2
    :caption: API Reference

    api/methods/index
    api/types/index
    api/bound-methods/index

.. toctree::
    :maxdepth: 2
    :caption: Concepts

    topics/mtproto-vs-botapi
    topics/message-identifiers
    topics/text-formatting
    topics/serializing

.. toctree::
    :maxdepth: 2
    :caption: Updates & Filters

    topics/use-filters
    topics/create-filters
    topics/more-on-updates
    topics/smart-plugins

.. toctree::
    :maxdepth: 2
    :caption: Configuration

    topics/client-settings
    topics/storage-engines
    topics/proxy
    topics/scheduling
    topics/test-servers
    topics/synchronous

.. toctree::
    :maxdepth: 2
    :caption: Advanced

    topics/advanced-usage
    topics/speedups
    topics/voice-calls
    topics/debugging

.. toctree::
    :maxdepth: 2
    :caption: Help

    topics/faq

.. _wzgram: https://github.com/rjriajul/wzgram
