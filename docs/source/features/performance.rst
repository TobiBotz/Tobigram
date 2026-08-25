Performance and Resource Budgets
================================

*A wzgram extension*

wzgram is tuned for two shapes of deployment that pull in opposite directions: one client
moving files as fast as the link allows, and fifteen clients sharing a 500 MiB host. The
things that make both work are worth knowing, because a few of them are tunable and the rest
explain why the defaults are what they are.


-----

Start-up and resident memory
----------------------------

``pyrogram.raw`` is the TL schema turned into Python: roughly three thousand modules, one
class each. wzgram imports them **on first use**, not all at once, because a client touches
a handful of them and a bot that only uses the high-level API touches almost none.

.. list-table::
    :header-rows: 1
    :widths: 40 20 20 20

    * - ``import wzgram``
      - RSS
      - modules
      - time
    * - importing the whole schema
      - 66.7 MiB
      - 4389
      - 3.1 s
    * - importing it on first use
      - 33.7 MiB
      - 1351
      - 1.0 s

Using two hundred raw constructors afterwards adds 2.3 MiB and 200 modules, so the cost
tracks what a program actually reaches for.

Nothing about this is visible in code: ``raw.types.Message``, ``from pyrogram.raw.types
import *``, ``dir(raw.functions)`` and ``isinstance(x, raw.types.Message)`` all behave as
before. The map from constructor id to class, ``raw.objects``, resolves an entry the first
time that id arrives on the wire rather than building the whole table at import.

There is no polling loop to switch off, and no webhook to configure. MTProto keeps one TCP
connection and the server pushes updates down it; the only periodic work an idle client does
is a keepalive ping, which costs about 13 µs. Long polling and webhooks are Bot API
transports and do not exist here.

Rust crypto
-----------

AES-IGE and AES-CTR run in `WarpCrypto <https://github.com/rjriajul/WarpCrypto>`_, a Rust
extension. It is a hard dependency, not an optional speedup — there is no pure-Python
fallback to fall back to.

Small payloads are encrypted **on the event loop**, not in the crypto thread pool. A 64-byte
control packet costs 1.3 µs to pack and a thread hand-off costs about 110 µs — 85 times the
work being handed off. Above ``WZGRAM_INLINE_CRYPTO_MAX`` (32 KiB) the pool earns its keep
again: a 1 MiB transfer part costs 2.4 ms, which is a stall the loop cannot afford.

Measured end to end: ``Session.send(Ping)`` went from 148.8 µs to 13.0 µs, and
``Session.handle_packet`` from 127.2 µs to 6.7 µs.

Peer cache
----------

``resolve_peer`` runs on every send. Against the session database it cost 126 µs — aiosqlite
runs each statement on its own thread, so every query paid a hand-off. A cache hit costs
0.7 µs.

``WZGRAM_PEER_CACHE`` (4096) is how many peers are held. The cache stores the database *row*,
not the ``InputPeer`` built from it: callers hand those to the API and are free to mutate
them, and rebuilding one costs a microsecond.

Budgets are process-wide
------------------------

Every budget on the transfer path is shared by every client in the process, because a bot
running fifteen clients otherwise multiplied every per-client reservation by fifteen.

``WZGRAM_MAX_READ_AHEAD`` (64) is the single ceiling on how much memory transfers may hold,
whatever the client count. Streaming, disk downloads and uploads all draw on it. The handler
thread pool is shared the same way, through ``WZGRAM_HANDLER_WORKERS``.

Measured with fifteen clients each streaming 60 MiB: 419.5 MiB above baseline before,
62.9 MiB after.

On a small host, tune ``WZGRAM_MAX_READ_AHEAD`` down rather than the per-connection caps.

Per-connection caps
-------------------

``WZGRAM_MAX_INFLIGHT_MEDIA`` (6) caps concurrent requests on one media connection. This is
the fix for transfers timing out past three or four in parallel: each transfer opens about
twelve workers, but the media session pool hands out the same three sessions to everybody, so
in-flight requests scale with transfer count while the deadline does not. Past a threshold
every request breaches it *at once*, and each retry puts another 1 MiB part back on the same
saturated link.

Measured on a 3 MB/s link with 60 MiB files: four parallel transfers gave 93 timeouts and
118 s before, 0 timeouts and 75 s after. It costs no throughput — a saturated link carries the
same bytes per second either way.

``WZGRAM_MAX_INFLIGHT_PACKETS`` (16) caps packets being decrypted at once. The receive loop
acquires *before* the next read, so a full backlog stops draining the socket and the TCP
window throttles the server.

Both are per connection on purpose: they cap latency on one socket, not total memory. A
deployment with many clients on one slow uplink should lower ``WZGRAM_MAX_INFLIGHT_MEDIA``
rather than assume the default protects the link globally.

Environment knobs
-----------------

.. list-table::
    :header-rows: 1
    :widths: 40 15 45

    * - Variable
      - Default
      - What it bounds
    * - ``WZGRAM_WORKERS``
      - cpu + 4
      - dispatcher worker tasks
    * - ``WZGRAM_CRYPTO_WORKERS``
      - 2-4
      - crypto threads, process-wide
    * - ``WZGRAM_HANDLER_WORKERS``
      - cpu-based
      - handler thread pool, process-wide
    * - ``WZGRAM_MAX_READ_AHEAD``
      - 64
      - chunks buffered ahead, process-wide
    * - ``WZGRAM_MAX_INFLIGHT_MEDIA``
      - 6
      - requests per media connection
    * - ``WZGRAM_MAX_INFLIGHT_PACKETS``
      - 16
      - packets decrypting at once
    * - ``WZGRAM_INLINE_CRYPTO_MAX``
      - 32768
      - bytes encrypted on the event loop
    * - ``WZGRAM_PEER_CACHE``
      - 4096
      - peers held in front of the database
    * - ``WZGRAM_MEDIA_TIMEOUT``
      - 60
      - seconds a transfer part may take
    * - ``WZGRAM_MEDIA_SESSION_IDLE_TIMEOUT``
      - 300
      - seconds before a pooled session is reaped
    * - ``WZGRAM_TCP_TIMEOUT``
      - 10
      - seconds on a socket read
    * - ``WZGRAM_TCP_CONNECT_TIMEOUT``
      - 600
      - seconds to establish a connection
    * - ``WZGRAM_SOCKET_BUFFER``
      - 0
      - socket buffer size; 0 leaves autotuning on
    * - ``WZGRAM_MAX_LISTENERS``
      - 1000
      - outstanding listeners, process-wide

Setting ``WZGRAM_SOCKET_BUFFER`` at all disables kernel autotuning, which costs fixed memory
per session and caps throughput on high-latency links. That is why the default is 0.

Gotchas
-------

- Raising ``WZGRAM_MAX_INFLIGHT_MEDIA`` does not make transfers faster. A saturated link is
  saturated; more in flight only means more requests sharing one deadline.
- ``WZGRAM_INLINE_CRYPTO_MAX=0`` restores the old always-use-a-thread behaviour, which is
  useful for comparison and slower in every measurement taken.
- Read-ahead is a shared budget, so an abandoned ``stream_media`` that never returns its
  chunks bleeds it away for everybody. Let the generator close — do not abandon it mid-file.
