Storage Engines
===============

SQLite Storage
--------------

The default storage engine. Sessions are stored in a SQLite database file.

.. code-block:: python

    app = Client("my_account")
    # Creates my_account.session

Memory Storage
--------------

Keeps the session in memory only. Useful for ephemeral or bot scenarios.

.. code-block:: python

    from pyrogram.storage import MemoryStorage

    app = Client("my_account", storage=MemoryStorage())

File Storage
------------

The legacy storage format. Sessions are stored in a plain ``.session`` file.

.. code-block:: python

    from pyrogram.storage import FileStorage

    app = Client("my_account", storage=FileStorage("my_account"))
