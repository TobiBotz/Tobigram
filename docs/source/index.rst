Welcome to wzgram's documentation!
===================================

`wzgram`_ is an elegant, modern and asynchronous Telegram MTProto API framework for Python.
It is a fork of Pyrogram and a **drop-in replacement** — the distribution is ``wzgram``, the
import stays ``pyrogram``, and existing code runs unchanged.

.. code-block:: python

    from pyrogram import Client, filters

    app = Client("my_account")

    @app.on_message(filters.private)
    async def hello(client, message):
        await message.reply("Hello from wzgram!")

    app.run()

-----

What you get
------------

-   **Up to date with Telegram.** Every parameter of every implemented method and type is
    checked against Bot API 10.2 and the TL schema at build time. :doc:`features/index`
    walks what Telegram has shipped, in the order it shipped it — business accounts, paid
    media, gifts, stories, checklists, suggested posts, rich messages, ephemeral messages.
-   **Conversations without state machines.** :doc:`features/listeners` waits for the next
    message or button press inline, inside the handler that asked for it.
-   **Built to stay up.** Client-side :doc:`rate limiting <features/rate-limiting>`, bounded
    memory on every transfer path, Rust cryptography, and a hot path measured rather than
    guessed — see :doc:`features/performance`.
-   **Portable sessions.** Checksummed :doc:`session strings <features/session-strings>` that
    survive being copy-pasted, with every legacy format still decodable.

New here? :doc:`intro/install` then :doc:`intro/quickstart`.

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

    api/client
    api/methods/index
    api/types/index
    api/bound-methods/index
    api/handlers
    api/filters
    api/storage
    api/errors

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
