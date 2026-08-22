Session Strings
===============

*A wzgram extension*

A session string packs everything a client needs to resume an authorised session — the
datacenter, the auth key, who you are — into one line of text you can move between machines,
put in an environment variable, or hand to a deployment.

wzgram's format adds a checksum and a prefix, and its decoder accepts every format the
library has ever produced.


-----

Exporting
---------

.. code-block:: python

    async with Client("my_account", api_id, api_hash) as app:
        print(await app.export_session_string())

The result starts with ``WZ_``. Using it back is a constructor argument:

.. code-block:: python

    app = Client("my_account", session_string=os.environ["SESSION"])

There is no file on disk in that mode — the string *is* the session. Treat it exactly like a
password: anybody holding it is logged in as you, with no second factor in the way.

What is in it
-------------

The current format carries the datacenter id, whether it is a test session, the 256-byte
auth key, the user id, whether that user is a bot, the api_id, and the server address and
port — followed by a CRC32 of all of it.

Only what the wire format cannot invent is required: ``dc_id``, ``test_mode``, ``auth_key``,
``user_id``, ``is_bot``. An unknown ``api_id`` packs as zero and is read back as absent, then
filled in from the :obj:`~pyrogram.Client` — otherwise the one format that *cannot* carry an
api_id would be the one that could never be re-exported, which is the format whose deprecation
warning asks you to re-export.

An address the string does not carry is resolved from ``dc_id`` at load time, including the
sixteen NUL bytes a v2 string exported before the address was known packs instead of nothing.
A session's stored address always belongs to that session's own datacenter.

The checksum, and repair
------------------------

Session strings get mangled in transit: a newline from a database column, a space from a
copy-paste, a character eaten by a chat client. The CRC32 is what tells a corrupted string
from a merely unfamiliar one.

Decoding tries, in order:

1. the current format, checksum verified;
2. the pre-checksum v2 format, with a warning suggesting a re-export;
3. every legacy layout, with a deprecation warning.

If none of those decode, it tries **repair**: prepending and appending one character, then
two, from the alphabet. A repaired string is only ever accepted when the CRC vouches for it.
Without that rule the auth key handed back would be assembled from a guess, which is worse
than an error.

The ``WZ_`` prefix is stripped whatever the string is wrapped in, and characters outside the
alphabet are dropped before decoding — so a stray newline is not corruption.

Gotchas
-------

- A string exported from a different library may decode and still be a legacy format; the
  warning is asking you to re-export for a reason, not as ceremony.
- Do not commit one. It is not a token that can be rotated from a dashboard — invalidating it
  means terminating the session from a logged-in client.
- ``in_memory=True`` and a session string are the same idea from two directions: neither
  writes a session file, and only the string lets you resume later.
