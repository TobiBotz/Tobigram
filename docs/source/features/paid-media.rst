Paid Media
==========

*Bot API 7.6 — July 2024, opened to any chat in 7.9*

Paid media is a photo or video that arrives blurred. The recipient pays a number of
Telegram Stars to unlock it, and the payment goes to whoever sent it. Nothing about the
upload changes: it is an ordinary album with a price attached.


-----

Sending
-------

:meth:`~pyrogram.Client.send_paid_media` takes the price in Stars and a list of
:obj:`~pyrogram.types.InputMediaPhoto` / :obj:`~pyrogram.types.InputMediaVideo`:

.. code-block:: python

    from pyrogram.types import InputMediaPhoto, InputMediaVideo

    await app.send_paid_media(
        chat_id="my_channel",
        stars_amount=25,
        media=[
            InputMediaPhoto("cover.jpg"),
            InputMediaVideo("clip.mp4"),
        ],
        caption="Behind the scenes from today's shoot",
    )

The caption is **not** paid: everyone sees it, which is what makes it the sales pitch. Only
the media behind it is locked.

``payload`` is a string of your own that comes back to you when someone pays, so you can tie
a purchase to a record on your side without a database lookup on the caption.

Knowing who paid
----------------

When a user unlocks paid media a bot sent, the bot is told:

.. code-block:: python

    @app.on_purchased_paid_media()
    async def paid(client, purchase):
        print(f"{purchase.from_user.id} unlocked, payload={purchase.payload}")

Reading it back
---------------

On a message that carries paid media, ``message.paid_media`` holds a
:obj:`~pyrogram.types.PaidMediaInfo`: ``stars_amount`` is the price, and ``media`` is the
list of items. Until the viewer pays, each item is a :obj:`~pyrogram.types.PaidMediaPreview`
— dimensions and a blurred thumbnail, with no file to download. After payment the same list
holds real :obj:`~pyrogram.types.Photo` and :obj:`~pyrogram.types.Video` objects.

Gotchas
-------

- ``stars_amount`` is per message, not per item. A five-photo album unlocks as one purchase.
- Sending paid media to a channel requires the channel to be eligible for Stars payouts;
  the API rejects it otherwise rather than sending it unpaid.
- A bot cannot unlock paid media on a user's behalf, and a user session cannot buy media
  through the API without going through the normal payment form.
