rich_message
============

This example sends a structured document — headings, a list and a code block — as a single
message.

.. include:: /_includes/usable-by/bots.rst

.. code-block:: python

    from wzgram import Client
    from wzgram.types import (
        InputRichMessage,
        InputRichBlockSectionHeading,
        InputRichBlockParagraph,
        InputRichBlockList,
        InputRichBlockListItem,
        InputRichBlockPreformatted,
        InputRichBlockDivider,
    )

    app = Client("my_bot")


    async def main():
        async with app:
            await app.send_rich_message(
                chat_id="me",
                rich_text=InputRichMessage(blocks=[
                    InputRichBlockSectionHeading(text="Deploy checklist", size=2),
                    InputRichBlockParagraph(text="Run these in order."),
                    InputRichBlockList(
                        items=[
                            InputRichBlockListItem(text="Run the test suite", has_checkbox=True),
                            InputRichBlockListItem(text="Bump the version", has_checkbox=True),
                            InputRichBlockListItem(text="Publish", has_checkbox=True),
                        ],
                        ordered=True,
                    ),
                    InputRichBlockDivider(),
                    InputRichBlockPreformatted(text="uv run poe test", language="bash"),
                ]),
            )


    app.run(main())

The same message can be written as HTML or Markdown instead — pass ``html=`` or
``markdown=`` to :obj:`~pyrogram.types.InputRichMessage`. Exactly one of the three forms is
used, and they carry media differently.

See :doc:`/features/rich-messages`.
