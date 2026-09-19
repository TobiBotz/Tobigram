Welcome to Tobigram
===================

.. raw:: html

    <div align="center">
        <a href="/">
            <div class="pyrogram-logo-index">
                <img src="_static/pyrogram.png" alt="Tobigram">
            </div>
            <div class="pyrogram-text pyrogram-text-index">Tobigram</div>
        </a>
    </div>

    <p align="center">
        <b>Telegram MTProto API Framework for Python</b>
        <br>
        <a href="https://tobigram.com">Homepage</a> •
        <a href="https://github.com/TobiBotz/Tobigram">Development</a> •
        <a href="https://docs.tobigram.com">Documentation</a> •
        <a href="https://t.me/TobigramNews">News</a>
    </p>

.. code-block:: python

    from pyrogram import Client, filters

    app = Client("my_account")


    @app.on_message(filters.private)
    async def hello(client, message):
        await message.reply("Hello from Tobigram!")


    app.run()

**Tobigram** is a modern, elegant and asynchronous :doc:`MTProto API <topics/mtproto-vs-botapi>` framework. It enables you
to easily interact with the main Telegram API through a user account (custom client) or a bot identity
(bot API alternative) using Python.

How the Documentation is Organized
----------------------------------

Contents are organized into sections composed of self-contained topics which can be all accessed from the sidebar,
or by following them in order using the :guilabel:`Next` button at the end of each page. You can also switch to
:guilabel:`Dark` or :guilabel:`Light` theme or leave on :guilabel:`Auto` (follows system preferences) by using the
dedicated button in the top left corner.

Here below you can, instead, find a list of the most relevant pages for a quick access.

First Steps
^^^^^^^^^^^

- :doc:`intro/quickstart`: Overview to get you started quickly.
- :doc:`intro/install`: Installation guide with pip and uv.
- :doc:`start/invoking`: How to call Tobigram's methods.
- :doc:`start/updates`: How to handle Telegram updates.
- :doc:`start/errors`: How to handle API errors correctly.

API Reference
^^^^^^^^^^^^^

- :doc:`api/client`: Reference details about the Client class.
- :doc:`api/methods/index`: List of available high-level methods.
- :doc:`api/types/index`: List of available high-level types.
- :doc:`api/bound-methods/index`: List of convenient bound methods.
- :doc:`api/enums`: List of available enumerations.
- :doc:`api/handlers`: List of available update handlers.
- :doc:`api/filters`: List of available update filters.

Telegram Raw API
^^^^^^^^^^^^^^^^

- :doc:`telegram/functions/index`: List of all raw Telegram functions.
- :doc:`telegram/types/index`: List of all raw Telegram types.
- :doc:`telegram/base/index`: List of all raw base types.

Features
^^^^^^^^

- :doc:`features/index`: Modern features Telegram has shipped (Gifts, Stories, Topics, Business).
- :doc:`features/listeners`: Inline conversation flows without state machines.
- :doc:`features/rate-limiting`: Client-side rate limiting and throttling.
- :doc:`features/session-strings`: Checksummed portable session strings.

Meta
^^^^

- :doc:`topics/faq`: Answers to common Tobigram questions.
- :doc:`topics/speedups`: Boost performance with Rust cryptography and uvloop.
- :doc:`topics/mtproxy`: Built-in MTProxy Fake-TLS support.
- :doc:`topics/web-proxy`: MTProto Web Proxy over WebSocket/TLS 1.3.

.. toctree::
    :hidden:
    :caption: Introduction

    intro/install
    intro/quickstart

.. toctree::
    :hidden:
    :caption: Getting Started

    start/setup
    start/auth
    start/invoking
    start/updates
    start/errors
    start/examples/index

.. toctree::
    :hidden:
    :caption: Features

    features/index

.. toctree::
    :hidden:
    :caption: API Reference

    api/client
    api/methods/index
    api/types/index
    api/bound-methods/index
    api/handlers
    api/filters
    api/storage
    api/errors
    api/enums

.. toctree::
    :hidden:
    :caption: Concepts

    topics/mtproto-vs-botapi
    topics/message-identifiers
    topics/text-formatting
    topics/rich-text
    topics/serializing
    topics/reporting

.. toctree::
    :hidden:
    :caption: Updates & Filters

    topics/use-filters
    topics/create-filters
    topics/more-on-updates
    topics/smart-plugins

.. toctree::
    :hidden:
    :caption: Configuration

    topics/client-settings
    topics/storage-engines
    topics/proxy
    topics/mtproxy
    topics/web-proxy
    topics/scheduling
    topics/test-servers
    topics/synchronous

.. toctree::
    :hidden:
    :caption: Advanced

    topics/advanced-usage
    topics/speedups
    topics/voice-calls
    topics/debugging

.. toctree::
    :hidden:
    :caption: Help

    topics/faq

.. toctree::
    :hidden:
    :caption: Telegram Raw API

    telegram/functions/index
    telegram/types/index
    telegram/base/index


