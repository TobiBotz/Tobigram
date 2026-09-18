Text Formatting
===============

.. role:: strike
    :class: strike

.. role:: underline
    :class: underline

.. role:: bold-underline
    :class: bold-underline

.. role:: strike-italic
    :class: strike-italic

Tobigram uses a custom Markdown dialect for text formatting which adds some unique features that make writing styled
texts easier in both Markdown and HTML. You can send sophisticated text messages and media captions using a
variety of decorations that can also be nested in order to combine multiple styles together.

`The official BOT API style HTML formatting is also supported <https://core.telegram.org/bots/api#html-style>`__

.. tip::

    The default parse mode, :obj:`~pyrogram.enums.ParseMode.DEFAULT`, understands **both**
    syntaxes in one message, so ``**bold**`` and ``<blockquote>`` can sit side by side.
    :obj:`~pyrogram.enums.ParseMode.MARKDOWN` and :obj:`~pyrogram.enums.ParseMode.HTML` are
    the strict modes: each escapes the other's syntax, so a tag inside strict Markdown is
    sent as literal text. :obj:`~pyrogram.enums.ParseMode.DISABLED` sends everything as
    written.


-----

Basic Styles
------------

When formatting your messages, you can choose between Markdown-style, HTML-style or both (default). The following is a
list of the basic styles currently supported by Tobigram.

- **bold**
- *italic*
- :underline:`underline`
- :strike:`strike`
- blockquote and expandable blockquote
- ``inline fixed-width code``
- pre-formatted fixed-width code block
- spoiler
- custom emoji (``<emoji id="...">``)
- formatted date and time (``<tg-time unix="...">``)
- `text URL <https://docs.tobigram.com/>`_
- `user text mention <tg://user?id=123456789>`_


HTML Style
----------

To strictly use this mode, pass :obj:`~pyrogram.enums.ParseMode.HTML` to the *parse_mode* parameter when using
:meth:`~pyrogram.Client.send_message`. The following tags are currently supported:

.. code-block:: text

    <b>bold</b>, <strong>bold</strong>

    <i>italic</i>, <em>italic</em>

    <u>underline</u>, <ins>underline</ins>

    <s>strike</s>, <del>strike</del>, <strike>strike</strike>

    <tg-spoiler>spoiler</tg-spoiler>, <span class="tg-spoiler">spoiler</span>

    <blockquote>block quotation</blockquote>

    <blockquote expandable>expandable block quotation</blockquote>

    <a href="https://pyrogram.com/">text URL</a>

    <a href="tg://user?id=123456789">inline mention</a>

    <code>inline fixed-width code</code>

    <tg-emoji emoji-id="5469770542288478598">👍</tg-emoji>

    <tg-time unix="1735689600" format="d">formatted date and time</tg-time>

    <pre>
        <code class="language-python">
            pre-formatted fixed-width code block written in the Python programming language
        </code>
    </pre>

**Example**:

.. code-block:: python

    from pyrogram.enums import ParseMode

    await app.send_message(
        chat_id="me",
        text=(
            "<b>bold</b>, <strong>bold</strong>"
            "<i>italic</i>, <em>italic</em>"
            "<u>underline</u>, <ins>underline</ins>"
            "<s>strike</s>, <strike>strike</strike>, <del>strike</del>"
            "<tg-spoiler>spoiler</tg-spoiler>\n\n"

            "<b>bold <i>italic bold <s>italic bold strike <tg-spoiler>italic bold strike spoiler</tg-spoiler></s> <u>underline italic bold</u></i> bold</b>\n\n"

            "<a href=\"https://tobigram.com/\">inline URL</a> "
            "<a href=\"tg://user?id=23122162\">inline mention of a user</a>\n"
            "<tg-emoji emoji-id=5469770542288478598>👍</tg-emoji> "
            "<code>inline fixed-width code</code> "
            "<pre>pre-formatted fixed-width code block</pre>\n\n"
            "<pre><code class='language-python'>"
            "for i in range(10):\n"
            "    print(i)"
            "</code></pre>\n\n"

            "<tg-time unix=\"1735689600\" format=\"d\">today</tg-time>\n\n"

            "<blockquote>Block quotation started"
            "Block quotation continued"
            "The last line of the block quotation</blockquote>"
            "<blockquote expandable>Expandable block quotation started"
            "Expandable block quotation continued"
            "Expandable block quotation continued"
            "Hidden by default part of the block quotation started"
            "Expandable block quotation continued"
            "The last line of the block quotation</blockquote>"
        ),
        parse_mode=ParseMode.HTML
    )

.. note::

    All ``<``, ``>`` and ``&`` symbols that are not a part of a tag or an HTML entity must be replaced with the
    corresponding HTML entities (``<`` with ``&lt;``, ``>`` with ``&gt;`` and ``&`` with ``&amp;``). You can use this
    snippet to quickly escape those characters:

    .. code-block:: python

        text = "<my & text>"
        text = text.replace("<", "&lt;").replace("&", "&amp;")

        print(text)

    .. code-block:: text

        &lt;my &amp; text>


Markdown Style
--------------

To strictly use this mode, pass :obj:`~pyrogram.enums.ParseMode.MARKDOWN` to the *parse_mode* parameter when using
:meth:`~pyrogram.Client.send_message`. Use the following syntax in your message:

.. note::

    Blockquotes can be written in Markdown using ``>`` (for standard quotes) and ``**>...||`` (for expandable quotes).
    For custom emoji, use HTML syntax (``<emoji id="...">`` or ``<tg-emoji emoji-id="...">``).
    In the default combined parse mode, you can mix HTML emoji tags alongside Markdown styles freely.

.. code-block:: text

    **bold**

    __italic__

    --underline--

    ~~strike~~

    `inline fixed-width code`

    ```
    pre-formatted
      fixed-width
        code block
    ```

    ||spoiler||

    >block quotation

    **>expandable block quotation||

    [text URL](https://tobigram.com/)

    [text user mention](tg://user?id=123456789)


**Example**:

.. code-block:: python

    from pyrogram.enums import ParseMode

    await app.send_message(
        chat_id="me",
        text=(
            "**bold**, "
            "__italic__, "
            "--underline--, "
            "~~strike~~, "
            "||spoiler||, "
            ">quoted block\n"
            "**>expandable quote||\n"
            "[URL](https://tobigram.com/), "
            "`code`, "
            "```py\n"
            "for i in range(10):\n"
            "    print(i)\n"
            "```\n"

        ),
        parse_mode=ParseMode.MARKDOWN
    )


Different Styles
----------------

By default, when ignoring the *parse_mode* parameter, both Markdown and HTML styles are enabled together.
This means you can combine together both syntaxes in the same text:

.. code-block:: python

    await app.send_message(chat_id="me", text="**bold**, <i>italic</i>")

Result:

    **bold**, *italic*

If you don't like this behaviour you can always choose to only enable either Markdown or HTML in strict mode by passing
:obj:`~pyrogram.enums.ParseMode.MARKDOWN` or :obj:`~pyrogram.enums.ParseMode.HTML` as argument to the *parse_mode* parameter.

.. code-block:: python

    from pyrogram.enums import ParseMode

    await app.send_message(chat_id="me", text="**bold**, <i>italic</i>", parse_mode=ParseMode.MARKDOWN)
    await app.send_message(chat_id="me", text="**bold**, <i>italic</i>", parse_mode=ParseMode.HTML)

Result:

    **bold**, <i>italic</i>

    \*\*bold**, *italic*

In case you want to completely turn off the style parser, simply pass :obj:`~pyrogram.enums.ParseMode.DISABLED` to *parse_mode*.
The text will be sent as-is.

.. code-block:: python

    from pyrogram.enums import ParseMode

    await app.send_message(chat_id="me", text="**bold**, <i>italic</i>", parse_mode=ParseMode.DISABLED)

Result:

    \*\*bold**, <i>italic</i>

Nested and Overlapping Entities
-------------------------------

.. warning::

    The Markdown style is not recommended for complex text formatting.

    If you want to use complex text formatting such as nested entities, overlapping entities use the HTML style instead.


You can also style texts with more than one decoration at once by nesting entities together. For example, you can send
a text message with both :bold-underline:`bold and underline` styles, or a text that has both :strike-italic:`italic and
strike` styles, and you can still combine both Markdown and HTML together.

Here there are some example texts you can try sending:

**Markdown**:

- ``**bold, --underline--**``
- ``**bold __italic --underline ~~strike~~--__**``
- ``**bold __and** italic__``

**HTML**:

- ``<b>bold, <u>underline</u></b>``
- ``<b>bold <i>italic <u>underline <s>strike</s></u></i></b>``
- ``<b>bold <i>and</b> italic</i>``

**Combined**:

- ``--you can combine <i>HTML</i> with **Markdown**--``
- ``**and also <i>overlap** --entities</i> this way--``


-----

RichText (Rich Media Text Formatting)
--------------------------------------

RichText is used for Instant View page blocks, article rendering and inline rich media formatting.
It is a different wire format from MessageEntity-based text formatting and supports advanced decorations
such as LaTeX mathematical formulas, subscripts, superscripts, highlighted text backgrounds, and named anchors.

For complete guides, usage tutorials, and working code examples:

- See :doc:`Rich Text Formatting </topics/rich-text>` for comprehensive details on syntax, formulas, and supported types.
- See :doc:`Rich Messages </features/rich-messages>` for sending structured bot documents with headings, tables, and media.
