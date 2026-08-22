Topics and Drafts
=================

*Bot API 9.3 — December 2025*

Topics split one chat into many. A supergroup with forums turned on becomes a list of
threads instead of a single stream, and every message in it belongs to exactly one topic.
Drafts are the other half of the same release: the unsent text a client keeps for a chat.


-----

Turning a group into a forum
----------------------------

.. code-block:: python

    await app.toggle_forum(chat_id, enabled=True)

``tabs=True`` presents the topics as tabs rather than as a list.
:meth:`~pyrogram.Client.toggle_view_forum_as_messages` flips an individual member's view
back to one flat stream, which is a per-user preference and not a group setting.

Managing topics
---------------

.. code-block:: python

    topic = await app.create_forum_topic(
        chat_id=group_id,
        title="Bug reports",
        icon_color=0x6FB9F0,
        icon_emoji_id=custom_emoji_id,
    )

    await app.edit_forum_topic(group_id, topic.id, title="Bugs", closed=False)
    await app.close_forum_topic(group_id, topic.id)
    await app.delete_forum_topic(group_id, topic.id)

Reading them back:

.. code-block:: python

    async for topic in app.get_forum_topics(group_id):
        print(topic.id, topic.title, topic.unread_count, topic.is_closed)

    one = await app.get_forum_topics_by_id(group_id, topic_ids=[topic_id])

Sending into a topic
--------------------

``message_thread_id`` is the topic id, and every ``send_*`` method takes it:

.. code-block:: python

    await app.send_message(
        chat_id=group_id,
        text="Reproduced on 3.14.",
        message_thread_id=topic_id,
    )

On an incoming message, ``message.message_thread_id`` is the topic it belongs to and
``message.topic`` is the parsed :obj:`~pyrogram.types.ForumTopic` — that second one is
filled in only when the client is fetching topics, which is the ``fetch_topics`` argument to
:obj:`~pyrogram.Client` and is on by default. Turn it off to save the lookups if you only
ever need the id.

Private chat topics
-------------------

Bot API 9.3 also brought topics to private chats, which Telegram models as a "monoforum": a
channel whose direct messages tab is organised per user. wzgram surfaces those as
:obj:`~pyrogram.types.DirectMessagesTopic` with their own parameter,
``direct_messages_topic_id``, rather than as forum topics — see :doc:`direct-messages`.

A chat that is one of these has ``is_direct_messages`` set, and a channel that owns one
points at it with ``direct_messages_chat_id``.

Drafts
------

Every ``send_*`` method takes ``clear_draft``. Passing ``True`` wipes the chat's saved draft
as the message goes out, which is what an interactive client does so the half-typed text
does not reappear after a successful send:

.. code-block:: python

    await app.send_message(chat_id, "Sent for real this time", clear_draft=True)

For the richer, structured drafts of Bot API 10.1, see
:meth:`~pyrogram.Client.send_rich_message_draft` in :doc:`rich-messages`.

Gotchas
-------

- Topic id 1 is the "General" topic that every forum has and that cannot be deleted.
- ``message_thread_id`` on a *non-forum* supergroup means the discussion thread of a
  channel post, not a topic. Same parameter, different meaning by chat type.
- Closing a topic is not deleting it: closed topics stay readable and admins can still post.
