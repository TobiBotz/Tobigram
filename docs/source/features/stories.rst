Stories
=======

*Bot API 9.0 — April 2025*

Stories are the 24-hour posts that sit above the chat list. They belong to a user or a
channel, expire on their own, and carry their own privacy rules, reactions and view lists.

Posting stories is a **user** feature: a bot cannot post one for itself, only manage one for
a business account it is connected to with the right permission.


-----

Posting
-------

:meth:`~pyrogram.Client.send_story` uploads a photo or video and publishes it:

.. code-block:: python

    from wzgram import enums

    story = await app.send_story(
        chat_id="me",
        media="sunset.jpg",
        caption="Golden hour",
        period=86400,
        privacy=enums.StoriesPrivacyRules.CONTACTS,
    )

``period`` is how long it stays up, in seconds — Telegram accepts 6, 12, 24 or 48 hours.
``privacy`` takes a :obj:`~pyrogram.enums.StoriesPrivacyRules` member: ``PUBLIC``,
``CONTACTS``, ``CLOSE_FRIENDS`` or ``SELECTED_USERS``, the last one paired with
``allowed_users``. ``disallowed_users`` subtracts from whichever rule you chose.

``pinned=True`` also keeps the story on the profile after it expires.

Interactive areas
-----------------

``media_areas`` places tappable regions on top of the media — a location, a venue, a
reaction bubble, a link to a channel post, a weather badge, a gift. One
:obj:`~pyrogram.types.MediaArea` covers all of them: the rectangle is given in percentages
of the media's own size, and ``type`` says what the area *is*.

.. code-block:: python

    from wzgram import enums
    from wzgram.types import MediaArea

    await app.send_story(
        chat_id="me",
        media="announcement.mp4",
        media_areas=[
            MediaArea(
                x=50, y=80, width=60, height=10, rotation=0,
                type=enums.MediaAreaType.URL,
                url="https://example.com/tickets",
            )
        ],
    )

Every coordinate is a percentage from 0 to 100, so an area keeps its place whatever the
resolution of the upload. The writable types are ``POST``, ``LOCATION``, ``REACTION``,
``URL``, ``WEATHER`` and ``GIFT``; each reads the fields its own kind needs — ``url`` here,
``sender_chat`` and ``message_id`` for ``POST``, ``reaction`` for ``REACTION``.

Reading
-------

.. code-block:: python

    async for story in app.get_chat_stories("some_channel"):
        print(story.id, story.caption, story.views)

    story = await app.get_stories("some_channel", story_ids=42)

    async for view in app.get_story_views("me", story_id=42, reactions_first=True):
        print(view.from_user.first_name, view.reaction)

:meth:`~pyrogram.Client.get_pinned_stories` reads what a profile keeps on show,
:meth:`~pyrogram.Client.get_archived_stories` reads your own expired ones, and
:meth:`~pyrogram.Client.get_all_stories` walks the whole feed.

Marking a story as seen is :meth:`~pyrogram.Client.view_stories` for one and
:meth:`~pyrogram.Client.read_chat_stories` for everything up to an id.
:meth:`~pyrogram.Client.enable_stealth_mode` hides your views for a window of time — ``past``
retroactively for the last five minutes, ``future`` for the next twenty-five.

Editing and reposting
---------------------

A published story can still be changed:

- :meth:`~pyrogram.Client.edit_story_caption` — text only
- :meth:`~pyrogram.Client.edit_story_media` — replace the file, areas and dimensions
- :meth:`~pyrogram.Client.edit_story_privacy` — change who can see it
- :meth:`~pyrogram.Client.pin_chat_stories` / :meth:`~pyrogram.Client.unpin_chat_stories`

:meth:`~pyrogram.Client.copy_story` republishes someone else's story as your own, while
:meth:`~pyrogram.Client.forward_story` sends it into a chat as a message.

Reacting and receiving
----------------------

New stories reach a running client through :meth:`~pyrogram.Client.on_story`:

.. code-block:: python

    @app.on_story()
    async def seen(client, story):
        print(f"new story {story.id} from {story.chat.id}")

Gotchas
-------

- :meth:`~pyrogram.Client.can_post_stories` returns the number of stories still allowed
  today, not a boolean. Zero means the daily limit is spent.
- ``story.media`` is a :obj:`~pyrogram.enums.MessageMediaType`, not the file. The file is in
  ``story.photo`` or ``story.video``.
- Channel stories need the *post stories* admin right; the API rejects the call rather than
  posting silently to your own profile.
