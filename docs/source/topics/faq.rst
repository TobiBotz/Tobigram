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

For user accounts, yes. Get them at https://my.telegram.org/apps.
For bot accounts, you only need a bot token from @BotFather.

How do I start a Client?
-------------------------

.. code-block:: python

    from pyrogram import Client

    app = Client("my_account")
    await app.start()
    await app.send_message("me", "Hello!")
    await app.stop()

Can I use wzgram synchronously?
-------------------------------

Yes. The Client can be used as a context manager:

.. code-block:: python

    from pyrogram import Client

    app = Client("my_account")
    with app:
        app.send_message("me", "Hello!")

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

Yes. You can send rich text messages using Markdown or HTML via the
``rich_text`` and ``rich_text_parse_mode`` parameters on
:meth:`~pyrogram.Client.send_message`.

How do I enable debug logging?
-------------------------------

.. code-block:: python

    import logging
    logging.basicConfig(level=logging.INFO)

For more verbose output:

.. code-block:: python

    logging.getLogger("pyrogram").setLevel(logging.DEBUG)

Where can I get help?
---------------------

Open an issue on the `GitHub repository`_.

.. _GitHub repository: https://github.com/rjriajul/wzgram/issues
