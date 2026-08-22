Error Handling
==============

Errors can be correctly handled with ``try...except`` blocks in order to control the behaviour of your application.
wzgram errors all live inside the ``errors`` package:

.. code-block:: python

    from pyrogram import errors


-----

RPCError
--------

The father of all errors is named ``RPCError`` and is able to catch all Telegram API related errors.
This error is raised every time a method call against Telegram's API was unsuccessful.

.. code-block:: python

    from pyrogram.errors import RPCError

.. warning::

    Avoid catching this error everywhere, especially when no feedback is given (i.e. by logging/printing the full error
    traceback), because it makes it impossible to understand what went wrong.

Error Categories
----------------

The ``RPCError`` packs together all the possible errors Telegram could raise, but to make things tidier, wzgram
provides categories of errors, which are named after the common HTTP errors and are subclass-ed from the ``RPCError``:

.. code-block:: python

    from pyrogram.errors import BadRequest, Forbidden, ...

-   ``303 - SeeOther``
-   ``400 - BadRequest``
-   ``401 - Unauthorized``
-   ``403 - Forbidden``
-   ``406 - NotAcceptable``
-   ``420 - Flood``
-   ``500 - InternalServerError``

Single Errors
-------------

For a fine-grained control over every single error, wzgram does also expose errors that deal each with a specific
issue. For example:

.. code-block:: python

    from pyrogram.errors import FloodWait

These errors subclass directly from the category of errors they belong to, which in turn subclass from the father
``RPCError``, thus building a class of error hierarchy such as this:

- RPCError
    - BadRequest
        - ``MessageEmpty``
        - ``UsernameOccupied``
        - ``...``
    - InternalServerError
        - ``RpcCallFail``
        - ``InterDcCallError``
        - ``...``
    - ``...``

.. _Errors: api/errors

Unknown Errors
--------------

In case wzgram does not know anything about a specific error yet, it raises a generic error from its known category,
for example, an unknown error with error code ``400``, will be raised as a ``BadRequest``. This way you can catch the
whole category of errors and be sure to also handle these unknown errors.

.. admonition :: RPC Errors
    :class: tip

    There is no official list of every RPC error Telegram can return, so the list of known
    errors is maintained on a best-effort basis. When new methods appear, the list may lag
    behind simply because nobody knows yet what they can raise.

    An unknown error is logged at ``warning`` level, with the error string and the raw
    function that caused it:

    .. code-block:: text

        Unknown RPC error [420 SOME_NEW_ERROR] caused by messages.SendMessage

    Earlier versions wrote these to an ``unknown_errors.txt`` file in the working directory.
    They no longer do: the write was unbounded, it blocked the event loop from inside an
    exception constructor, and on a read-only filesystem the resulting ``OSError`` replaced
    the RPC error being raised. Capture them from logging instead.

Errors with Values
------------------

Exception objects may also contain some informative values. For example, ``FloodWait`` holds the amount of seconds you
have to wait before you can try again, some other errors contain the DC number on which the request must be repeated on.
The value is stored in the ``value`` attribute of the exception object:

.. code-block:: python

    import asyncio
    from pyrogram.errors import FloodWait

    ...
        try:
            ...  # Your code
        except FloodWait as e:
            await asyncio.sleep(e.value)  # Wait N seconds before continuing
    ...