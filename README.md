<p align="center">
    <b>Telegram MTProto API Framework for Python</b>
    <br>
    <a href="https://github.com/rjriajul/wzgram">
        Homepage
    </a>
    •
    <a href="https://github.com/rjriajul/wzgram">
        Documentation
    </a>
    <br/>
</p>

## wzgram

> Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots

wzgram is a fork of Pyrogram providing support for the latest Telegram features including Gifts, Stories, Topics, Business Accounts, and more.

```python
from pyrogram import Client, filters

app = Client("my_account")


@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from wzgram!")


app.run()
```

**wzgram** is a modern, elegant and asynchronous [MTProto API](https://docs.pyrogram.org/topics/mtproto-vs-botapi)
framework. It enables you to easily interact with the main Telegram API through a user account (custom client) or a bot
identity (bot API alternative) using Python.

### Key Features

- **Ready**: Install wzgram with pip and start building your applications right away.
- **Easy**: Makes the Telegram API simple and intuitive, while still allowing advanced usages.
- **Elegant**: Low-level details are abstracted and re-presented in a more convenient way.
- **Fast**: Boosted up by [TgCrypto](https://github.com/pyrogram/tgcrypto), a high-performance cryptography library written in C.
- **Type-hinted**: Types and methods are all type-hinted, enabling excellent editor support.
- **Async**: Fully asynchronous (also usable synchronously if wanted, for convenience).
- **Powerful**: Full access to Telegram's API to execute any official client action and more.

### Installing

``` bash
pip install wzgram
```

### Resources

- Check out the [source code](https://github.com/rjriajul/wzgram) to learn more about wzgram.
