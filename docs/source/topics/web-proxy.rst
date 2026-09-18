Web Proxy Settings
==================

Tobigram supports Telegram MTProto **Web Proxies** (``scheme="web"``).
A Web Proxy establishes an encrypted WebSocket connection over HTTPS (port 443) using TLS 1.3
to reach an intermediate relay that communicates with Telegram data centers.
This is ideal for restrictive firewall environments where direct MTProxy or standard ports are blocked.


-----

Usage
-----

To use Tobigram with a Web Proxy, pass the proxy configuration to the *proxy* parameter in the
:obj:`~pyrogram.Client` class.

You can provide the proxy in two convenient ways:

1. Using Telegram Web Proxy Links (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can pass a ``tg://webproxy?...`` share link directly:

.. code-block:: python

    from pyrogram import Client

    app = Client(
        "my_account",
        proxy="tg://webproxy?server=relay.example.com&port=443&secret=dd1405e16163887494a4425d6925f218",
    )

    app.run()

Both ``tg://webproxy?server=...&secret=...`` and ``https://t.me/webproxy?server=...&secret=...``
are automatically detected and parsed.

2. Using a Dictionary
~~~~~~~~~~~~~~~~~~~~~

Set ``scheme="web"`` in a configuration dictionary:

.. code-block:: python

    from pyrogram import Client

    proxy = {
        "scheme": "web",
        "hostname": "relay.example.com",
        "secret": "dd1405e16163887494a4425d6925f218",
    }

    app = Client("my_account", proxy=proxy)

    app.run()

.. note::

    The port for a Web Proxy is always ``443`` (HTTPS) and can be omitted in the dictionary.

3. Using WebProxy Dataclass
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For type hints and clean structure, use the :obj:`~pyrogram.connection.WebProxy` dataclass:

.. code-block:: python

    from pyrogram import Client
    from pyrogram.connection import WebProxy

    proxy = WebProxy(
        hostname="relay.example.com",
        secret="dd1405e16163887494a4425d6925f218",
    )

    app = Client("my_account", proxy=proxy)

    app.run()


-----

Secret Format
-------------

Web Proxies use a 16-byte plain secret or a 17-byte ``dd``-prefixed secret (in hex, base64, or base64url).
Fake-TLS (``ee``) secrets are not supported for the Web Proxy scheme because the connection is already
a genuine TLS 1.3 connection to the relay hostname.
