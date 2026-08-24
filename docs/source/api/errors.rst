Errors
======

Every error wzgram raises lives in ``pyrogram.errors``. They fall into three families: RPC
errors that Telegram sent back, listener errors from :meth:`~pyrogram.Client.listen`, and
low-level protocol errors from the MTProto session.

.. code-block:: python

    from wzgram.errors import FloodWait, RPCError

    try:
        await app.send_message("me", "Hi")
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except RPCError as e:
        print(e.ID, e.CODE, e.MESSAGE)

See :doc:`/start/errors` for the guide; this page is the hierarchy.


-----

RPC errors
----------

``RPCError`` is the base of everything Telegram can answer with. Below it sits one class per
HTTP-like status code, and below those, one class per specific error string:

.. code-block:: text

    RPCError
    ├── SeeOther            (303)  the request belongs on another datacenter
    ├── BadRequest          (400)  malformed or invalid request
    ├── Forbidden           (403)  not allowed
    ├── NotAcceptable       (406)  refused, usually needing user action
    ├── Flood               (420)  rate limited — FloodWait lives here
    ├── InternalServerError (500)  Telegram's problem, retry
    └── ServiceUnavailable  (503)  Telegram is down or overloaded

Catching a category catches every specific error under it, including ones wzgram does not
know about yet.

Each instance carries:

.. csv-table::
    :header: Attribute, Meaning
    :widths: 20 80

    ``ID``, "the error string, e.g. ``FLOOD_WAIT_X``"
    ``CODE``, "the numeric code, e.g. ``420``"
    ``NAME``, "the error name Telegram sent"
    ``MESSAGE``, "a human-readable description"
    ``value``, "the number embedded in the error, when there is one"

``FloodWait.value`` is the number of seconds to wait; on a ``SeeOther`` it is the datacenter
to migrate to.

An error code the schema does not know raises the nearest category with ``UnknownError``
semantics and logs a warning naming the raw function that caused it.

Listener errors
---------------

Raised by :meth:`~pyrogram.Client.listen`, :meth:`~pyrogram.Client.ask` and the
``wait_for_*`` helpers — see :doc:`/features/listeners`.

.. code-block:: text

    ListenerError
    ├── ListenerTimeout        nobody answered in time; retrying is reasonable
    ├── ListenerStopped        the wait was cancelled or the client is stopping
    └── ListenerLimitReached   the process-wide listener budget is exhausted

The distinction matters: ``except ListenerTimeout: retry`` is correct, while retrying a
``ListenerStopped`` spins against a client that is shutting down.

Protocol errors
---------------

Raised from the MTProto session rather than by Telegram's application layer. You rarely
catch these; they show up in logs when a connection misbehaves.

.. csv-table::
    :header: Error, Raised when
    :widths: 30 70

    ``BadMsgNotification``, "the server rejected a message id or salt"
    ``SecurityError``, "a security check failed"
    ``SecurityCheckMismatch``, "a decrypted packet did not match what was expected"
    ``ReplayedMsgId``, "a message id was seen twice"
    ``CDNFileHashMismatch``, "a CDN chunk failed its hash check"

Two ordinary Python errors are also load-bearing here, and the difference is deliberate:

-   ``ConnectionResetError`` — the connection dropped while a request was in flight. wzgram
    re-sends it on the new connection.
-   ``TimeoutError`` — the request really did time out. It is never used for a dropped
    connection, so "Request timed out" keeps meaning what it says.
