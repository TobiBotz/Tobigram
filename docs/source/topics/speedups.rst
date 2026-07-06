Speedups
========

wzgram's speed can be boosted up by using uvloop.


-----

WarpCrypto
----------

wzgram ships WarpCrypto_ bundled — a high-performance cryptography library written in C that
implements the cryptographic algorithms Telegram requires, namely: AES-256-IGE, AES-256-CTR
and AES-256-CBC. No additional installation is needed; wzgram uses WarpCrypto automatically.

uvloop
------

uvloop_ is a fast, drop-in replacement of the built-in asyncio event loop. uvloop is implemented in Cython and uses
libuv under the hood. It makes asyncio 2-4x faster.

Installation
^^^^^^^^^^^^

.. code-block:: bash

    $ pip3 install -U uvloop

Usage
^^^^^

Call ``uvloop.install()`` before calling ``asyncio.run()`` or ``app.run()``.

.. code-block:: python

    import asyncio
    import uvloop

    from pyrogram import Client


    async def main():
        app = Client("my_account")

        async with app:
            print(await app.get_me())


    uvloop.install()
    asyncio.run(main())

The ``uvloop.install()`` call also needs to be placed before creating a Client instance.

.. code-block:: python

    import uvloop
    from pyrogram import Client

    uvloop.install()

    app = Client("my_account")


    @app.on_message()
    async def hello(client, message):
        print(await client.get_me())


    app.run()

.. _WarpCrypto: https://github.com/rjriajul/wzgram
.. _uvloop: https://github.com/MagicStack/uvloop
