Features
========

wzgram tracks Telegram's Bot API and MTProto layers closely. This section explains the
features Telegram has shipped over the past releases, in the order they were released, and
shows how to use each one from wzgram.

The pinned Bot API schema wzgram is checked against is **Bot API 10.2 (July 14, 2026)**.
Every parameter of every implemented method and type is verified against it at build time,
so if a feature is documented here, the parameters that carry it are present.

Read top to bottom for the story of how Telegram grew, or jump to what you need.


-----

Telegram Features
-----------------

.. list-table::
    :header-rows: 1
    :widths: 30 15 20 35

    * - Feature
      - Bot API
      - Released
      - What it gives you
    * - :doc:`business-accounts`
      - 7.2
      - March 2024
      - Act on behalf of a user's business account
    * - :doc:`paid-media`
      - 7.6
      - July 2024
      - Photos and videos unlocked with Stars
    * - :doc:`gifts-and-stars`
      - 8.0
      - November 2024
      - Stars balance, gifts, upgrades, resale, auctions
    * - :doc:`stories`
      - 9.0
      - April 2025
      - Post, edit and read stories
    * - :doc:`checklists`
      - 9.1
      - July 2025
      - Shared to-do lists inside a message
    * - :doc:`suggested-posts`
      - 9.2
      - August 2025
      - Propose a paid post to a channel and approve it
    * - :doc:`direct-messages`
      - 9.2
      - August 2025
      - Per-user topics in a channel's direct messages tab
    * - :doc:`chat-topics-drafts`
      - 9.3
      - December 2025
      - Forum topics, private chat topics, message drafts
    * - :doc:`text-entities`
      - 9.5
      - March 2026
      - Date/time entities, custom emoji, styled buttons
    * - :doc:`polls`
      - 9.6
      - April 2026
      - Multiple correct answers, poll media, descriptions
    * - :doc:`guest-mode-and-managed-bots`
      - 10.0
      - May 2026
      - Messages a bot sees without joining; managed bots
    * - :doc:`rich-messages`
      - 10.1
      - June 2026
      - Article-grade documents as a message
    * - :doc:`ephemeral-messages`
      - 10.2
      - July 2026
      - Messages only one user sees, stored nowhere
    * - :doc:`communities`
      - 10.2
      - July 2026
      - Groups of chats presented as one entity

.. toctree::
    :hidden:

    business-accounts
    paid-media
    gifts-and-stars
    stories
    checklists
    suggested-posts
    direct-messages
    chat-topics-drafts
    text-entities
    polls
    guest-mode-and-managed-bots
    rich-messages
    ephemeral-messages
    communities

wzgram Extensions
-----------------

These are not Telegram features. They are things wzgram adds on top of the API, to make
long-running clients behave.

.. list-table::
    :header-rows: 1
    :widths: 30 70

    * - Feature
      - What it gives you
    * - :doc:`listeners`
      - Wait for the next message or callback inline, without a handler
    * - :doc:`rate-limiting`
      - Client-side token buckets that keep you under Telegram's limits
    * - :doc:`session-strings`
      - Checksummed, portable session strings that repair themselves
    * - :doc:`performance`
      - Rust crypto, shared pools and the memory budget for small hosts

.. toctree::
    :hidden:

    listeners
    rate-limiting
    session-strings
    performance
