# wzgram

[![PyPI](https://img.shields.io/pypi/v/wzgram)](https://pypi.org/project/wzgram/)
[![Python](https://img.shields.io/pypi/pyversions/wzgram)](https://pypi.org/project/wzgram/)
[![Downloads](https://img.shields.io/pypi/dm/wzgram)](https://pypi.org/project/wzgram/)
[![License](https://img.shields.io/github/license/rjriajul/wzgram)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-rjriajul.github.io/blue)](https://rjriajul.github.io/wzgram)

> Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots

wzgram is a **drop-in replacement** for Pyrogram — your existing `from pyrogram import ...` code works without changes, with access to the latest Telegram features including **Gifts, Stories, Topics, Business Accounts**, and more.

```python
from pyrogram import Client, filters

app = Client("my_account")


@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from wzgram!")


app.run()
```

**wzgram** is a modern, elegant and asynchronous [MTProto API](https://docs.pyrogram.org/topics/mtproto-vs-botapi) framework. It enables you to easily interact with the main Telegram API through a user account (custom client) or a bot identity (bot API alternative) using Python.

### Key Features

- **Drop-in Replacement** — Use `from pyrogram import ...`; existing codebases migrate with zero import changes.
- **Up-to-Date** — Supports Gifts, Stories, Topics, Business Accounts, Giveaways, and the latest Telegram layer.
- **Async Natively** — Fully `async`/`await` throughout. Also usable synchronously via `app.run()` for convenience.
- **Type-hinted** — Every type and method is annotated for excellent editor support.
- **Fast** — Boosted by [WarpCrypto](https://github.com/rjriajul/WarpCrypto), a high-performance cryptography library written in Rust.
- **Powerful** — Full access to Telegram's API for any official client action and more.

### Example with Inline Keyboard

```python
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Client("my_bot")


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "Choose an option:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Website", url="https://example.com"),
                InlineKeyboardButton("Help", callback_data="help"),
            ],
            [InlineKeyboardButton("About", callback_data="about")],
        ])
    )


app.run()
```

### Installing

```bash
pip install wzgram
```

For better performance:

```bash
pip install wzgram[fast]
```

### Development

```bash
# Clone the repo
git clone https://github.com/rjriajul/wzgram
cd wzgram

# Install uv (if not already)
pip install uv

# Create virtual environment with dev dependencies
uv sync --frozen --extra dev

# Generate TL API types
uv run poe api

# Run tests
uv run poe test
```

### Documentation

Full documentation at **[https://rjriajul.github.io/wzgram](https://rjriajul.github.io/wzgram)**

### Resources

- [Source code](https://github.com/rjriajul/wzgram)
- [Documentation](https://rjriajul.github.io/wzgram)
- [Issue tracker](https://github.com/rjriajul/wzgram/issues)
- [Contributing guide](CONTRIBUTING.md)
