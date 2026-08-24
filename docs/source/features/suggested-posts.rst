Suggested Posts
===============

*Bot API 9.2 — August 2025*

A suggested post is a paid pitch. Someone proposes a message to a channel, naming a price
and a publication time; the channel's admins approve it, and the post goes out at that time
with the payment settled. Declining costs nothing.

Suggestions travel through the channel's **direct messages** chat, so this feature and
:doc:`direct-messages` are two halves of the same mechanism.


-----

Proposing a post
----------------

Every ``send_*`` method takes ``suggested_post_parameters``. Passing it turns an ordinary
send into a proposal:

.. code-block:: python

    from datetime import datetime, timedelta
    from wzgram.types import SuggestedPostParameters, SuggestedPostPriceStar

    await app.send_photo(
        chat_id=channel_direct_messages_id,
        photo="ad.jpg",
        caption="Our new collection — 20% off this week",
        suggested_post_parameters=SuggestedPostParameters(
            price=SuggestedPostPriceStar(star_count=500),
            send_date=datetime.now() + timedelta(days=1),
        ),
    )

Price is a union, matching how Telegram settles the payment:
:obj:`~pyrogram.types.SuggestedPostPriceStar` for Stars, and
:obj:`~pyrogram.types.SuggestedPostPriceTon` with ``toncoin_nano_count`` for TON. Omit
``price`` for a free suggestion, and omit ``send_date`` to leave the timing to the admin.

Approving and declining
-----------------------

.. code-block:: python

    @app.on_message()
    async def review(client, message):
        if not message.suggested_post_info:
            return

        info = message.suggested_post_info

        if info.price and info.price.star_count >= 500:
            await app.approve_suggested_post(
                chat_id=message.chat.id,
                message_id=message.id,
            )
        else:
            await app.decline_suggested_post(
                chat_id=message.chat.id,
                message_id=message.id,
                comment="Below our minimum rate.",
            )

:meth:`~pyrogram.Client.approve_suggested_post` takes an optional ``send_date`` — pass it to
publish at a different time than the one proposed, omit it to accept the proposed one. It
must be within 30 days.

:meth:`~pyrogram.Client.decline_suggested_post` takes an optional ``comment`` that reaches
the person who proposed it.

Following the outcome
---------------------

A suggestion's state is on the message itself, in
:obj:`~pyrogram.types.SuggestedPostInfo`:

.. code-block:: python

    info = message.suggested_post_info

    print(info.state)      # PENDING, APPROVED or DECLINED
    print(info.send_date)  # when it will be published
    print(info.price)

Telegram also posts service messages as the suggestion moves along, and wzgram parses each
into its own field on :obj:`~pyrogram.types.Message`:
``suggested_post_approved``, ``suggested_post_declined``, ``suggested_post_paid``,
``suggested_post_refunded`` and ``suggested_post_approval_failed`` — the last one being an
approval that could not be charged.

Gotchas
-------

- Send the proposal to the channel's **direct messages** chat, not to the channel. Sending
  to the channel itself either fails or posts immediately, depending on your rights.
- ``price`` is a union, not a number. ``SuggestedPostPriceStar`` and
  ``SuggestedPostPriceTon`` carry different fields, so check which one you have before
  reading ``star_count``.
- An approved post is not a sent post. It is scheduled; the payment settles when it
  publishes, which is when ``suggested_post_paid`` arrives.
