Synchronous Usage
=================

wzgram is asynchronous. Every API method is a coroutine, and there is no synchronous mode:
calling ``app.send_message(...)`` without awaiting it returns a coroutine object and sends
nothing.

.. warning::

    Older Pyrogram versions shipped a compatibility layer that wrapped every method so it
    could be called without ``await`` — ``with app:`` instead of ``async with app:``. wzgram
    does not have it. Code relying on it fails quietly: the coroutine is created, never
    scheduled, and Python warns that it was never awaited.

What to write instead is below, and none of it is more code than the sync form was.


-----

A script that does one thing
----------------------------

:py:func:`asyncio.run` is the whole bridge. It starts an event loop, runs your coroutine and
shuts the loop down:

.. code-block:: python

    import asyncio

    from wzgram import Client


    async def main():
        async with Client("my_account") as app:
            await app.send_message("me", "Hi!")


    asyncio.run(main())

A program that stays running
----------------------------

:meth:`~pyrogram.Client.run` does the same thing for you and then blocks, keeping the client
online until you stop it:

.. code-block:: python

    from wzgram import Client, filters

    app = Client("my_account")


    @app.on_message(filters.private)
    async def echo(client, message):
        await message.reply(message.text)


    app.run()

:meth:`~pyrogram.Client.run` also accepts a coroutine, which covers the one-shot case without
writing the ``asyncio.run`` yourself:

.. code-block:: python

    app = Client("my_account")


    async def main():
        async with app:
            await app.send_message("me", "Hi!")


    app.run(main())

Calling from synchronous code
-----------------------------

When wzgram has to live inside something that is not async — a Django view, a Flask route, a
worker in a thread pool — run the client in its own loop and hand work to it:

.. code-block:: python

    import asyncio
    import threading

    from wzgram import Client

    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever, daemon=True).start()

    app = Client("my_account")
    asyncio.run_coroutine_threadsafe(app.start(), loop).result()


    def send(chat_id, text):
        """Callable from ordinary synchronous code."""
        future = asyncio.run_coroutine_threadsafe(
            app.send_message(chat_id, text), loop
        )
        return future.result(timeout=30)

:py:func:`asyncio.run_coroutine_threadsafe` is the supported way across a thread boundary.
Do not call :py:func:`asyncio.run` per request — each call builds and tears down a loop, and
the client belongs to the loop it was started on.

Blocking calls inside handlers
------------------------------

A handler that blocks — a synchronous HTTP request, a heavy computation, ``time.sleep`` —
stops the event loop, and with it every other handler, the ping worker and the receive loop.
Push that work to a thread:

.. code-block:: python

    @app.on_message()
    async def handler(client, message):
        result = await asyncio.to_thread(expensive_blocking_call, message.text)
        await message.reply(result)

This is the same reason wzgram runs crypto above ``WZGRAM_INLINE_CRYPTO_MAX`` in a thread
pool — see :doc:`/features/performance`.
