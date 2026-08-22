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

wzgram ships four kinds of storage engine. Two keep the session on the machine that is
running — a **File Storage** and a **Memory Storage**, both backed by SQLite — and two keep
it somewhere that outlives the machine: a **Remote Storage** (MongoDB or Redis) and a
**Hybrid Storage**, which is a local cache in front of a remote one.

Start with File Storage. Reach for the others when the host is ephemeral, or when several
deployments need to look at the same sessions.

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

Remote Storage
--------------

A file on disk is the wrong place for a session when the host is replaced on every deploy.
:obj:`~pyrogram.storage.MongoStorage` and :obj:`~pyrogram.storage.RedisStorage` keep it in a
database instead, so a container that restarts resumes with its peers already warm.

Drivers are optional and imported only when the storage is opened:

.. code-block:: bash

    $ pip install "wzgram[mongo]"      # motor
    $ pip install "wzgram[redis]"      # redis

.. code-block:: python

    from pyrogram import Client
    from pyrogram.storage import MongoStorage

    app = Client(
        "my_account",
        api_id=api_id, api_hash=api_hash,
        storage_engine=MongoStorage("my_account", "mongodb://localhost:27017"),
    )

    app.run()

Both engines take either a connection URI, which they own and close, or an
already-created client to share with the rest of your program:

.. code-block:: python

    from motor.motor_asyncio import AsyncIOMotorClient
    from pyrogram.storage import MongoStorage, RedisStorage

    MongoStorage("my_account", AsyncIOMotorClient(uri), database="sessions")
    RedisStorage("my_account", redis_client, prefix="bots:my_account")

.. warning::

    In Redis, an evicted session key is a lost login. Peers are a cache and can be evicted
    safely, but the session hash cannot — run the database with
    ``maxmemory-policy noeviction``, or give wzgram a database of its own. Opening the
    storage logs a warning when the server reports any other policy.

Coming from pyrofork's MongoStorage? Its documents carry no ``server_address`` or ``port``.
:meth:`MongoStorage.import_pyrofork() <pyrogram.storage.MongoStorage.import_pyrofork>` reads
that layout once and writes wzgram's, resolving the address from the datacenter id.

Hybrid Storage
--------------

A remote database is durable, but it is also a network round trip, and ``resolve_peer`` runs
on every single send. :obj:`~pyrogram.storage.HybridStorage` puts a local SQLite cache in
front of any backend:

.. code-block:: python

    from pyrogram import Client
    from pyrogram.storage import HybridStorage, MongoStorage

    app = Client(
        "my_account",
        storage_engine=HybridStorage(
            "my_account",
            backend=MongoStorage("my_account", "mongodb://localhost:27017"),
        ),
    )

    app.run()

What it does:

- **Reads are local.** On ``open()`` the backend is copied into the cache; after that every
  peer lookup and every session attribute is answered without touching the network.
- **Writes are mirrored in the background.** They land in the cache immediately and reach the
  backend through a bounded queue drained by a background task, coalesced by key.
- **A remote outage is not a client outage.** A failed write is retried with backoff and
  logged; reads keep working and the client keeps running.
- **Under pressure, the right writes survive.** When the queue is full, peer writes are
  dropped oldest-first — losing one costs a single lookup. Session attributes and update
  state are never dropped: losing those costs the login, or restarts gap recovery from a
  stale pts.

The trade-off is honest and worth stating: the last writes live only in the cache until the
writer drains. ``close()`` flushes them, bounded by ``flush_timeout``; a SIGKILL does not.

Pass ``cache_in_memory=False`` to keep the cache in a file, which survives a restart and
skips the bulk load on open.

Writing your own engine
-----------------------

Subclass :obj:`~pyrogram.storage.RemoteStorage` rather than
:obj:`~pyrogram.storage.Storage`: it implements the whole contract on top of a handful of
primitives, and it brings the two caches that keep the hot path off the network.

.. csv-table::
    :header: Primitive, What it does
    :widths: 40 60

    "``_connect()`` / ``_disconnect()``", "open and close the driver"
    "``_load_session()``", "the session as a dict, or None if there is none yet"
    "``_save_session(fields)``", "upsert those fields"
    "``_upsert_peers(rows)``", "``(id, access_hash, type, phone_number)`` tuples"
    "``_fetch_peer(peer_id)``", "``(id, access_hash, type, last_update_on)`` or None"
    "``_fetch_peer_by_username(username)``", "same shape"
    "``_fetch_peer_by_phone(number)``", "same shape"
    "``_replace_usernames(rows)``", "delete-then-insert per peer id"
    "``_load_states()`` / ``_save_state(t)`` / ``_delete_state(id)``", "update state"
    "``_purge(remove_peers)``", "what ``delete()`` does"

Three rules the base already follows, and a hand-written engine has to keep:

-   **Session attributes are read once**, then served from memory. ``dc_id()`` runs on every
    send; it must not be a round trip.
-   **``update_peers`` skips peers whose access hash has not changed.** Every ``invoke``
    feeds ``r.users`` and ``r.chats`` back through ``fetch_peers``, so without that filter
    the same unchanged peers are rewritten on every RPC.
-   **The username TTL is enforced on read**, not by an expiry feature of the store. A
    backend that drops the row itself would disagree with what SQLite does with a stale one.

Version your layout with a ``VERSION`` constant and implement ``_load_version`` /
``_save_version`` / ``_migrate``, so a change of shape can migrate rather than corrupt.

Reusing a Telethon session
^^^^^^^^^^^^^^^^^^^^^^^^^^

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
