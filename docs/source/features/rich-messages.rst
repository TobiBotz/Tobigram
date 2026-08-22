Rich Messages
=============

*Bot API 10.1 — June 2026, media added in 10.2*

A rich message is a document sent as a message. Where an ordinary message is a line of text
with entities on top, a rich message has structure: headings, lists, tables, pull quotes,
code blocks, collapsible sections, collages, maps and captions — the vocabulary of an
Instant View article, composed and sent from your own code.

Rich messages are sent by **bots**.


-----

Three ways to write one
-----------------------

:obj:`~pyrogram.types.InputRichMessage` takes exactly one of ``html``, ``markdown`` or
``blocks``. They map to three different constructors on the wire and they carry media
differently, which is the one thing worth understanding before you start.

.. code-block:: python

    from pyrogram.types import InputRichMessage

    await app.send_rich_message(
        chat_id="me",
        rich_text=InputRichMessage(
            html="<h2>Release notes</h2><p>Layer <b>228</b> is live.</p>",
        ),
    )

``markdown`` is the same thing in the other syntax. ``blocks`` is the structured form:

.. code-block:: python

    from pyrogram.types import (
        InputRichMessage,
        InputRichBlockSectionHeading,
        InputRichBlockParagraph,
        InputRichBlockList,
        InputRichBlockListItem,
        InputRichBlockPreformatted,
    )

    await app.send_rich_message(
        chat_id="me",
        rich_text=InputRichMessage(blocks=[
            InputRichBlockSectionHeading(text="Release notes", size=2),
            InputRichBlockParagraph(text="Layer 228 is live."),
            InputRichBlockList(
                items=[
                    InputRichBlockListItem(text="Ephemeral messages"),
                    InputRichBlockListItem(text="Communities"),
                    InputRichBlockListItem(text="Rich message media", has_checkbox=True, is_checked=True),
                ],
                ordered=False,
            ),
            InputRichBlockPreformatted(text="pip install -U wzgram", language="bash"),
        ]),
    )

Passing more than one of the three is not an error: the first set one in the order
``html``, ``markdown``, ``blocks`` wins and the rest are ignored. Setting none raises
``ValueError`` when the message is sent.

The block vocabulary
--------------------

Every block is a class under :obj:`~pyrogram.types.InputRichBlock`:

============================================  ===========================================
Block                                          What it is
============================================  ===========================================
``InputRichBlockParagraph``                    a paragraph of text
``InputRichBlockSectionHeading``               a heading, ``size`` 1-6
``InputRichBlockPreformatted``                 a code block with a ``language``
``InputRichBlockList``                         ordered or bulleted, items may have checkboxes
``InputRichBlockBlockQuotation``               a quote wrapping other blocks
``InputRichBlockPullQuotation``                a pull quote with a ``credit``
``InputRichBlockTable``                        rows of ``InputRichBlockTableCell``
``InputRichBlockDetails``                      a collapsible section
``InputRichBlockCollage`` / ``…Slideshow``     grouped media
``InputRichBlockPhoto`` / ``…Video``           a single photo or video, with spoiler and autoplay flags
``InputRichBlockAudio`` / ``…VoiceNote``       an audio file or a voice note
``InputRichBlockAnimation``                    a looping video
``InputRichBlockMap``                          a map at a geo point and zoom
``InputRichBlockMathematicalExpression``       a formula
``InputRichBlockAnchor``                       a named target to link to
``InputRichBlockDivider``                      a horizontal rule
``InputRichBlockFooter``                       trailing small print
``InputRichBlockThinking``                     a model's reasoning, rendered as such
============================================  ===========================================

Attaching media
---------------

Media in a rich message must **already exist on Telegram**. You pass a file identifier, an
``InputPhoto`` or an ``InputDocument`` — never a local path. Nothing here uploads.

How you attach it depends on which of the three forms you used, and
:obj:`~pyrogram.types.InputRichMessageMedia` covers both shapes:

**html and markdown** — each media entry needs an ``id`` of your choosing, and the text
refers to it with a ``tg://`` link:

.. code-block:: python

    from pyrogram.types import InputRichMessage, InputRichMessageMedia

    await app.send_rich_message(
        chat_id="me",
        rich_text=InputRichMessage(
            html='<p>Here it is:</p><img src="tg://photo?id=cover">',
            media=[InputRichMessageMedia(id="cover", media=photo_file_id)],
        ),
    )

The scheme says what kind of media it is: ``tg://photo?id=``, ``tg://video?id=`` or
``tg://audio?id=``.

**blocks** — the media travels as bare vectors that the blocks point into, so the entry
carries ``photos``, ``documents`` or ``users`` rather than a single ``media``:

.. code-block:: python

    InputRichMessage(
        blocks=[InputRichBlockPhoto(photo_id=input_photo.id, caption="The cover")],
        media=[InputRichMessageMedia(photos=[input_photo])],
    )

A block's ``photo_id`` / ``video_id`` / ``audio_id`` must equal the ``id`` attribute of the
corresponding ``InputPhoto`` or ``InputDocument`` in those vectors. MTProto carries no
string identifiers on this side, which is why the two shapes differ at all.

Drafts and diffs
----------------

:meth:`~pyrogram.Client.send_rich_message_draft` saves a rich message as a draft in a chat
rather than sending it, which is how an editing tool shows a preview before publishing:

.. code-block:: python

    await app.send_rich_message_draft(chat_id, draft_id=1, rich_message=rich)

:obj:`~pyrogram.types.RichTextDiff` marks a rich text as a *change* against an older one,
pairing ``text`` with ``old_text``. Clients render the difference.

Rich text elsewhere
-------------------

``rich_text`` is not confined to :meth:`~pyrogram.Client.send_rich_message`.
:meth:`~pyrogram.Client.send_message`, :meth:`~pyrogram.Client.edit_message_text` and
:meth:`~pyrogram.Client.send_ephemeral_message` take a ``rich_text`` of their own, with
``rich_text_media`` for its media and ``rich_text_parse_mode`` (Markdown by default) for
when you pass a plain string rather than an :obj:`~pyrogram.types.InputRichMessage`:

.. code-block:: python

    await app.send_message(
        chat_id="me",
        text="",
        rich_text="# Heading

A paragraph.",
    )

When ``rich_text`` is set, ``text`` is ignored.

Gotchas
-------

- A local file path in ``media`` is refused, not uploaded. Send the file somewhere first —
  a saved-messages chat is the usual trick — and use the identifier it comes back with.
- With ``html`` and ``markdown``, the ``id`` in the media entry and the ``id=`` in the
  ``tg://`` link must match exactly. A typo means the media is dropped rather than an error.
- With ``blocks``, a block's ``photo_id`` is the *file's own* id, not a position in the
  vector. Copying an id from one message's media to another's will not resolve.
- The three constructors are not interchangeable at the protocol level even though one
  wzgram type covers them. Media attached in the block shape is ignored by the html shape
  and the other way round.
