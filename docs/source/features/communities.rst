Communities
===========

*Bot API 10.2 — July 2026*

A community is a bundle of chats presented as one thing. Instead of a group, an announcement
channel and three topic groups sitting apart in the chat list, they appear as a single entry
that opens into its member chats.

The chats keep their own ids, permissions and histories. The community is the wrapper.


-----

Recognising one
---------------

A chat that belongs to a community carries it:

.. code-block:: python

    chat = await app.get_chat("some_chat")

    if chat.community:
        print(chat.community.id, chat.community.title, chat.community.is_collapsed)

:obj:`~pyrogram.types.Community` is small on purpose — ``id``, ``title``, ``date`` and the
flags ``is_creator``, ``is_left``, ``is_min`` and ``is_collapsed``. Everything you do with a
chat inside a community is still done against that chat.

:obj:`~pyrogram.enums.ChatType` also gained a ``COMMUNITY`` member, so a dialog list can be
filtered on it directly.

Membership changes
------------------

When a chat joins or leaves a community, a service message says so:

.. code-block:: python

    @app.on_message()
    async def watch(client, message):
        if message.community_chat_added:
            print(f"added to community {message.community_chat_added.community_id}")

        if message.community_chat_removed:
            print(f"removed from community {message.community_chat_removed.community_id}")

Both :obj:`~pyrogram.types.CommunityChatAdded` and
:obj:`~pyrogram.types.CommunityChatRemoved` carry ``community_id`` and, when it is known,
the community's ``community`` chat.

Searching inside one
--------------------

:meth:`~pyrogram.Client.search_global` takes a ``community``, which narrows a global search
to the chats that community holds:

.. code-block:: python

    async for message in app.search_global("changelog", community=community_id):
        print(message.chat.title, message.text)

:meth:`~pyrogram.Client.search_global_count` takes the same argument for a count without the
messages.

Gotchas
-------

- ``is_collapsed`` is a presentation flag on your own client — whether the community shows
  as one row or expanded into its chats. It says nothing about the community itself.
- ``is_min`` means the object came from a context that only carried a partial community.
  Fetch the chat properly before relying on fields beyond the id and title.
- There is no "send to a community". Messages go to one of its chats.
