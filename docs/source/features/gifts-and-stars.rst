Gifts and Stars
===============

*Bot API 8.0 — November 2024, grown in almost every release since*

Telegram Stars are the platform's in-app currency, and gifts are what people spend them on.
What began as a static sticker attached to a profile has turned into the largest feature
surface Telegram has added: gifts upgrade into unique collectibles, get transferred, resold,
crafted and auctioned.

wzgram exposes the whole chain. This page walks it in the order a gift moves through it.


-----

Stars balance
-------------

.. code-block:: python

    stars = await app.get_stars_balance()
    ton = await app.get_ton_balance()

    print(f"{stars} Stars, {ton} TON")

Pass ``chat_id`` to :meth:`~pyrogram.Client.get_stars_balance` to read a channel's balance
instead of your own.

Sending a gift
--------------

:meth:`~pyrogram.Client.get_available_gifts` lists what is on sale right now — limited gifts
sell out, so the catalogue is not static:

.. code-block:: python

    gifts = await app.get_available_gifts()

    for gift in gifts:
        print(gift.id, gift.star_count, gift.is_limited, gift.is_sold_out)

    await app.send_gift(
        chat_id="me",
        gift_id=gifts[0].id,
        text="Happy birthday!",
        is_private=True,
        pay_for_upgrade=True,
    )

``is_private`` hides the sender's name from other people looking at the recipient's profile.
``pay_for_upgrade`` covers the upgrade cost in advance, so the recipient can turn the gift
into a collectible without spending their own Stars.

Gifts can go to a channel as well as to a user — pass the channel's id as ``chat_id``.

Reading someone's gifts
-----------------------

:meth:`~pyrogram.Client.get_chat_gifts` is an async generator over the gifts a user or
channel has displayed:

.. code-block:: python

    async for gift in app.get_chat_gifts("me", exclude_unsaved=True):
        print(gift.received_gift_id, gift.type, gift.is_pinned)

The ``exclude_*`` flags filter server-side, which matters on profiles holding thousands of
gifts. :meth:`~pyrogram.Client.hide_gift` and :meth:`~pyrogram.Client.show_gift` control
whether one appears on the profile at all, and :meth:`~pyrogram.Client.set_pinned_gifts`
puts a chosen few at the top.

Upgrading to a unique gift
--------------------------

An upgrade turns a mass-produced gift into a one-of-a-kind item with a model, a backdrop, a
pattern and a rarity. :meth:`~pyrogram.Client.get_gift_upgrade_preview` shows the attribute
pool it will be drawn from before you commit:

.. code-block:: python

    preview = await app.get_gift_upgrade_preview(gift_id)

    await app.upgrade_gift(
        owned_gift_id=owned_id,
        keep_original_details=True,
    )

``keep_original_details`` keeps who sent it and when visible on the upgraded item. If the
sender already paid, :meth:`~pyrogram.Client.buy_gift_upgrade` redeems that prepaid upgrade.

Transferring, reselling, crafting, auctioning
---------------------------------------------

Once a gift is unique it becomes an asset, and the API treats it like one:

.. code-block:: python

    # give it away
    await app.transfer_gift(owned_gift_id, new_owner_chat_id="friend_username")

    # put it on the market
    await app.set_gift_resale_price(owned_gift_id, price=resale_price)

    # shop the market
    async for gift in app.search_gifts_for_resale(gift_id, order=enums.GiftForResaleOrder.PRICE):
        print(gift.resale_parameters.star_count)

    # combine several into a new one
    result = await app.craft_gift(owned_gift_ids=[a, b, c])

    # bid in a live auction
    state = await app.get_gift_auction_state(auction_id)
    await app.place_gift_auction_bid(gift_id, star_count=500)

Collections group gifts on a profile the way albums group photos:
:meth:`~pyrogram.Client.create_gift_collection`,
:meth:`~pyrogram.Client.add_collection_gifts`,
:meth:`~pyrogram.Client.reorder_gift_collections` and
:meth:`~pyrogram.Client.set_gift_collection_name`.

Gotchas
-------

- ``gift_id`` and ``owned_gift_id`` are different things. The first identifies the *kind* of
  gift in the catalogue and is an ``int``; the second identifies the specific copy someone
  owns and is a ``str`` — on :obj:`~pyrogram.types.Gift` it is ``received_gift_id``. Passing
  one where the other belongs is the most common mistake here.
- :meth:`~pyrogram.Client.convert_gift_to_stars` is irreversible and pays out less than the
  gift cost. It exists for unwanted gifts, not as a refund.
- Gift attributes are a union, and not every member carries every field —
  ``starGiftAttributeOriginalDetails`` has no rarity, for instance. Read attribute fields
  defensively if you touch :obj:`~pyrogram.types.GiftAttribute` directly.
- Auction and resale prices can be quoted in Stars *or* TON.
  :obj:`~pyrogram.types.GiftResaleParameters` carries ``star_count``, ``toncoin_cent_count``
  and a ``toncoin_only`` flag — do not assume Stars.
