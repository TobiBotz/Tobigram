Scheduling Tasks
================

Scheduling tasks means executing one or more functions periodically at pre-defined intervals or after a delay. This is
useful, for example, to send recurring messages to specific chats or users.

This page shows how to integrate wzgram with ``apscheduler``. For more detail, see the
library's own documentation.


-----

Using apscheduler
-----------------

- Install with ``pip3 install apscheduler``
- Documentation: https://apscheduler.readthedocs.io

Asynchronously
^^^^^^^^^^^^^^

.. code-block:: python

    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    from wzgram import Client

    app = Client("my_account")


    async def job():
        await app.send_message(chat_id="me", text="Hi!")


    scheduler = AsyncIOScheduler()
    scheduler.add_job(job, "interval", seconds=3)

    scheduler.start()
    app.run()

From a background thread
^^^^^^^^^^^^^^^^^^^^^^^^

``BackgroundScheduler`` runs jobs in threads, and a wzgram method called from a thread has
no running loop to await on. Hand the coroutine to the client's loop instead:

.. code-block:: python

    import asyncio

    from apscheduler.schedulers.background import BackgroundScheduler

    from wzgram import Client

    app = Client("my_account")


    def job():
        asyncio.run_coroutine_threadsafe(
            app.send_message(chat_id="me", text="Hi!"), app.loop
        )


    scheduler = BackgroundScheduler()
    scheduler.add_job(job, "interval", seconds=3)

    scheduler.start()
    app.run()

``AsyncIOScheduler`` is the better fit whenever you can use it — it needs none of this. See
:doc:`synchronous` for the general rule about crossing a thread boundary.

Telegram-side scheduling
------------------------

For a message that should be sent at a fixed time, the server can hold it for you: every
``send_*`` method takes a ``schedule_date``, and no process has to stay running.

.. code-block:: python

    from datetime import datetime, timedelta

    await app.send_message(
        chat_id="me",
        text="Sent an hour from now",
        schedule_date=datetime.now() + timedelta(hours=1),
    )

:meth:`~pyrogram.Client.get_scheduled_messages`,
:meth:`~pyrogram.Client.send_scheduled_messages` and
:meth:`~pyrogram.Client.delete_scheduled_messages` manage what is queued.
