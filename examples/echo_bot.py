from pyrogram import Client, filters

app = Client(
    "echo_bot",
    api_id=12345,
    api_hash="0123456789abcdef0123456789abcdef",
    bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
)


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "Hello! Send me any message and I'll echo it back."
    )


@app.on_message(filters.text & ~filters.command("start"))
async def echo(client, message):
    await message.reply(message.text)


app.run()
