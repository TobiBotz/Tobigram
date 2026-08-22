Storage Engines
===============

Every time you login to Telegram, some personal piece of data are created and held by both parties (the client, wzgram
and the server, Telegram). This session data is uniquely bound to your own account, indefinitely (until you logout or
decide to manually terminate it) and is used to authorize a client to execute API calls on behalf of your identity.


-----

Persisting Sessions
-------------------

In order to make a client reconnect successfully between restarts, that is, without having to start a new
authorization process from scratch each time, wzgram needs to store the generated session data somewhere.

Different Storage Engines
-------------------------

wzgram offers two different types of storage engines: a **File Storage** and a **Memory Storage**.
These engines are well integrated in the framework and require a minimal effort to set up. Here's how they work:

File Storage
^^^^^^^^^^^^

This is the most common storage engine. It is implemented by using **SQLite**, which will store the session details.
The database will be saved to disk as a single portable file and is designed to efficiently store and retrieve
data whenever they are needed.

To use this type of engine, simply pass any name of your choice to the ``name`` parameter of the
:obj:`~pyrogram.Client` constructor, as usual:

.. code-block:: python

    from pyrogram import Client

    async with Client("my_account") as app:
        print(await app.get_me())

Once you successfully log in (either with a user or a bot identity), a session file will be created and saved to disk as
``my_account.session``. Any subsequent client restart will make wzgram search for a file named that way and the
session database will be automatically loaded.

Memory Storage
^^^^^^^^^^^^^^

In case you don't want to have any session file saved to disk, you can use an in-memory storage by passing True to the
``in_memory`` parameter of the :obj:`~pyrogram.Client` constructor:

.. code-block:: python

    from pyrogram import Client

    async with Client("my_account", in_memory=True) as app:
        print(await app.get_me())

This storage engine is still backed by SQLite, but the database exists purely in memory. This means that, once you stop
a client, the entire database is discarded and the session details used for logging in again will be lost forever.

Session Strings
---------------

In case you want to use an in-memory storage, but also want to keep access to the session you created, call
:meth:`~pyrogram.Client.export_session_string` anytime before stopping the client...

.. code-block:: python

    from pyrogram import Client

    async with Client("my_account", in_memory=True) as app:
        print(await app.export_session_string())

...and save the resulting string. You can use this string by passing it as Client argument the next time you want to
login using the same session; the storage used will still be in-memory:

.. code-block:: python

    from pyrogram import Client

    session_string = "...ZnUIFD8jsjXTb8g_vpxx48k1zkov9sapD-tzjz-S4WZv70M..."

    async with Client("my_account", session_string=session_string) as app:
        print(await app.get_me())

Session strings are useful when you want to run authorized wzgram clients on platforms whose ephemeral filesystems
make a file-based storage engine impractical.

wzgram's strings start with ``WZ_`` and carry a CRC32, so a string mangled in transit is
told apart from one that is merely in an older format, and every format wzgram has ever
exported still decodes. :doc:`/features/session-strings` covers the format, the repair pass
and what a string is safe to be stored in.

.. warning::

    A session string is a live login. Anyone holding it is you, with no second factor in the
    way. Keep it out of version control, and revoke it by terminating the session from a
    logged-in client rather than by deleting the string.

Custom Storages
---------------

:obj:`~pyrogram.storage.Storage` is the abstract base every engine implements. Pass an
instance of your own subclass as the ``storage_engine`` argument of :obj:`~pyrogram.Client`
and wzgram will keep the session wherever you decide.

Writing one
^^^^^^^^^^^

Subclass :obj:`~pyrogram.storage.Storage` and implement its interface, then pass an instance
as ``storage_engine``. The built-in ``SQLiteStorage`` is already async — it runs on
``aiosqlite``, a core dependency — so a custom engine is for putting the session somewhere
else entirely: Redis, Postgres, a secrets manager, a row in an existing table.

Two things a custom engine has to get right, because the built-in one does:

-   ``SQLiteStorage.VERSION`` is a schema version. If your engine persists a schema of its
    own, version it too and migrate on open.
-   Writes should be batched but bounded **by time as well as by count**. A write left in an
    open transaction until the batch fills is lost when the process is killed, and the
    update state among them is what stops gap recovery restarting from a stale pts.

Example of Telethon Storage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To reuse a Telethon session (the two formats are not compatible on their own), there is a
community `storage engine <https://gist.github.com/KurimuzonAkuma/3991606c259facef95d0c8afb676bd85>`_
that reads and writes Telethon's layout, so the same session file stays usable from both
libraries.

.. code-block:: python

    from pyrogram import Client
    from .tele_storage import TelethonStorage  # assumes that the path downloaded is accurate

    workdir = Path(__file__).parent
    test_mode = False
    is_bot = False # Pass True if your session is bot session

    async with Client(
        "my_account",
        api_id=api_id,
        api_hash=api_hash,
        lang_code="ru",
        workdir=workdir,
        test_mode=test_mode,
        storage_engine=TelethonStorage(
            name="my_account",
            workdir=workdir,
            api_id=api_id,
            test_mode=test_mode,
            is_bot=is_bot
        )
    ) as app:
        await app.send_message(chat_id="me", text="Greetings from **wzgram**!")
