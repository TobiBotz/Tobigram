MTProxy Settings
================

Tobigram supports classic Telegram MTProto Proxies (**MTProxy**) via direct TCP connections.
This allows your client to communicate directly with Telegram's data centers through an intermediate
obfuscated proxy server, bypassing network restrictions.


-----

Usage
-----

To use Tobigram with an MTProxy, pass the proxy configuration to the *proxy* parameter in the
:obj:`~pyrogram.Client` class.

You can provide the proxy in two convenient ways:

1. Using Telegram Share Links (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can directly pass the Telegram proxy link copied from the app:

.. code-block:: python

    from pyrogram import Client

    app = Client(
        "my_account",
        proxy="tg://proxy?server=11.22.33.44&port=443&secret=ee1405e16163887494a4425d6925f2187777772e676f6f676c652e636f6d",
    )

    app.run()

Both ``tg://proxy?server=...&port=...&secret=...`` and ``https://t.me/proxy?server=...&port=...&secret=...``
are automatically detected and parsed.

2. Using a Dictionary
~~~~~~~~~~~~~~~~~~~~~

Set ``scheme="mtproxy"`` in a configuration dictionary:

.. code-block:: python

    from pyrogram import Client

    proxy = {
        "scheme": "mtproxy",
        "hostname": "11.22.33.44",
        "port": 443,
        "secret": "ee1405e16163887494a4425d6925f2187777772e676f6f676c652e636f6d",
    }

    app = Client("my_account", proxy=proxy)

    app.run()

3. Using MtProxy Dataclass
~~~~~~~~~~~~~~~~~~~~~~~~~~

For type hints and clean structure, use the :obj:`~pyrogram.connection.MtProxy` dataclass:

.. code-block:: python

    from pyrogram import Client
    from pyrogram.connection import MtProxy

    proxy = MtProxy(
        hostname="11.22.33.44",
        port=443,
        secret="ee1405e16163887494a4425d6925f2187777772e676f6f676c652e636f6d",
    )

    app = Client("my_account", proxy=proxy)

    app.run()


-----

Supported Secret Types
----------------------

Tobigram supports all standard MTProxy secret formats (in hex, base64, or base64url):

1. **Plain Secret (16 bytes)**:
   A standard 32-hex-character secret key.
   Uses the standard ``TCPAbridged`` transport.

   .. code-block:: python

       secret = "1405e16163887494a4425d6925f218"

2. **DD Secret (Random Padding, 17 bytes)**:
   A 34-hex-character secret starting with ``dd``.
   Instructs the transport to apply randomized packet padding to resist Deep Packet Inspection (DPI).
   Tobigram automatically routes this to ``TCPIntermediatePadded`` transport.

   .. code-block:: python

       secret = "dd1405e16163887494a4425d6925f218"

3. **EE Secret (Fake-TLS with SNI Domain)**:
   A secret starting with ``ee``, followed by the 16-byte secret key and the hex-encoded domain name (SNI).
   Tobigram emulates a real TLS 1.3 ClientHello / ServerHello handshake to make the connection appear
   indistinguishable from ordinary HTTPS traffic.

   .. code-block:: python

       # ee + 16-byte key + hex("www.google.com")
       secret = "ee1405e16163887494a4425d6925f2187777772e676f6f676c652e636f6d"
