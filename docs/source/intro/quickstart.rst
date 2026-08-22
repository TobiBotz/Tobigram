Quick Start
===========

Six steps from nothing to a program that talks to Telegram. Each one says what it is for, so
you can tell which parts you will need to change for your own project.


-----

1. Install wzgram
-----------------

.. code-block:: bash

    $ python3 -m venv venv
    $ source venv/bin/activate        # Windows: venv\Scripts\activate
    $ pip install wzgram

The virtual environment keeps this project's packages out of your system Python. See
:doc:`install` if anything here fails.

2. Get an API key
-----------------

Log in at https://my.telegram.org/apps and create an application. You get two values back:
an **api_id** (a number) and an **api_hash** (a 32-character string).

These identify your *application*, not your account, and Telegram requires them from every
MTProto client. Keep the hash private — it belongs with your credentials, not in a public
repository.

3. Write the program
--------------------

Save this as ``hello.py``:

.. code-block:: python

    import asyncio

    from pyrogram import Client

    api_id = 12345
    api_hash = "0123456789abcdef0123456789abcdef"


    async def main():
        async with Client("my_account", api_id, api_hash) as app:
            await app.send_message("me", "Greetings from **wzgram**!")


    asyncio.run(main())

Note that you import ``pyrogram``, not ``wzgram``. That is deliberate: wzgram is a drop-in
replacement, so code written for Pyrogram runs unchanged.

Three things worth naming:

- ``"my_account"`` is the **session name**. wzgram writes ``my_account.session`` next to your
  script and reuses it, so you log in once rather than on every run.
- ``async with`` starts the client, runs your code and stops it cleanly. Without it you would
  call ``await app.start()`` and ``await app.stop()`` yourself.
- ``"me"`` is a chat id that means your own Saved Messages — a safe place to test against.

4. Run it
---------

.. code-block:: bash

    $ python3 hello.py

The first run asks for your phone number, then the code Telegram sends you, then your
two-step password if you have one. That is the login, and it happens once: the session file
holds the result.

Look in Saved Messages. The text arrives in bold, because wzgram parses Markdown by default.

5. React to messages
--------------------

Sending is half of it. To *respond* to things, register a handler and let the client run:

.. code-block:: python

    from pyrogram import Client, filters

    app = Client("my_account", api_id, api_hash)


    @app.on_message(filters.private & filters.text)
    async def echo(client, message):
        await message.reply(message.text)


    app.run()

``app.run()`` blocks: it starts the client, keeps it connected, and dispatches updates to
your handlers until you stop it with Ctrl-C. The ``filters`` argument decides which messages
reach this function — here, text messages in private chats.

6. Where to go next
-------------------

- :doc:`../start/invoking` — how method calls actually work
- :doc:`../start/updates` — handlers, groups and how updates are dispatched
- :doc:`../topics/use-filters` — narrowing what your handlers see
- :doc:`../start/examples/index` — short, complete programs
- :doc:`../features/index` — what Telegram can do, release by release

If something goes wrong, :doc:`../start/errors` explains what wzgram raises and when, and
:doc:`../topics/debugging` covers how to see the traffic.
