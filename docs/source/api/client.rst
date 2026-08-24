Client
======

:obj:`~pyrogram.Client` is the entry point of the library. One instance is one Telegram
session: it owns the connection, the storage, the update dispatcher and every API method.

.. code-block:: python

    from wzgram import Client

    async with Client("my_account", api_id, api_hash) as app:
        await app.send_message("me", "Hi!")

Its methods are listed in :doc:`methods/index`, grouped by what they do. This page documents
the class itself and the arguments it accepts; :doc:`/topics/client-settings` explains which
of them are worth changing and why.


-----

.. autoclass:: pyrogram.Client()
