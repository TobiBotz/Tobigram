conversation_bot
================

This bot asks questions and waits for the answers inline, without storing per-user state.

:meth:`Chat.ask() <pyrogram.types.Chat.ask>` sends a message and waits for the next one that
matches. The update it consumes does not reach your handlers, so the answer to a question
cannot re-trigger the command that asked it.

.. include:: /_includes/usable-by/users-bots.rst

.. code-block:: python

    from wzgram import Client, filters
    from wzgram.errors import ListenerTimeout

    app = Client("my_bot")


    @app.on_message(filters.command("register") & filters.private)
    async def register(client, message):
        try:
            name = await message.chat.ask("What should I call you?", timeout=60)
            age = await message.chat.ask(
                "How old are you?",
                filters=filters.text,
                timeout=60,
            )
        except ListenerTimeout:
            await message.reply("Took too long — send /register again when you're ready.")
            return

        if not age.text.isdigit():
            await age.reply("That wasn't a number. Start over with /register.")
            return

        await age.reply(f"Registered {name.text}, age {age.text}.")


    app.run()

Each wait has its own ``timeout``, and a listener that expires raises ``ListenerTimeout``
rather than leaving the conversation hanging. Waiting inside a handler is safe: wzgram covers
the parked dispatcher worker with a relief worker, so concurrent conversations do not starve
the pool.

See :doc:`/features/listeners`.
