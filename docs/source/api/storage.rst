Storage
=======

A storage engine holds everything a client needs to resume a session: the datacenter and
auth key, the peer cache, the usernames, and the update state. :obj:`~pyrogram.Client` takes
one through its ``storage_engine`` argument, and defaults to a SQLite file next to your
script.

:doc:`/topics/storage-engines` is the guide — which engine to pick, what the hybrid one
trades away, and how to write your own. This page is the reference.


-----

Local
-----

.. autoclass:: pyrogram.storage.SQLiteStorage()
.. autoclass:: pyrogram.storage.FileStorage()
.. autoclass:: pyrogram.storage.MemoryStorage()

Remote
------

.. autoclass:: pyrogram.storage.RemoteStorage()
.. autoclass:: pyrogram.storage.MongoStorage()
.. autoclass:: pyrogram.storage.RedisStorage()

Hybrid
------

.. autoclass:: pyrogram.storage.HybridStorage()

Base class
----------

.. autoclass:: pyrogram.storage.Storage()
