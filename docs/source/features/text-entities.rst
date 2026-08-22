Text Entities and Button Styling
================================

*Bot API 9.4 and 9.5 — February and March 2026*

Two releases widened what a message can say without carrying media: custom emoji anywhere in
the text, dates that each reader sees in their own locale and timezone, and buttons that can
be coloured and carry an emoji.

The formatting syntax itself is covered in :doc:`/topics/text-formatting`. This page is about
what the newer entities mean and when to reach for them.


-----

Formatted dates
---------------

``MessageEntityFormattedDate`` — :obj:`~pyrogram.enums.MessageEntityType`'s ``DATE_TIME`` —
holds a Unix timestamp, and every client renders it in the reader's own timezone and
language. A deadline written this way reads correctly in Tokyo and in Lisbon.

In HTML it is ``tg-time``:

.. code-block:: python

    from pyrogram.enums import ParseMode

    await app.send_message(
        chat_id="me",
        text='Maintenance starts <tg-time unix="1767225600" format="Dt">then</tg-time>.',
        parse_mode=ParseMode.HTML,
    )

``format`` is a set of single-letter flags:

============  ====================================================
Flag          Renders
============  ====================================================
``r``         relative — "in 3 hours", "2 days ago"; used alone
``w``         day of the week
``d``         short date
``D``         long date
``t``         short time
``T``         long time
============  ====================================================

Combine them (``"Dt"`` is a long date with a short time). ``r`` is exclusive: given alone it
makes the whole thing relative, and it ignores the rest.

Custom emoji
------------

``CUSTOM_EMOJI`` entities replace a run of text with an animated emoji from a pack. The
document id is what identifies it:

.. code-block:: python

    await app.send_message(
        chat_id="me",
        text='<tg-emoji emoji-id="5469770542288478598">👍</tg-emoji> shipped',
        parse_mode=ParseMode.HTML,
    )

Always keep a real emoji as the tag's text. That is what clients without the pack — and
every notification preview — will show instead.

:meth:`~pyrogram.Client.get_custom_emoji_stickers` resolves ids back to the stickers behind
them, which is how you find out what an incoming entity actually depicts.

Styled buttons
--------------

:obj:`~pyrogram.types.InlineKeyboardButton` takes ``style`` and ``icon_custom_emoji_id``:

.. code-block:: python

    from pyrogram import enums
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    await app.send_message(
        chat_id="me",
        text="Delete this backup?",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Delete", callback_data="del", style=enums.ButtonStyle.DANGER),
            InlineKeyboardButton("Keep", callback_data="keep", style=enums.ButtonStyle.SUCCESS),
        ]]),
    )

:obj:`~pyrogram.enums.ButtonStyle` is ``DEFAULT``, ``PRIMARY``, ``DANGER`` or ``SUCCESS``.
Colour carries meaning here — use ``DANGER`` for the destructive choice rather than for
emphasis.

Diff entities
-------------

``DIFF_INSERT``, ``DIFF_REPLACE`` and ``DIFF_DELETE`` mark up a *change* to text rather than
the text itself. They are what Telegram's AI writing tools use to show what they altered, and
they arrive from :meth:`~pyrogram.Client.compose_text_with_ai` and
:meth:`~pyrogram.Client.fix_text_with_ai`.

Gotchas
-------

- A formatted date entity needs text to cover, just like bold does. Give it something
  readable as a fallback — the entity replaces it, but only where the client understands it.
- Custom emoji ids belong to a pack, not to your bot. If the pack is removed, the fallback
  text is all that is left.
- Entity offsets are in UTF-16 code units. wzgram handles that for you when you use a parse
  mode; building entities by hand is where the surprises are.
