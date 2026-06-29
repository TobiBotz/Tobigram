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

Python 3.8 through 3.14.

Can I use wzgram synchronously?
--------------------------------

Yes. Importing from ``pyrogram`` automatically wraps async methods in sync
helpers. Use the ``with`` block:

.. code-block:: python

    from pyrogram import Client

    app = Client("my_account")
    with app:
        app.send_message("me", "Hello!")

Do I need an API ID and hash?
-----------------------------

For user accounts, yes. Get them at https://my.telegram.org/apps.
For bot accounts, you only need a bot token from @BotFather.

Where can I get help?
---------------------

Open an issue on the `GitHub repository`_.

.. _GitHub repository: https://github.com/rjriajul/wzgram/issues
