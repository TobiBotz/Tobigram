FAQ
===

What is wzgram?
---------------

wzgram is a fork of Pyrogram with support for the latest Telegram features
including Gifts, Stories, Topics, Business Accounts, and more.

How is it different from Pyrogram?
-----------------------------------

wzgram stays up to date with Telegram's latest API changes faster than the
upstream Pyrogram project. It adds support for newer Telegram features and
fixes compatibility issues with recent Telegram server updates.

What Python versions are supported?
------------------------------------

Python 3.10 through 3.14.

How do I install wzgram?
-------------------------

.. code-block:: bash

    pip install wzgram

Or install directly from the repository:

.. code-block:: bash

    pip install git+https://github.com/rjriajul/wzgram.git

Can I use wzgram with uv?
--------------------------

Yes. wzgram is built with Hatch and fully compatible with uv:

.. code-block:: bash

    uv add wzgram

Do I need an API ID and hash?
------------------------------

Yes, for both. Get them at https://my.telegram.org/apps. A bot additionally needs its
token from `@BotFather <https://t.me/botfather>`_, but the API key is still required for
the first authorization — wzgram raises ``AttributeError`` without it. Once a session
exists, neither is needed again.

How do I start a Client?
-------------------------

.. code-block:: python

    from wzgram import Client

    async with Client("my_account") as app:
        await app.send_message("me", "Hello!")

The context manager starts and stops the client for you. Doing it by hand is
``await app.start()`` and ``await app.stop()``.

Can I use wzgram synchronously?
-------------------------------

No. wzgram is async-only — there is no wrapper that lets you call methods without
``await``. Use :py:func:`asyncio.run` or :meth:`~pyrogram.Client.run`:

.. code-block:: python

    import asyncio

    from wzgram import Client


    async def main():
        async with Client("my_account") as app:
            await app.send_message("me", "Hello!")


    asyncio.run(main())

See :doc:`synchronous` for calling wzgram from code that is not async.

How do I handle progress for uploads and downloads?
----------------------------------------------------

Pass a ``progress`` callback to any send or download method:

.. code-block:: python

    async def progress(current, total):
        print(f"{current * 100 / total:.1f}%")

    await app.send_document("me", "file.zip", progress=progress)

What are bound methods?
------------------------

Bound methods are convenience methods attached to type instances. For example,
a ``Message`` object has ``.reply()``, ``.delete()``, and ``.download()``:

.. code-block:: python

    msg = await app.send_message("me", "Hello!")
    await msg.reply("World!")       # bound method on the Message object
    await msg.delete()              # same

Does wzgram support parallel downloads?
-----------------------------------------

Yes. wzgram uses an aria2c-style parallel download engine that fetches file
chunks concurrently from multiple sessions. Pass a ``progress`` callback to
:meth:`~pyrogram.Client.download_media` to track speed and progress.

Does wzgram support Stories?
-----------------------------

Yes. Use methods like :meth:`~pyrogram.Client.send_story`,
:meth:`~pyrogram.Client.get_stories`, and :meth:`~pyrogram.Client.delete_stories`
to manage stories.

Does wzgram support Gifts and Stars?
--------------------------------------

Yes. wzgram fully supports Telegram Stars, Gifts, Gift Upgrades, and
Auction Bids through the ``payments`` method group.

Does wzgram support Business Accounts?
----------------------------------------

Yes. wzgram provides business-specific methods for managing chat links,
away messages, greeting messages, working hours, and locations.

Does wzgram support Rich Text (styled messages)?
--------------------------------------------------

Yes, and there are two different things under that name. Message-level formatting —
bold, spoilers, custom emoji, formatted dates — is covered in :doc:`text-formatting`.
Full documents with headings, lists and tables are :doc:`rich messages
</features/rich-messages>`, sent with ``rich_text`` on
:meth:`~pyrogram.Client.send_message` or with
:meth:`~pyrogram.Client.send_rich_message`.

How do I enable debug logging?
-------------------------------

.. code-block:: python

    import logging
    logging.basicConfig(level=logging.INFO)

For more verbose output:

.. code-block:: python

    logging.getLogger("pyrogram").setLevel(logging.DEBUG)

Can I wait for a user's reply without a handler?
--------------------------------------------------

Yes, with :meth:`~pyrogram.Client.ask` and :meth:`~pyrogram.Client.listen`:

.. code-block:: python

    answer = await message.chat.ask("What is your name?", timeout=60)
    await answer.reply(f"Hello, {answer.text}!")

See :doc:`/features/listeners`.

How do I avoid FloodWait?
--------------------------

By default wzgram sends at full speed and lets ``sleep_threshold`` decide how long a
``FloodWait`` it sits out for you rather than raising. If you would rather not reach one at
all, pass ``rate_limits`` to enable the built-in token-bucket limiter, which paces requests
below Telegram's limits. See :doc:`/features/rate-limiting`.

Why does my bot use so much memory with many clients?
-------------------------------------------------------

It should not: transfer budgets are process-wide, not per client, so fifteen clients do not
reserve fifteen times the buffers. If memory is still high, lower
``WZGRAM_MAX_READ_AHEAD``. See :doc:`/features/performance`.

Can I keep sessions in a database instead of a file?
------------------------------------------------------

Yes. :obj:`~pyrogram.storage.MongoStorage` and :obj:`~pyrogram.storage.RedisStorage` keep
the session in a database, and :obj:`~pyrogram.storage.HybridStorage` puts a local cache in
front of either so reads never pay network latency:

.. code-block:: python

    from wzgram import Client
    from wzgram.storage import HybridStorage, MongoStorage

    app = Client(
        "my_account",
        storage_engine=HybridStorage(
            "my_account",
            backend=MongoStorage("my_account", "mongodb://localhost:27017"),
        ),
    )

Install the driver with ``pip install "wzgram[mongo]"`` or ``pip install "wzgram[redis]"``.
See :doc:`storage-engines`.

Where can I get help?
---------------------

Open an issue on the `GitHub repository`_.

.. _GitHub repository: https://github.com/rjriajul/wzgram/issues
