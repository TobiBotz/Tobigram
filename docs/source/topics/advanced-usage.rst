Advanced Usage
==============

wzgram's API -- which consists of well documented :doc:`methods <../api/methods/index>` and
:doc:`types <../api/types/index>` -- exists to provide an easier interface to the more complex Telegram API.

In this section, you'll be shown the alternative way of communicating with Telegram using wzgram: the main "raw"
Telegram API with its functions and types.


-----

Telegram Raw API
----------------

If you can't find a high-level method for your needs or if you want complete, low-level access to the whole
Telegram API, you have to use the raw :mod:`~pyrogram.raw.functions` and :mod:`~pyrogram.raw.types`. Both are generated
from the TL schema, so they always match the layer wzgram was built against; the names come
straight from `Telegram's own schema <https://core.telegram.org/methods>`_.

As already hinted, raw functions and types can be less convenient. This section will therefore explain some pitfalls to
take into consideration when working with the raw API.

.. tip::

    Every available high-level method in wzgram is built on top of these raw functions.

Invoking Functions
------------------

Unlike the :doc:`methods <../api/methods/index>` found in wzgram's API, which can be called in the usual simple way,
functions to be invoked from the raw Telegram API have a different way of usage.

First of all, both :mod:`raw functions <pyrogram.raw.functions>` and :mod:`raw types <pyrogram.raw.types>`
live in their respective packages (and sub-packages): ``pyrogram.raw.functions``, ``pyrogram.raw.types``. They all exist
as Python classes, meaning you need to create an instance of each every time you need them and fill them in with the
correct values using named arguments.

Next, to actually invoke the raw function you have to use the :meth:`~pyrogram.Client.invoke` method provided by the
Client class and pass the function object you created.

Here's some examples:

-   Update first name, last name and bio:

    .. code-block:: python

        from pyrogram import Client
        from pyrogram.raw import functions

        async with Client("my_account") as app:
            await app.invoke(
                functions.account.UpdateProfile(
                    first_name="First Name", last_name="Last Name",
                    about="New bio text"
                )
            )

-   Set online/offline status:

    .. code-block:: python

        from pyrogram import Client
        from pyrogram.raw import functions, types

        async with Client("my_account") as app:
            # Set online status
            await app.invoke(functions.account.UpdateStatus(offline=False))

            # Set offline status
            await app.invoke(functions.account.UpdateStatus(offline=True))

-   Get chat info:

    .. code-block:: python

        from pyrogram import Client
        from pyrogram.raw import functions, types

        async with Client("my_account") as app:
            r = await app.invoke(
                functions.channels.GetFullChannel(
                    channel=await app.resolve_peer("username")
                )
            )

            print(r)

Chat IDs
--------

The way Telegram works makes it not possible to directly send a message to a user or a chat by using their IDs only.
Instead, a pair of ``id`` and ``access_hash`` wrapped in a so called ``InputPeer`` is always needed. wzgram allows
sending messages with IDs only thanks to cached access hashes.

There are three different InputPeer types, one for each kind of Telegram entity.
Whenever an InputPeer is needed you must pass one of these:

- :class:`~pyrogram.raw.types.InputPeerUser` - Users
- :class:`~pyrogram.raw.types.InputPeerChat` -  Basic Chats
- :class:`~pyrogram.raw.types.InputPeerChannel` - Channels & Supergroups

But you don't necessarily have to manually instantiate each object because wzgram already provides
:meth:`~pyrogram.Client.resolve_peer` as a convenience utility method that returns the correct InputPeer
by accepting a peer ID only.

Another thing to take into consideration about chat IDs is the way they are represented: they are all integers and
all positive within their respective raw types.

Things are different when working with wzgram's API because having them in the same space could lead to
collisions, and that's why wzgram uses a slightly different representation for each kind of ID.

For example, given the ID *123456789*, here's how wzgram can tell entities apart:

- ``+ID`` User: *123456789*
- ``-ID`` Chat: *-123456789*
- ``-100ID`` Channel or Supergroup: *-100123456789*

So, every time you take a raw ID, make sure to translate it into the correct ID when you want to use it with an
high-level method.

.. note::

    The raw API tracks the TL layer, and a layer bump can change a field's *type*, not only
    add fields. Code that builds raw objects by hand is what breaks on an upgrade — the
    high-level methods are updated for you.

.. _Community: https://t.me/wzgram