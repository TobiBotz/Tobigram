Quick Start
===========

Installation
------------

Install wzgram from PyPI:

.. code-block:: bash

    pip install wzgram

For better performance, install with the optional ``fast`` extra:

.. code-block:: bash

    pip install wzgram[fast]

Your First Bot
--------------

Create a file ``bot.py``:

.. code-block:: python

    from pyrogram import Client, filters

    app = Client(
        "my_bot",
        bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    )

    @app.on_message(filters.command("start"))
    async def start(client, message):
        await message.reply("Hello! I'm a wzgram bot.")

    @app.on_message(filters.private & ~filters.command("start"))
    async def echo(client, message):
        await message.reply(message.text)

    app.run()

Run it:

.. code-block:: bash

    python bot.py

Your First User Client
----------------------

Create a file ``user.py``:

.. code-block:: python

    from pyrogram import Client, filters

    app = Client("my_account")

    @app.on_message(filters.private)
    async def hello(client, message):
        await message.reply("Hello from wzgram!")

    app.run()

On first run, you will be prompted for your **api_id** and **api_hash**,
which you can obtain from https://my.telegram.org/apps.

Synchronous Usage
-----------------

wzgram is fully asynchronous but also supports synchronous use out of the box:

.. code-block:: python

    from pyrogram import Client

    app = Client("my_account")

    with app:
        app.send_message("me", "Hello from sync wzgram!")

Using the ``with`` block automatically handles ``start()`` and ``stop()``.
