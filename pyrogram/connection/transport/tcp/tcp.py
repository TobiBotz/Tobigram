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

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import socket
import time
from typing import ClassVar, Final, NamedTuple, TYPE_CHECKING

from python_socks import ProxyType
from python_socks.async_.asyncio import Proxy as SocksProxy

from pyrogram import utils
from pyrogram.crypto import aes, faketls
from pyrogram.crypto.executor import get_crypto_executor
from pyrogram.enums import ProxyScheme

from ...proxy import (
    MARKED_SECRET_SIZE,
    HttpProxy,
    MtProxy,
    Proxy,
    Socks4Proxy,
    Socks5Proxy,
    WebProxy,
    normalize_proxy,
    uses_random_padding,
)
from .faketls_records import (
    GREETING_RESPONSE_PREFIXES,
    RECORD_LENGTH_SIZE,
    FakeTlsRecords,
)
from .web_proxy_carrier import WebCarrierError, WebProxyCarrier

if TYPE_CHECKING:
    from concurrent.futures import ThreadPoolExecutor

log = logging.getLogger(__name__)


# --- MTProxy "obfuscated2" handshake -------------------------------------

_OBFUSCATED2_RESERVED_PREFIXES: Final[tuple[bytes, ...]] = (
    b"HEAD",
    b"POST",
    b"GET ",
    b"OPTI",
    b"\xdd\xdd\xdd\xdd",
    b"\xee\xee\xee\xee",
    b"\x16\x03\x01\x02",
)

ABRIDGED_OBFUSCATE_TAG: Final[bytes] = b"\xef\xef\xef\xef"
INTERMEDIATE_PADDED_OBFUSCATE_TAG: Final[bytes] = b"\xdd\xdd\xdd\xdd"

CipherArgs = tuple[bytes, bytearray, bytearray]  # (key, iv, state) for aes.ctr256_{en,de}crypt


def generate_obfuscated2_nonce(
    reserved_prefixes: tuple[bytes, ...] = _OBFUSCATED2_RESERVED_PREFIXES,
) -> bytearray:
    while True:
        nonce = bytearray(os.urandom(64))
        if (
            nonce[0] != 0xEF
            and bytes(nonce[:4]) not in reserved_prefixes
            and nonce[4:8] != b"\x00\x00\x00\x00"
        ):
            return nonce


def finalize_obfuscated2_tag(nonce: bytearray, encrypt: CipherArgs) -> bytes:
    return aes.ctr256_encrypt(bytes(nonce), *encrypt)[56:64]


class Obfuscated2Header(NamedTuple):
    header: bytes
    encrypt: CipherArgs
    decrypt: CipherArgs


def build_obfuscated2_header(secret: bytes, dc_id: int, obfuscate_tag: bytes) -> Obfuscated2Header:
    if len(secret) != 16:
        raise ValueError(f"obfuscated2: secret must be exactly 16 bytes, got {len(secret)}")
    if len(obfuscate_tag) != 4:
        raise ValueError("obfuscated2: obfuscate_tag must be exactly 4 bytes")

    nonce = generate_obfuscated2_nonce()
    reversed_tail = bytearray(nonce[55:7:-1])

    encrypt_key = hashlib.sha256(bytes(nonce[8:40]) + secret).digest()
    encrypt_iv = bytearray(nonce[40:56])
    decrypt_key = hashlib.sha256(bytes(reversed_tail[0:32]) + secret).digest()
    decrypt_iv = bytearray(reversed_tail[32:48])

    encrypt: CipherArgs = (encrypt_key, encrypt_iv, bytearray(1))
    decrypt: CipherArgs = (decrypt_key, decrypt_iv, bytearray(1))

    nonce[56:60] = obfuscate_tag
    nonce[60:62] = dc_id.to_bytes(2, "little", signed=True)
    nonce[56:64] = finalize_obfuscated2_tag(nonce, encrypt)

    return Obfuscated2Header(header=bytes(nonce), encrypt=encrypt, decrypt=decrypt)


# The schemes `python_socks` dials for us, and its name for each.
_PYTHON_SOCKS_TYPES: Final[dict[ProxyScheme, ProxyType]] = {
    ProxyScheme.SOCKS4: ProxyType.SOCKS4,
    ProxyScheme.SOCKS5: ProxyType.SOCKS5,
    ProxyScheme.HTTP: ProxyType.HTTP,
}


class TCP:
    TIMEOUT = int(os.environ.get("PYROGRAM_TCP_TIMEOUT", 10))
    CONNECT_TIMEOUT = int(os.environ.get("PYROGRAM_TCP_CONNECT_TIMEOUT", 600))

    SOCKET_BUFFER = int(os.environ.get("PYROGRAM_SOCKET_BUFFER", 0))

    MAX_FRAME_SIZE = 0xFFFFFF * 4

    OBFUSCATE_TAG: ClassVar[bytes | None] = None

    def __init__(
        self,
        ipv6: bool = False,
        proxy: dict | str | Proxy | None = None,
        crypto_executor: ThreadPoolExecutor | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
        dc_id: int | None = None,
    ):
        self.is_connected = False
        self.mid_message = False

        self.reader = None
        self.writer = None

        self.lock = asyncio.Lock()
        if isinstance(loop, asyncio.AbstractEventLoop):
            self.loop = loop
        else:
            self.loop = utils.get_event_loop()

        self.proxy: Proxy | None = normalize_proxy(proxy)
        self.dc_id = dc_id
        self.crypto_executor = crypto_executor or get_crypto_executor()

        self._web_carrier: WebProxyCarrier | None = None
        self._records: FakeTlsRecords | None = None
        self._web_recv_buffer = bytearray()
        self._encrypt: CipherArgs | None = None
        self._decrypt: CipherArgs | None = None

        if self.proxy is None:
            self.socket = socket.socket(socket.AF_INET6 if ipv6 else socket.AF_INET)
            self.socket.setblocking(False)
        else:
            self.socket = None

    @property
    def is_web_proxy(self) -> bool:
        return isinstance(self.proxy, WebProxy)

    @property
    def is_mtproxy(self) -> bool:
        return isinstance(self.proxy, MtProxy)

    @property
    def opens_with_obfuscated2_header(self) -> bool:
        return isinstance(self.proxy, (WebProxy, MtProxy))

    def _obfuscated2_secret(self, secret: bytes) -> bytes:
        if self.dc_id is None:
            raise ValueError(
                "An obfuscated2 proxy scheme requires a dc_id, passed through by Connection"
            )

        if not self.OBFUSCATE_TAG:
            raise ValueError(
                f"{type(self).__name__} has no OBFUSCATE_TAG and cannot speak obfuscated2; use "
                f"e.g. TCPAbridged for a plain secret, TCPIntermediatePadded for dd"
            )

        if (
            uses_random_padding(self.proxy)
            and self.OBFUSCATE_TAG != INTERMEDIATE_PADDED_OBFUSCATE_TAG
        ):
            raise ValueError(
                f"this proxy's secret asks for random padding, which {type(self).__name__} "
                f"does not send; use TCPIntermediatePadded"
            )

        if len(secret) == MARKED_SECRET_SIZE:
            return secret[1:]

        return secret

    async def _connect_via_web_proxy(self) -> None:
        web_proxy: WebProxy = self.proxy
        bare_secret = self._obfuscated2_secret(web_proxy.secret)

        log.info("Connecting to WEB proxy relay %s (dc_id=%s)", web_proxy.hostname, self.dc_id)

        carrier = WebProxyCarrier(web_proxy.hostname, web_proxy.secret, loop=self.loop)
        self._web_carrier = carrier
        try:
            await carrier.start()
        except WebCarrierError as e:
            self._web_carrier = None
            await carrier.close()
            raise OSError(str(e)) from e

        built = build_obfuscated2_header(bare_secret, self.dc_id, self.OBFUSCATE_TAG)
        self._encrypt = built.encrypt
        self._decrypt = built.decrypt

        try:
            await carrier.send(built.header)
        except WebCarrierError as e:
            self._web_carrier = None
            await carrier.close()
            raise OSError(str(e)) from e

        log.info("WEB proxy carrier established")
        self.is_connected = True

    async def _connect_via_mtproxy(self) -> None:
        mt_proxy: MtProxy = self.proxy
        bare_secret = self._obfuscated2_secret(mt_proxy.secret)

        log.info(
            "Connecting to MTProxy %s:%s (dc_id=%s)", mt_proxy.hostname, mt_proxy.port, self.dc_id
        )

        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(
                    host=mt_proxy.hostname,
                    port=mt_proxy.port,
                    family=socket.AF_UNSPEC,
                ),
                TCP.CONNECT_TIMEOUT,
            )
        except asyncio.TimeoutError:
            raise TimeoutError("MTProxy connection timed out")
        except OSError as e:
            raise OSError(
                f"Failed to connect to MTProxy {mt_proxy.hostname}:{mt_proxy.port}: {e}"
            ) from e

        sock = self.writer.get_extra_info("socket")
        if sock is not None:
            self.socket = sock
            try:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

                if TCP.SOCKET_BUFFER > 0:
                    for option in (socket.SO_SNDBUF, socket.SO_RCVBUF):
                        if TCP.SOCKET_BUFFER > sock.getsockopt(socket.SOL_SOCKET, option):
                            sock.setsockopt(socket.SOL_SOCKET, option, TCP.SOCKET_BUFFER)
            except OSError:
                pass

        built = build_obfuscated2_header(bare_secret, self.dc_id, self.OBFUSCATE_TAG)

        if mt_proxy.sni_hostname is None:
            self.writer.write(built.header)
            await self.writer.drain()
        else:
            await self._greet_fake_tls_proxy(domain=mt_proxy.sni_hostname, secret=bare_secret)
            self._records = FakeTlsRecords(self._recv_from_socket, prologue=built.header)

        self._encrypt = built.encrypt
        self._decrypt = built.decrypt
        self.is_connected = True

    async def _greet_fake_tls_proxy(self, *, domain: str, secret: bytes) -> None:
        hello = faketls.build_client_hello(domain=domain, secret=secret, unix_time=int(time.time()))

        log.info("Greeting the fake-TLS MTProxy as %s", domain)

        self.writer.write(hello.record)
        await self.writer.drain()

        response = await self._read_greeting_response()

        if not faketls.server_hello_is_authentic(
            response, secret=secret, client_random=hello.random
        ):
            raise OSError(
                f"fake-TLS: {domain} answered the greeting without knowing the proxy secret"
            )

        log.info("Fake-TLS greeting answered")

    async def _read_greeting_response(self) -> bytes:
        response = bytearray()

        for prefix in GREETING_RESPONSE_PREFIXES:
            head = await self._recv_from_socket(len(prefix) + RECORD_LENGTH_SIZE)

            if head is None or head[: len(prefix)] != prefix:
                raise OSError("fake-TLS: the greeting was not answered with a ServerHello")

            body = await self._recv_from_socket(int.from_bytes(head[-RECORD_LENGTH_SIZE:], "big"))

            if body is None:
                raise OSError("fake-TLS: the connection closed inside the ServerHello")

            response += head + body

        return bytes(response)

    async def _build_proxy(self) -> SocksProxy:
        proxy = self.proxy

        if not isinstance(proxy, (Socks4Proxy, Socks5Proxy, HttpProxy)):
            msg = f"{type(proxy).__name__} cannot be dialed as a SOCKS/HTTP proxy"
            raise ValueError(msg)

        return SocksProxy(
            proxy_type=_PYTHON_SOCKS_TYPES[proxy.scheme],
            host=proxy.hostname,
            port=proxy.port,
            username=proxy.username,
            password=proxy.password,
        )

    async def _connect_via_proxy(self, destination: tuple[str, int]) -> None:
        dest_host, dest_port = destination
        proxy = await self._build_proxy()

        log.info(
            "Connecting to %s:%s via proxy %s",
            dest_host,
            dest_port,
            self.proxy,
        )

        try:
            sock = await proxy.connect(
                dest_host=dest_host,
                dest_port=dest_port,
                timeout=TCP.CONNECT_TIMEOUT,
            )
        except Exception as e:
            log.error("Proxy connection failed: %s %s", type(e).__name__, e)
            raise

        self.socket = sock
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            if TCP.SOCKET_BUFFER > 0:
                for option in (socket.SO_SNDBUF, socket.SO_RCVBUF):
                    if TCP.SOCKET_BUFFER > sock.getsockopt(socket.SOL_SOCKET, option):
                        sock.setsockopt(socket.SOL_SOCKET, option, TCP.SOCKET_BUFFER)
        except OSError:
            pass

        log.info("Proxy connection established")
        self.reader, self.writer = await asyncio.open_connection(sock=sock)

    async def connect(self, address: tuple):
        if isinstance(self.proxy, WebProxy):
            await self._connect_via_web_proxy()
            return
        elif isinstance(self.proxy, MtProxy):
            await self._connect_via_mtproxy()
            return
        elif isinstance(self.proxy, (Socks4Proxy, Socks5Proxy, HttpProxy)):
            await self._connect_via_proxy(address)
        else:
            try:
                await asyncio.wait_for(
                    self.loop.sock_connect(self.socket, address), TCP.CONNECT_TIMEOUT
                )
            except asyncio.TimeoutError:
                raise TimeoutError("Connection timed out")

            self.reader, self.writer = await asyncio.open_connection(sock=self.socket)

            try:
                sock = self.writer.get_extra_info("socket")
                if sock is not None:
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

                    if TCP.SOCKET_BUFFER > 0:
                        for option in (socket.SO_SNDBUF, socket.SO_RCVBUF):
                            if TCP.SOCKET_BUFFER > sock.getsockopt(socket.SOL_SOCKET, option):
                                sock.setsockopt(socket.SOL_SOCKET, option, TCP.SOCKET_BUFFER)
            except OSError:
                pass

        self.is_connected = True

    async def close(self):
        self.is_connected = False
        self._records = None

        if self._web_carrier is not None:
            carrier, self._web_carrier = self._web_carrier, None
            try:
                await carrier.close()
            except Exception as e:
                log.info("WEB proxy close exception: %s %s", type(e).__name__, e)
            return

        try:
            if self.writer is not None:
                self.writer.close()
                await asyncio.wait_for(self.writer.wait_closed(), TCP.TIMEOUT)
            elif self.socket is not None:
                self.socket.close()
        except Exception as e:
            log.info("Close exception: %s %s", type(e).__name__, e)
        finally:
            if self.socket is not None:
                try:
                    self.socket.close()
                except Exception:
                    pass

    async def send(self, data: bytes):
        async with self.lock:
            if not self.is_connected:
                raise OSError("Connection closed")

            if self._encrypt is not None:
                data = await self.loop.run_in_executor(
                    self.crypto_executor, aes.ctr256_encrypt, data, *self._encrypt
                )

            try:
                if self._web_carrier is not None:
                    await self._web_carrier.send(data)
                elif self.writer is not None:
                    if self._records is not None:
                        data = self._records.wrap(data)
                    self.writer.write(data)
                    await self.writer.drain()
            except Exception as e:
                log.info("Send exception: %s %s", type(e).__name__, e)
                raise OSError(e)

    async def recv(self, length: int = 0) -> bytes | None:
        if length <= 0:
            return b""

        if length > TCP.MAX_FRAME_SIZE:
            raise OSError(f"Frame of {length} bytes exceeds the {TCP.MAX_FRAME_SIZE} byte limit")

        if self._web_carrier is not None:
            data = await self._recv_from_web_proxy(length)
        elif self._records is not None:
            data = await self._records.recv(length)
        else:
            data = await self._recv_from_socket(length)

        if data is not None and self._decrypt is not None:
            data = await self.loop.run_in_executor(
                self.crypto_executor, aes.ctr256_decrypt, data, *self._decrypt
            )

        return data

    async def _recv_from_web_proxy(self, length: int) -> bytes | None:
        while len(self._web_recv_buffer) < length:
            try:
                chunk = await asyncio.wait_for(self._web_carrier.recv(), TCP.TIMEOUT)
            except asyncio.TimeoutError:
                if len(self._web_recv_buffer) > 0 or self.mid_message:
                    raise OSError("Connection desynchronised mid-message")
                raise TimeoutError("Socket read timed out")

            if chunk is None:
                return None
            self._web_recv_buffer.extend(chunk)

        result = bytes(self._web_recv_buffer[:length])
        del self._web_recv_buffer[:length]
        self.mid_message = True
        await self._web_carrier.grant_credit(length)
        return result

    async def _recv_from_socket(self, length: int) -> bytes | None:
        if not self.reader:
            return None

        chunks = []
        received = 0

        while received < length:
            try:
                chunk = await asyncio.wait_for(self.reader.read(length - received), TCP.TIMEOUT)
            except asyncio.TimeoutError:
                if received or self.mid_message:
                    raise OSError("Connection desynchronised mid-message")

                raise TimeoutError("Socket read timed out")
            except OSError:
                return None

            if not chunk:
                return None

            chunks.append(chunk)
            received += len(chunk)
            self.mid_message = True

        return chunks[0] if len(chunks) == 1 else b"".join(chunks)
