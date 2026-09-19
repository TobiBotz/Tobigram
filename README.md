<p align="center">
    <a href="https://github.com/TobiBotz/Tobigram">
        <img
            src="https://raw.githubusercontent.com/TobiBotz/Tobigram/dev/assets/pyrogram-logo.png"
            alt="Tobigram"
            width="128"
        />
    </a>
    <br />
    <b>Telegram MTProto API Framework for Python</b>
    <br />
    <a href="https://tobigram.com"> Homepage </a>
    •
    <a href="https://docs.tobigram.com"> Documentation </a>
    •
    <a href="https://t.me/TobigramNews"> News </a>
    •
    <a href="https://t.me/TobigramChat"> Chat </a>
    <br />
    <br />
    <a href="https://pypi.org/project/tobigram/">
        <img
            src="https://img.shields.io/pypi/v/Tobigram"
            alt="PyPI package version"
        />
    </a>
    <a href="https://pypi.org/project/tobigram/">
        <img
            src="https://img.shields.io/pypi/dm/Tobigram"
            alt="Downloads"
        />
    </a>
    <a href="https://pypi.org/project/tobigram/">
        <img
            src="https://img.shields.io/pypi/pyversions/Tobigram"
            alt="Python versions"
        />
    </a>
    <a href="https://github.com/TobiBotz/Tobigram/blob/dev/COPYING.lesser">
        <img
            src="https://img.shields.io/github/license/TobiBotz/Tobigram"
            alt="License"
        />
    </a>
</p>


## Tobigram

> Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots

Tobigram is an actively maintained Pyrogram fork for Python designed as a drop-in replacement for Pyrogram. Tobigram provides support for the latest Telegram features including Gifts, Stories, Topics, Business Accounts, and more.

```python
from pyrogram import Client, filters

app = Client("my_account")


@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from Tobigram!")


app.run()
```

**Tobigram** is a modern, elegant and asynchronous [MTProto API](https://docs.tobigram.com/topics/mtproto-vs-botapi) framework. It enables you to easily interact with the main Telegram API through a user account (custom client) or a bot identity (bot API alternative) using Python.

### Key Features

- **Ready**: Install Tobigram with `pip` or `uv` and start building your applications right away.
- **Drop-in Replacement**: 100% compatible with Pyrogram codebases — keep your existing imports with zero migration hassle.
- **Fast**: Boosted up by [WarpCrypto](https://github.com/TobiBotz/WarpCrypto), a high-performance cryptography library written in Rust.
- **Up-to-Date**: First-class support for Star Gifts, Stories, Forum Topics, Business Connections, and Reaction effects.
- **High-Speed Transfers**: Parallel DC chunk streaming with adaptive rate limiting and session pooling.
- **Advanced Proxy Support**: Built-in support for MTProxy (EE Fake-TLS with SNI), MTProto Web Proxy (WebSocket/TLS 1.3), and SOCKS5/HTTP.
- **Modern Python**: Fully compatible with Python 3.10 through Python 3.14+.
- **Type-hinted**: Comprehensive type hints across all methods and types for excellent editor autocomplete.
- **Async**: Fully asynchronous with native async/await for peak concurrency and responsiveness.
- **Powerful**: Full access to Telegram's MTProto API to execute any official client action and more.

### Installing

Stable version

```bash
pip install tobigram
```

Using uv (Recommended)

```bash
uv add tobigram
```

Dev version

```bash
pip install https://github.com/TobiBotz/Tobigram/archive/dev.zip --force-reinstall
```

Optional dependencies

```bash
pip install tobigram[fast]     # uvloop for better performance
```

### Resources

- Check out the [docs](https://docs.tobigram.com) to learn more about Tobigram, get started right away and discover more in-depth material for building your client applications.
- Join the [official channel](https://t.me/TobigramNews) and stay tuned for news, updates and announcements.
- Join the [official chat](https://t.me/TobigramChat) to communicate with people.

### Special Thanks

- **[Dan](https://github.com/delivrance)** The original creator of [Pyrogram](https://github.com/pyrogram/pyrogram).
- **[Kurimuzon Akuma](https://github.com/KurimuzonAkuma)** Creator and maintainer of [Kurigram](https://github.com/kurigram-org/kurigram).
- **[Riajul](https://github.com/rjriajul)** Creator of [Wzgram](https://github.com/rjriajul/wzgram) and author of [WarpCrypto](https://github.com/TobiBotz/WarpCrypto).

