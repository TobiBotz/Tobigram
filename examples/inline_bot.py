from pyrogram import Client, filters
from pyrogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
)

app = Client(
    "inline_bot",
    api_id=12345,
    api_hash="0123456789abcdef0123456789abcdef",
    bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
)


@app.on_inline_query()
async def inline(client, query):
    results = [
        InlineQueryResultArticle(
            title="Bold",
            input_message_content=InputTextMessageContent(
                f"**{query.query}**"
            )
        ),
        InlineQueryResultArticle(
            title="Italic",
            input_message_content=InputTextMessageContent(
                f"__{query.query}__"
            )
        ),
    ]

    await query.answer(results)


app.run()
