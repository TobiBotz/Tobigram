Rich Text Formatting
====================

Rich Text is Telegram's structured formatting engine used for Instant View articles, page blocks,
web app responses, and modern **Rich Messages** (introduced in Bot API 10.1 and MTProto Layer 228+).

Unlike ordinary message text formatting (which attaches a flat list of :obj:`~pyrogram.types.MessageEntity`
offsets on top of a string), **Rich Text** is a tree-based hierarchical document structure. It supports
advanced styling that ordinary messages cannot express, such as mathematical formulas (LaTeX), subscript,
superscript, highlighted text, named anchors, collapsible sections, and inline images.

-----

Ordinary Formatting vs Rich Text
--------------------------------

==================================  ===============================  ===================================
Feature                             Ordinary Message Formatting       Rich Text (:class:`~pyrogram.types.RichText`)
==================================  ===============================  ===================================
**Wire Protocol**                   ``MessageEntity`` offsets        ``raw.types.Text*`` & ``RichText``
**Methods**                         ``send_message()``               ``send_rich_message()``, Web Apps
**Subscript & Superscript**         ❌ Not supported                 ✅ ``RichTextSubscript`` / ``RichTextSuperscript``
**Highlighted / Marked Text**       ❌ Not supported                 ✅ ``RichTextMarked`` (``<mark>``)
**Math Expressions (LaTeX)**        ❌ Not supported                 ✅ ``RichTextMathematicalExpression``
**Inline Anchors & Links**          ❌ Text links only               ✅ ``RichTextAnchor`` & ``RichTextAnchorLink``
**Collapsible Details & Blocks**    ❌ Blockquotes only              ✅ Full collapsible sections & tables
==================================  ===============================  ===================================

-----

Writing and Sending Rich Text
-----------------------------

Bots can send rich messages using :meth:`~pyrogram.Client.send_rich_message` and construct the content
using :class:`~pyrogram.types.InputRichMessage`.

There are three ways to compose rich content:

1. Using HTML (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can write standard HTML tags including rich tags like ``<mark>``, ``<sub>``, ``<sup>``, and ``<tg-emoji>``:

.. code-block:: python

    from pyrogram import Client
    from pyrogram.types import InputRichMessage

    app = Client("my_bot")

    async with app:
        await app.send_rich_message(
            chat_id="me",
            rich_text=InputRichMessage(
                html=(
                    "<h2>Scientific Note</h2>"
                    "<p>Water molecule: H<sub>2</sub>O</p>"
                    "<p>Einstein's equation: E = mc<sup>2</sup></p>"
                    "<p>Important note: <mark>Exam starts at 9:00 AM</mark></p>"
                    "<p>Emoji: <tg-emoji emoji-id=5469770542288478598>👍</tg-emoji></p>"
                )
            ),
        )

2. Using Markdown
~~~~~~~~~~~~~~~~~

Markdown mode supports standard styling along with blockquotes and code blocks:

.. code-block:: python

    from pyrogram.types import InputRichMessage

    await app.send_rich_message(
        chat_id="me",
        rich_text=InputRichMessage(
            markdown=(
                "## Project Update\n\n"
                "> Deployment to production is completed.\n\n"
                "**Status**: All checks passed.\n"
            )
        ),
    )

3. Using Structured Blocks
~~~~~~~~~~~~~~~~~~~~~~~~~~

For full control over articles, headings, tables, checkboxes, and collages, use :obj:`~pyrogram.types.InputRichBlock` classes:

.. code-block:: python

    from pyrogram.types import (
        InputRichMessage,
        InputRichBlockSectionHeading,
        InputRichBlockParagraph,
        InputRichBlockList,
        InputRichBlockListItem,
        InputRichBlockPreformatted,
        InputRichBlockDivider,
    )

    await app.send_rich_message(
        chat_id="me",
        rich_text=InputRichMessage(
            blocks=[
                InputRichBlockSectionHeading(text="Release v3.2", size=2),
                InputRichBlockParagraph(text="Tobigram now features enhanced rich media text formatting."),
                InputRichBlockDivider(),
                InputRichBlockList(
                    items=[
                        InputRichBlockListItem(text="Instant View acceleration", has_checkbox=True, is_checked=True),
                        InputRichBlockListItem(text="LaTeX math rendering", has_checkbox=True, is_checked=True),
                        InputRichBlockListItem(text="Interactive checklists", has_checkbox=True, is_checked=False),
                    ],
                    ordered=False,
                ),
                InputRichBlockPreformatted(text="pip install -U tobigram", language="bash"),
            ]
        ),
    )

-----

Supported RichText Elements
---------------------------

When receiving messages or reading Instant View pages, Telegram represents formatted nodes with
the following :obj:`~pyrogram.types.RichText` types:

========================================================  ======================================================
Class                                                     Description
========================================================  ======================================================
:class:`~pyrogram.types.RichTextPlain`                    Plain text without styling.
:class:`~pyrogram.types.RichTextBold`                     Bold styled text.
:class:`~pyrogram.types.RichTextItalic`                   Italic styled text.
:class:`~pyrogram.types.RichTextUnderline`                Underlined text.
:class:`~pyrogram.types.RichTextStrikethrough`            Strikethrough text.
:class:`~pyrogram.types.RichTextSpoiler`                  Hidden spoiler text.
:class:`~pyrogram.types.RichTextCode`                     Inline fixed-width code.
:class:`~pyrogram.types.RichTextSubscript`                Subscript text (e.g. chemical formulas).
:class:`~pyrogram.types.RichTextSuperscript`              Superscript text (e.g. mathematical powers).
:class:`~pyrogram.types.RichTextMarked`                   Highlighted or marked text background.
:class:`~pyrogram.types.RichTextCustomEmoji`              Animated or static custom emoji from sticker pack.
:class:`~pyrogram.types.RichTextDateTime`                 Reader-localized date and time.
:class:`~pyrogram.types.RichTextMathematicalExpression`   LaTeX mathematical formula.
:class:`~pyrogram.types.RichTextUrl`                      Clickable web link URL.
:class:`~pyrogram.types.RichTextEmailAddress`             Clickable email address.
:class:`~pyrogram.types.RichTextPhoneNumber`              Clickable phone number.
:class:`~pyrogram.types.RichTextBankCardNumber`           Formatted bank card number.
:class:`~pyrogram.types.RichTextAnchor`                   Named anchor target inside the article.
:class:`~pyrogram.types.RichTextAnchorLink`               Link jumping to a named anchor in the same document.
:class:`~pyrogram.types.RichTextImage`                    Inline picture embedded directly into text flow.
========================================================  ======================================================

-----

Rich Message Drafts & AI Composition
------------------------------------

Bots can send rich message drafts to display typing states, live generated progress, or "Thinking..." placeholders:

.. code-block:: python

    from pyrogram.types import (
        InputRichMessage,
        InputRichBlockParagraph,
        InputRichBlockThinking,
    )

    # Send a draft while computing the final response
    await app.send_rich_message_draft(
        chat_id="me",
        rich_text=InputRichMessage(
            blocks=[
                InputRichBlockParagraph(text="Generating response..."),
                InputRichBlockThinking(),
            ]
        ),
    )

    # Send the final rich message once computation completes
    await app.send_rich_message(
        chat_id="me",
        rich_text=InputRichMessage(
            html="<p><b>Done!</b> Here is your complete report.</p>"
        ),
    )
