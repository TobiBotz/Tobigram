Direct Messages in Channels
===========================

*Bot API 9.2 — August 2025*

A channel can open a **direct messages** tab: a place where readers write to the channel and
the admins answer. Each reader gets their own thread, called a direct messages topic, so the
admins see one conversation per person instead of one flat feed.

It is the channel-side counterpart of a support inbox, and it is also the channel where
:doc:`suggested-posts` are proposed.


-----

Listing the topics
------------------

.. code-block:: python

    async for topic in app.get_direct_messages_topics(channel_id):
        print(topic.id, topic.user.first_name, topic.unread_count)

Each :obj:`~pyrogram.types.DirectMessagesTopic` carries who is on the other side (``user``),
the unread counters and ``last_message``. :meth:`~pyrogram.Client.get_direct_messages_topics_by_id`
fetches specific ones when you already have their ids.

Reading a conversation
----------------------

:meth:`~pyrogram.Client.get_direct_messages_chat_topic_history` walks one topic the way
:meth:`~pyrogram.Client.get_chat_history` walks a chat:

.. code-block:: python

    async for message in app.get_direct_messages_chat_topic_history(channel_id, topic_id):
        print(message.from_user.first_name, message.text)

Pass ``reverse=True`` to read oldest-first, and ``offset_id`` / ``offset_date`` to resume
where you stopped.

:meth:`~pyrogram.Client.delete_direct_messages_chat_topic_history` clears one thread without
touching the others.

Replying into a topic
---------------------

Send methods take ``direct_messages_topic_id``, which is what puts your reply in the right
thread:

.. code-block:: python

    await app.send_message(
        chat_id=channel_id,
        text="Thanks for writing in!",
        direct_messages_topic_id=topic_id,
    )

Leaving it out sends to the channel's general direct messages area, which is rarely what you
want when you are answering somebody.

Gotchas
-------

- ``direct_messages_topic_id`` and ``message_thread_id`` are different parameters for
  different things: the first is a per-user thread in a channel's direct messages, the
  second is a forum topic in a supergroup. See :doc:`chat-topics-drafts`.
- ``can_send_unpaid_messages`` on the topic tells you whether that user may write without
  paying. A channel charging for messages will reject an unpaid reply chain.
- Reading topics is a user-session method. A bot administering the channel works through the
  ordinary message updates instead.
