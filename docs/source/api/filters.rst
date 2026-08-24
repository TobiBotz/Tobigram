Filters
=======

.. module:: pyrogram.filters

Filters decide which updates reach a handler. They are passed to a decorator or to a handler
class, and they compose with ``&`` (and), ``|`` (or) and ``~`` (not):

.. code-block:: python

    from wzgram import filters

    @app.on_message(filters.text & filters.private & ~filters.bot)
    async def only_humans_in_dm(client, message):
        ...

See :doc:`/topics/use-filters` for how they combine, and :doc:`/topics/create-filters` for
writing your own.


-----

Callable filters
----------------

These take arguments and return a filter:

.. csv-table::
    :header: Filter, Matches
    :widths: 25 75

    "``filters.command(commands, prefixes, case_sensitive)``", "messages starting with a command"
    "``filters.regex(pattern, flags=0)``", "messages whose text or caption matches a regex"
    "``filters.user(users)``", "updates from specific users, by id or username"
    "``filters.chat(chats)``", "updates from specific chats, by id or username"
    "``filters.topic(topics)``", "messages in specific forum topics"
    "``filters.create(func, name=None, **kwargs)``", "a custom filter from your own predicate"

``filters.user``, ``filters.chat`` and ``filters.topic`` build mutable sets — you can add and
remove entries on a live client, which is what makes an allow-list handler possible without
re-registering it.

Origin and direction
--------------------

.. csv-table::
    :header: Filter, Matches
    :widths: 25 75

    ``filters.all``, "everything"
    ``filters.me``, "messages sent by yourself"
    ``filters.bot``, "messages sent by a bot"
    ``filters.sender_chat``, "messages sent on behalf of a chat"
    ``filters.incoming``, "messages received"
    ``filters.outgoing``, "messages sent"
    ``filters.forwarded``, "forwarded messages"
    ``filters.via_bot``, "messages sent via an inline bot"
    ``filters.mentioned``, "messages that mention you"
    ``filters.reply``, "messages that reply to another"
    ``filters.quote``, "replies that quote part of the original"
    ``filters.scheduled``, "scheduled messages"
    ``filters.from_scheduled``, "messages that were scheduled and have now been sent"
    ``filters.linked_channel``, "channel posts automatically forwarded to a discussion group"
    ``filters.business``, "messages arriving through a business connection"
    ``filters.paid_message``, "messages that cost Stars to send"

Chat kind
---------

.. csv-table::
    :header: Filter, Matches
    :widths: 25 75

    ``filters.private``, "private chats"
    ``filters.direct``, "private chats (alias of ``private``)"
    ``filters.group``, "groups and supergroups"
    ``filters.channel``, "channels"
    ``filters.forum``, "chats with topics enabled"
    ``filters.admin``, "chats where you are an administrator"

Content
-------

.. csv-table::
    :header: Filter, Matches
    :widths: 25 75

    ``filters.text``, "text messages"
    ``filters.caption``, "messages with a caption"
    ``filters.media``, "any media message"
    ``filters.media_group``, "messages that are part of an album"
    ``filters.media_spoiler``, "media hidden behind a spoiler"
    ``filters.self_destruction``, "media with a self-destruct timer"
    ``filters.photo``, "photos"
    ``filters.video``, "videos"
    ``filters.video_note``, "video notes"
    ``filters.animation``, "animations (GIFs)"
    ``filters.audio``, "audio files"
    ``filters.voice``, "voice notes"
    ``filters.document``, "documents"
    ``filters.sticker``, "stickers"
    ``filters.story``, "stories"
    ``filters.web_page``, "messages with a link preview"
    ``filters.contact``, "shared contacts"
    ``filters.location``, "locations"
    ``filters.live_location``, "live locations"
    ``filters.venue``, "venues"
    ``filters.poll``, "polls"
    ``filters.dice``, "dice"
    ``filters.game``, "games"

Keyboards and interaction
-------------------------

.. csv-table::
    :header: Filter, Matches
    :widths: 25 75

    ``filters.reply_keyboard``, "messages carrying a reply keyboard"
    ``filters.inline_keyboard``, "messages carrying an inline keyboard"
    ``filters.users_shared``, "users shared through a request button"
    ``filters.chat_shared``, "a chat shared through a request button"

Gifts, giveaways and payments
-----------------------------

.. csv-table::
    :header: Filter, Matches
    :widths: 25 75

    ``filters.gift``, "gift service messages"
    ``filters.gift_code``, "premium gift codes"
    ``filters.gift_offer``, "a pending purchase offer for a unique gift"
    ``filters.gift_offer_accepted``, "an accepted purchase offer"
    ``filters.gift_offer_rejected``, "a declined purchase offer"
    ``filters.giveaway``, "giveaway messages"
    ``filters.giveaway_winners``, "giveaway winner announcements"
    ``filters.successful_payment``, "successful payment service messages"
    ``filters.game_high_score``, "game high score service messages"

Service messages
----------------

.. csv-table::
    :header: Filter, Matches
    :widths: 25 75

    ``filters.service``, "any service message"
    ``filters.new_chat_members``, "members joining"
    ``filters.left_chat_member``, "a member leaving"
    ``filters.new_chat_title``, "the chat title changing"
    ``filters.new_chat_photo``, "the chat photo changing"
    ``filters.delete_chat_photo``, "the chat photo being removed"
    ``filters.pinned_message``, "a message being pinned"
    ``filters.group_chat_created``, "a group being created"
    ``filters.supergroup_chat_created``, "a supergroup being created"
    ``filters.channel_chat_created``, "a channel being created"
    ``filters.migrate_to_chat_id``, "a group migrating to a supergroup"
    ``filters.migrate_from_chat_id``, "the supergroup a group migrated from"
    ``filters.video_chat_started``, "a video chat starting"
    ``filters.video_chat_ended``, "a video chat ending"
    ``filters.video_chat_members_invited``, "members invited to a video chat"

Base classes
------------

.. autoclass:: pyrogram.filters.Filter()
.. automethod:: pyrogram.filters.create()
.. automethod:: pyrogram.filters.command()
.. automethod:: pyrogram.filters.regex()
