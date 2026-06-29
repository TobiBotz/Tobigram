More on Updates
===============

Handlers
--------

Handlers are functions that process specific types of updates. Register them
using the ``@on_`` decorator pattern:

.. code-block:: python

    @app.on_message(filters.private)
    async def my_handler(client, message):
        await message.reply("Got a private message!")

Available handlers include:

* :class:`~pyrogram.handlers.MessageHandler`
* :class:`~pyrogram.handlers.CallbackQueryHandler`
* :class:`~pyrogram.handlers.InlineQueryHandler`
* :class:`~pyrogram.handlers.ChatMemberUpdatedHandler`
* :class:`~pyrogram.handlers.UserStatusHandler`
* :class:`~pyrogram.handlers.DisconnectHandler`
* :class:`~pyrogram.handlers.StoryHandler`

Filters
-------

Filters let you control which updates a handler receives:

.. code-block:: python

    @app.on_message(filters.text & filters.private)
    async def text_in_private(client, message):
        await message.reply(f"You said: {message.text}")

Common filters:

* ``filters.text``, ``filters.photo``, ``filters.video``, ``filters.audio``
* ``filters.private``, ``filters.group``, ``filters.channel``
* ``filters.command("start")``, ``filters.regex("pattern")``
* ``filters.me``, ``filters.bot``
* ``filters.group``, ``filters.forwarded``, ``filters.sticker``

Combine filters with ``&`` (and), ``|`` (or), and ``~`` (not).

Grouping
--------

Handlers can be grouped to control execution order:

.. code-block:: python

    @app.on_message(filters.text, group=1)
    async def first(client, message):
        print("Runs first")

    @app.on_message(filters.text, group=2)
    async def second(client, message):
        print("Runs second")

Stop Propagation
----------------

Stop a handler chain with :class:`~pyrogram.StopPropagation`:

.. code-block:: python

    from pyrogram import StopPropagation

    @app.on_message(filters.command("start"))
    async def start(client, message):
        await message.reply("Start!")
        raise StopPropagation
