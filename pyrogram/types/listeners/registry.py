#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import heapq
import itertools
import logging
import os
import weakref
from typing import Dict, List, Optional, Tuple

import pyrogram
from pyrogram.errors import ListenerLimitReached, ListenerStopped, ListenerTimeout

from .identifier import Identifier
from .listener import Listener

log = logging.getLogger(__name__)

MAX_LISTENERS = int(os.environ.get("WZGRAM_MAX_LISTENERS", 1000))

_CHAT = 0
_USER = 1
_GLOBAL = 2

_budgets: "weakref.WeakKeyDictionary" = weakref.WeakKeyDictionary()


class ListenerBudget:
    """A process-wide ceiling on outstanding listeners.

    Per-client caps do not compose: fifteen clients each allowed a thousand
    listeners is fifteen thousand futures on one host. The budget is keyed by
    event loop, so every client running on it draws from the same pool.
    """

    __slots__ = ("limit", "used")

    def __init__(self, limit: int):
        self.limit = limit
        self.used = 0

    def acquire(self) -> bool:
        if self.used >= self.limit:
            return False

        self.used += 1
        return True

    def release(self) -> None:
        if self.used:
            self.used -= 1


def listener_budget(limit: int = MAX_LISTENERS) -> ListenerBudget:
    loop = asyncio.get_event_loop()
    budget = _budgets.get(loop)

    if budget is None:
        budget = ListenerBudget(limit)
        _budgets[loop] = budget

    return budget


def _identify(
    listener_type: "pyrogram.enums.ListenerTypes",
    update
) -> Optional[Tuple[Identifier, Optional[int], Optional[int]]]:
    """Reduce an update to the criteria a listener matches against."""
    if listener_type is pyrogram.enums.ListenerTypes.CALLBACK_QUERY:
        message = getattr(update, "message", None)
        chat = getattr(message, "chat", None)
        from_user = getattr(update, "from_user", None)

        chat_id = getattr(chat, "id", None)
        user_id = getattr(from_user, "id", None)

        return (
            Identifier(
                chat_id=chat_id,
                user_id=user_id,
                message_id=getattr(message, "id", None),
                inline_message_id=getattr(update, "inline_message_id", None)
            ),
            chat_id,
            user_id
        )

    if getattr(update, "outgoing", False) or getattr(update, "scheduled", False):
        return None

    chat = getattr(update, "chat", None)
    from_user = getattr(update, "from_user", None)

    chat_id = getattr(chat, "id", None)
    user_id = getattr(from_user, "id", None)

    if user_id is None:
        user_id = getattr(getattr(update, "sender_chat", None), "id", None)

    return (
        Identifier(
            chat_id=chat_id,
            user_id=user_id,
            message_id=getattr(update, "id", None)
        ),
        chat_id,
        user_id
    )


def _as_keys(value) -> List:
    if value is None:
        return []

    return list(value) if isinstance(value, list) else [value]


def _consume_exception(future: asyncio.Future):
    if not future.cancelled():
        future.exception()


async def _invoke(client: "pyrogram.Client", callback, update):
    try:
        if asyncio.iscoroutinefunction(callback):
            await callback(client, update)
        else:
            await client.loop.run_in_executor(client.executor, callback, client, update)
    except Exception:
        log.exception("Listener callback raised")


class ListenerRegistry:
    """Holds the listeners a client is waiting on.

    Lookup is by canonical peer id rather than a scan, so a client with ten
    thousand users mid-conversation probes at most three buckets per update, and
    a client with no listeners at all pays a single ``__bool__``.

    Expiry is driven by one deadline heap and one reaper task rather than a
    ``wait_for`` wrapper per listener, which would make ten thousand waiters ten
    thousand timer handles and ten thousand wrapper tasks.
    """

    __slots__ = (
        "_client", "_live", "_buckets", "_heap", "_stale", "_seq",
        "_wake", "_reaper", "_budget", "closed"
    )

    def __init__(self, client: "pyrogram.Client"):
        self._client = client
        self._live: Dict[int, Listener] = {}
        self._buckets: Dict[Tuple, Dict[int, Listener]] = {}
        self._heap: List[Tuple[float, int, Listener, float]] = []
        self._stale = 0
        self._seq = itertools.count()
        self._wake = asyncio.Event()
        self._reaper: Optional[asyncio.Task] = None
        self._budget: Optional[ListenerBudget] = None
        self.closed = False

    def __bool__(self) -> bool:
        return len(self._live) != 0

    def __len__(self) -> int:
        return len(self._live)

    @property
    def budget(self) -> ListenerBudget:
        if self._budget is None:
            self._budget = listener_budget(
                getattr(self._client, "max_listeners", None) or MAX_LISTENERS
            )

        return self._budget

    def _keys_for(self, listener: Listener) -> Tuple:
        identifier = listener.identifier
        listener_type = listener.listener_type

        chats = _as_keys(identifier.chat_id)

        if chats:
            return tuple((listener_type, _CHAT, chat) for chat in chats)

        users = _as_keys(identifier.user_id)

        if users:
            return tuple((listener_type, _USER, user) for user in users)

        return ((listener_type, _GLOBAL, None),)

    def add(self, listener: Listener, timeout: Optional[float] = None):
        if self.closed:
            raise ListenerStopped("Client is stopping")

        budget = self.budget

        if not budget.acquire():
            raise ListenerLimitReached(budget.limit)

        listener.keys = self._keys_for(listener)
        self._live[id(listener)] = listener

        for key in listener.keys:
            bucket = self._buckets.get(key)

            if bucket is None:
                bucket = self._buckets[key] = {}

            bucket[id(listener)] = listener

        if timeout is not None:
            self._schedule(listener, timeout)

    def remove(self, listener: Listener) -> bool:
        if self._live.pop(id(listener), None) is None:
            return False

        for key in listener.keys:
            bucket = self._buckets.get(key)

            if bucket is not None:
                bucket.pop(id(listener), None)

                if not bucket:
                    del self._buckets[key]

        listener.keys = ()
        self.budget.release()
        self._stale += 1

        return True

    def _schedule(self, listener: Listener, timeout: float):
        heapq.heappush(
            self._heap,
            (self._client.loop.time() + timeout, next(self._seq), listener, timeout)
        )

        if self._reaper is None or self._reaper.done():
            self._reaper = self._client.loop.create_task(self._reap())
            self._reaper.add_done_callback(self._reaper_done)

        self._wake.set()

    @staticmethod
    def _reaper_done(task: asyncio.Task):
        if task.cancelled():
            return

        exc = task.exception()

        if exc is not None:
            log.error("Listener reaper stopped unexpectedly", exc_info=exc)

    def _compact(self):
        if self._stale < 32 or self._stale * 2 < len(self._heap):
            return

        self._heap = [entry for entry in self._heap if id(entry[2]) in self._live]
        heapq.heapify(self._heap)
        self._stale = 0

    async def _reap(self):
        loop = self._client.loop

        while True:
            try:
                self._wake.clear()
                self._compact()

                if not self._heap:
                    await self._wake.wait()
                    continue

                delay = self._heap[0][0] - loop.time()

                if delay > 0:
                    try:
                        await asyncio.wait_for(self._wake.wait(), delay)
                    except asyncio.TimeoutError:
                        pass

                    continue

                _, _, listener, timeout = heapq.heappop(self._heap)

                if not self.remove(listener):
                    continue

                self._fail(listener, ListenerTimeout(timeout))
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("Listener reaper error")
                await asyncio.sleep(0.1)

    @staticmethod
    def _fail(listener: Listener, error: Exception):
        future = listener.future

        if future is not None and not future.done():
            future.set_exception(error)
            future.add_done_callback(_consume_exception)

        listener.detach()

    def stop(self, listener: Listener) -> bool:
        """Abort a single listener. Returns whether it was still pending."""
        if not self.remove(listener):
            return False

        self._fail(listener, ListenerStopped())

        return True

    def find(
        self,
        listener_type: "pyrogram.enums.ListenerTypes",
        pattern: Identifier
    ) -> List[Listener]:
        """Every live listener whose own criteria *pattern* covers."""
        return [
            listener
            for listener in self._live.values()
            if listener.listener_type is listener_type
            and pattern.matches(listener.identifier)
        ]

    def _candidates(
        self,
        listener_type: "pyrogram.enums.ListenerTypes",
        chat_id: Optional[int],
        user_id: Optional[int]
    ) -> List[Listener]:
        found: List[Listener] = []

        for key in (
            (listener_type, _CHAT, chat_id) if chat_id is not None else None,
            (listener_type, _USER, user_id) if user_id is not None else None,
            (listener_type, _GLOBAL, None)
        ):
            if key is None:
                continue

            bucket = self._buckets.get(key)

            if bucket:
                found.extend(bucket.values())

        return found

    async def feed(
        self,
        client: "pyrogram.Client",
        listener_type: "pyrogram.enums.ListenerTypes",
        update
    ) -> bool:
        """Hand an update to a matching listener, reporting whether it was consumed.

        A listener that lost a race to another worker reports False, so the update
        still reaches the handlers. Reporting True there would destroy it.
        """
        identified = _identify(listener_type, update)

        if identified is None:
            return False

        data, chat_id, user_id = identified
        candidates = self._candidates(listener_type, chat_id, user_id)

        if not candidates:
            return False

        stranger: Optional[Listener] = None

        for listener in candidates:
            if not listener.pending:
                continue

            if not listener.identifier.matches(data):
                if stranger is None and self._is_stranger(listener, data):
                    stranger = listener

                continue

            try:
                passed = await pyrogram.filters.check_filter(
                    listener.filters, client, update
                )
            except Exception:
                log.exception("Listener filter raised, ignoring listener")
                continue

            if not passed:
                continue

            if not self.remove(listener):
                continue

            callback = listener.callback

            if callback is not None:
                listener.detach()
                await _invoke(client, callback, update)

                return True

            future = listener.future

            if future is None or future.done():
                continue

            future.set_result(update)
            listener.detach()

            return True

        if stranger is not None:
            return await self._reject(client, stranger, update)

        return False

    @staticmethod
    def _is_stranger(listener: Listener, data: Identifier) -> bool:
        """Whether *listener* wants this exact button, but not from this user."""
        if listener.listener_type is not pyrogram.enums.ListenerTypes.CALLBACK_QUERY:
            return False

        if not listener.unallowed_click_alert:
            return False

        permissive = Identifier(
            chat_id=listener.identifier.chat_id,
            message_id=listener.identifier.message_id,
            inline_message_id=listener.identifier.inline_message_id
        )

        return permissive.matches(data)

    async def _reject(
        self,
        client: "pyrogram.Client",
        listener: Listener,
        update
    ) -> bool:
        if not getattr(client, "unallowed_click_alert", True):
            return False

        alert = listener.unallowed_click_alert

        if not isinstance(alert, str):
            alert = client.unallowed_click_alert_text

        try:
            await update.answer(alert)
        except Exception:
            log.exception("Could not answer an unexpected callback query")

        return True

    async def close(self):
        """Abort every waiter, so shutdown does not hang on them.

        Waiters are walked from the buckets and not from the heap, because a
        listener with no timeout never entered the heap at all. They fail with
        ``ListenerStopped`` and never ``ListenerTimeout``, so a caller that
        retries on timeout does not spin against a stopping client.
        """
        self.closed = True

        for listener in list(self._live.values()):
            self.remove(listener)
            self._fail(listener, ListenerStopped())

        self._buckets.clear()
        self._heap.clear()
        self._stale = 0

        reaper, self._reaper = self._reaper, None

        if reaper is not None and not reaper.done():
            reaper.cancel()

            try:
                await reaper
            except asyncio.CancelledError:
                pass
            except Exception:
                log.exception("Error stopping listener reaper")

    def reopen(self):
        self.closed = False
