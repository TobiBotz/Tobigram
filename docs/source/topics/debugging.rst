Debugging
=========

When working with the API, chances are you'll stumble upon bugs, get stuck and start wondering how to continue. Nothing
to actually worry about since wzgram provides some commodities to help you in this.


-----

Caveman Debugging
-----------------

    *The most effective debugging tool is still careful thought, coupled with judiciously placed print statements.*

    -- Brian Kernighan, "Unix for Beginners" (1979)

Adding ``print()`` statements in crucial parts of your code is by far the most ancient, yet efficient technique for
debugging programs, especially considering the concurrent nature of the framework itself. wzgram goodness in this
respect comes with the fact that any object can be nicely printed just by calling ``print(obj)``, thus giving to you
an insight of all its inner details.

Consider the following code:

.. code-block:: python

    me = await app.get_users("me")
    print(me)  # User

This will show a JSON representation of the object returned by :meth:`~pyrogram.Client.get_users`, which is a
:class:`~pyrogram.types.User` instance, in this case. The output on your terminal will be something similar to this:

.. code-block:: json

    {
        "_": "User",
        "id": 123456789,
        "is_self": true,
        "is_contact": false,
        "is_mutual_contact": false,
        "is_deleted": false,
        "is_bot": false,
        "is_verified": false,
        "is_restricted": false,
        "is_support": false,
        "first_name": "wzgram",
        "photo": {
            "_": "ChatPhoto",
            "small_file_id": "AbCdE...EdCbA",
            "small_photo_unique_id": "VwXyZ...ZyXwV",
            "big_file_id": "AbCdE...EdCbA",
            "big_photo_unique_id": "VwXyZ...ZyXwV"
        }
    }

As you've probably guessed already, wzgram objects can be nested. That's how compound data are built, and nesting
keeps going until we are left with base data types only, such as ``str``, ``int``, ``bool``, etc.

Accessing Attributes
--------------------

Even though you see a JSON output, it doesn't mean we are dealing with dictionaries; in fact, all wzgram types are
fully-fledged Python objects and the correct way to access any attribute of them is by using the dot notation ``.``:

.. code-block:: python

    photo = me.photo
    print(photo)  # ChatPhoto

.. code-block:: json

    {
        "_": "ChatPhoto",
        "small_file_id": "AbCdE...EdCbA",
        "small_photo_unique_id": "VwXyZ...ZyXwV",
        "big_file_id": "AbCdE...EdCbA",
        "big_photo_unique_id": "VwXyZ...ZyXwV"
    }

Checking an Object's Type
-------------------------

Another thing worth talking about is how to tell and check for an object's type.

As you noticed already, when printing an object you'll see the special attribute ``"_"``. This is just a visual thing
useful to show humans the object type, but doesn't really exist anywhere; any attempt in accessing it will lead to an
error. The correct way to get the object type is by using the built-in function ``type()``:

.. code-block:: python

    status = me.status
    print(type(status))

.. code-block:: text

    <enum 'UserStatus'>

And to check if an object is an instance of a given class, you use the built-in function ``isinstance()``:

.. code-block:: python
    :name: this-py

    from wzgram.enums import UserStatus

    status = me.status
    print(isinstance(status, UserStatus))

.. code-block:: text

    True

.. raw:: html

    <script>
        var e = document.querySelector("blockquote p.attribution");
        var s = e.innerHTML;

        e.innerHTML = s[0] + " " + s.slice(1);
    </script>

Enabling logs
-------------

wzgram logs through the standard :py:mod:`logging` module under the ``pyrogram`` logger, so
turning it up needs no wzgram-specific setting:

.. code-block:: python

    import logging

    logging.basicConfig(level=logging.INFO)
    logging.getLogger("pyrogram").setLevel(logging.DEBUG)

``INFO`` covers connects, reconnects and session lifecycle. ``DEBUG`` adds every request and
response, which is what you want when a call behaves differently than the documentation says
— and far too much output to leave on.

Useful sub-loggers when you want less noise than a full ``DEBUG``:

.. csv-table::
    :header: Logger, What it reports
    :widths: 40 60

    ``pyrogram.session.session``, "MTProto packets, retries, flood waits, reconnects"
    ``pyrogram.connection.connection``, "which datacenter address is being tried, and why it failed"
    ``pyrogram.dispatcher``, "updates being parsed and dispatched, and queue drops"
    ``pyrogram.client``, "start and stop, plugins, file transfers"

A warning you will see in normal operation is an unknown RPC error being logged instead of
written to disk — see :doc:`/start/errors`.
