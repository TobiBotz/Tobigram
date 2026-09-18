Reporting Abuse & Content
==========================

Telegram provides native mechanisms to report spam, abuse, intellectual property violations,
and harmful content. Tobigram provides high-level client methods and convenient bound methods
for all reportable entities across Telegram's MTProto API.

.. code-block:: python

    from pyrogram import Client
    from pyrogram.enums import ReportReason

    app = Client("my_account")

    async with app:
        # Report a channel for spam
        await app.report_chat("@spammer_channel", ReportReason.SPAM)

-----

Available Reasons
-----------------

The :obj:`~pyrogram.enums.ReportReason` enumeration defines all 10 official reason categories
supported by Telegram:

.. list-table::
    :header-rows: 1
    :widths: 30 70

    * - Reason Enum
      - Description
    * - ``ReportReason.SPAM``
      - Unsolicited bulk messages, spam bots, or advertisements.
    * - ``ReportReason.VIOLENCE``
      - Physical threats, violence, or incitement to harm.
    * - ``ReportReason.PORNOGRAPHY``
      - Explicit adult, NSFW, or non-consensual sexual content.
    * - ``ReportReason.CHILD_ABUSE``
      - Child sexual abuse and child exploitation material.
    * - ``ReportReason.COPYRIGHT``
      - Unauthorized copyright or intellectual property infringements.
    * - ``ReportReason.GEO_IRRELEVANT``
      - Irrelevant or promotional content posted in location-based chats.
    * - ``ReportReason.FAKE``
      - Impersonation, fake profiles, phishing, or financial fraud.
    * - ``ReportReason.ILLEGAL_DRUGS``
      - Sale or promotion of illegal narcotics and banned substances.
    * - ``ReportReason.PERSONAL_DETAILS``
      - Doxxing, privacy violations, or unauthorized leaks of personal data.
    * - ``ReportReason.OTHER``
      - Any custom reason; accompanied by an explanatory message comment.

-----

Reporting Chats and Channels
----------------------------

Use :meth:`~pyrogram.Client.report_chat` to report an entire group, supergroup, or channel:

.. code-block:: python

    await app.report_chat(
        chat_id="@scam_channel",
        reason=ReportReason.FAKE,
        message="Impersonating our official service"
    )

For quick 1-click spam dismissal on incoming unapproved dialogues, use :meth:`~pyrogram.Client.report_spam`:

.. code-block:: python

    await app.report_spam(chat_id)

-----

Reporting Messages
------------------

Use :meth:`~pyrogram.Client.report_messages` to report one or more specific messages in a chat:

.. code-block:: python

    await app.report_messages(
        chat_id=chat_id,
        message_ids=[123, 124],
        reason=ReportReason.SPAM,
        message="Automated affiliate link spam"
    )

Supergroup administrators reporting specific participant spam can pass the ``participant`` argument:

.. code-block:: python

    await app.report_messages(
        chat_id=chat_id,
        message_ids=message_id,
        participant=user_id
    )

-----

Reporting Users and Profile Photos
----------------------------------

Use :meth:`~pyrogram.Client.report_user` to report a user profile directly:

.. code-block:: python

    await app.report_user(user_id, ReportReason.SPAM)

Use :meth:`~pyrogram.Client.report_profile_photo` to report an offensive profile photo:

.. code-block:: python

    user = await app.get_users("bad_actor")
    if user.photo:
        await app.report_profile_photo(
            chat_id=user.id,
            photo=user.photo.big_file_id,
            reason=ReportReason.PORNOGRAPHY
        )

-----

Reporting Stories and Reactions
-------------------------------

To report user or channel stories, use :meth:`~pyrogram.Client.report_story`:

.. code-block:: python

    await app.report_story(chat_id, story_id, ReportReason.SPAM)

To report abusive or offensive emoji reactions left on messages, use :meth:`~pyrogram.Client.report_reaction`:

.. code-block:: python

    await app.report_reaction(chat_id, message_id, reaction_peer)

-----

Bound Methods Shortcut
----------------------

Models in Tobigram include bound shortcuts for cleaner, object-oriented syntax:

.. code-block:: python

    # Bound method on Chat
    await chat.report(ReportReason.SPAM)
    await chat.report_spam()

    # Bound method on User
    await user.report(ReportReason.FAKE)

    # Bound method on Message
    await message.report(ReportReason.VIOLENCE)

    # Bound method on Story
    await story.report(ReportReason.PORNOGRAPHY)
