Rate Limiting
=============

*A wzgram extension*

Telegram answers a client that sends too fast with a ``FloodWait``: a number of seconds you
must not send in. wzgram handles those when they arrive — but a limiter that *never lets you
get there* is cheaper than one that recovers afterwards, because a flood wait charges for
the request that triggered it too.

**The limiter is off by default.** A client built without ``rate_limits`` sends without any
client-side throttling and leans on Telegram's own ``FloodWait`` (see ``sleep_threshold``) to
set the pace, which is the fastest option and what upstream Pyrogram does. Pass ``rate_limits``
— even an empty dict, for the defaults below — to turn the limiter on. Once it exists,
:meth:`~pyrogram.Client.invoke` — the choke point every raw call passes through — acquires
from it before the request goes out, and ``app.rate_limiter`` is ``None`` until then.


-----

Categories
----------

Telegram does not enforce one limit; it enforces different ones for different work. The
limiter mirrors that with a token bucket per category and one global bucket over all of them:

===========  ==========  ==========  ==============================================
Category     Rate/s      Burst       Covers
===========  ==========  ==========  ==============================================
``message``  20          30          sending, editing, forwarding text
``media``    5           10          anything carrying a photo, video, audio, file
``query``    30          50          ``Get*``, ``Search*``, ``Check*``
``admin``    15          20          bans, promotions, pins, toggles, deletes
``bulk``     3           5           update-difference fetches, pings
``account``  10          15          account-level changes
``global``   30          40          everything, on top of its own category
===========  ==========  ==========  ==============================================

A request is classified from the name of the raw function it wraps, so a new method lands in
the right bucket without anything being registered by hand.

Tuning it
---------

Pass ``rate_limits`` to the client. Only the categories you name are changed; the rest keep
the defaults in the table above:

.. code-block:: python

    app = Client(
        "my_bot",
        rate_limits={
            "media": {"rate": 2, "burst": 4},
            "global": {"rate": 15, "burst": 20},
        },
    )

    # Or take every default as-is:
    app = Client("my_bot", rate_limits={})

Lower is slower and safer. The defaults are already below what Telegram publishes, so raising
them is how you get flood waits.

Reading the pressure
--------------------

Only when the limiter is enabled — ``app.rate_limiter`` is ``None`` otherwise:

.. code-block:: python

    print(app.rate_limiter.congestion())  # 0.0 idle … 1.0 saturated
    print(app.rate_limiter.available)     # tokens left per category

``congestion()`` is the worst bucket, not the average — it answers "am I about to be
throttled", which is the question worth asking. A long-running job can use it to back off
before the limiter has to make it wait.

``acquire_nowait()`` takes a token only if one is free and reports whether it did, for work that would rather be skipped
than delayed. ``update_limits`` changes the limits on a live client.

How the bucket behaves
----------------------

Two properties are load-bearing, and both were bugs before they were properties:

- **The wait is served holding the lock.** Sleeping outside it woke every waiter at once for
  a single token, and a deficit of a fraction of a token makes that sleep microseconds long
  — a spin, under exactly the load the limiter exists for. Five waiters cost twenty sleeps.
- **Admission is in arrival order.** ``asyncio.Lock`` hands over in order, so holding it
  across the sleep also means a waiter cannot be starved by later arrivals.

Gotchas
-------

- The limiter is per client. Two clients in one process do not share buckets, so N clients
  on one account can still flood — lower the limits rather than assuming they compose.
- It bounds requests per second, not bytes. A slow uploader is not what it protects against;
  that is :doc:`performance`.
- ``sleep_threshold`` on the client is the other half of this: it decides how long a
  ``FloodWait`` wzgram will sit out for you rather than raise. The limiter tries to keep you
  from ever finding out.
