Guest Mode and Managed Bots
===========================

*Bot API 9.6 and 10.0 — April and May 2026*

Two changes to how a bot exists in a chat. **Guest mode** lets a bot answer in a group it is
not a member of. **Managed bots** let a user create and own a bot through another bot,
without going near BotFather.


-----

Guest mode
----------

Normally a bot must be added to a group before it sees anything. In guest mode a member can
summon it for a single question: the bot receives that message, answers it, and stays out.

.. code-block:: python

    @app.on_guest_message()
    async def guest(client, message):
        print(message.text, message.guest_query_id)

The update carries a ``guest_query_id``, and that id — not a chat id — is what the answer is
addressed to:

.. code-block:: python

    from wzgram.types import InlineQueryResultArticle, InputTextMessageContent

    @app.on_guest_message()
    async def guest(client, message):
        await client.answer_guest_query(
            message.guest_query_id,
            InlineQueryResultArticle(
                title="Layer",
                input_message_content=InputTextMessageContent("Currently layer 229."),
            ),
        )

The reply is a single :obj:`~pyrogram.types.InlineQueryResult`, the same shape an inline
query takes, because the bot is producing one result rather than joining a conversation.

A guest update also carries the messages the user quoted when summoning the bot. wzgram
parses those first, so the peers and messages they refer to are already known by the time
your handler runs, even though the bot never saw the chat's history.

Managed bots
------------

A managed bot is one created programmatically and owned by a user. When one is created,
its manager is told:

.. code-block:: python

    @app.on_managed_bot()
    async def created(client, updated):
        print(f"{updated.user.first_name} now owns @{updated.bot.username}")

:obj:`~pyrogram.types.ManagedBotUpdated` is deliberately small: ``user`` is the owner, ``bot``
is the bot. Everything else you do with it goes through the ordinary bot methods.

Gotchas
-------

- A guest message is not an ordinary message: it reaches
  :meth:`~pyrogram.Client.on_guest_message` and never
  :meth:`~pyrogram.Client.on_message`. Registering only the latter means seeing nothing.
- ``guest_query_id`` expires. Answer inside the handler; there is no chat to come back to
  later.
- Guest mode does not grant history. The bot sees the message it was summoned for and the
  messages quoted with it, nothing else.
