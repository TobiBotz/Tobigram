import os
from hashlib import sha1
from io import BytesIO

import pytest

from pyrogram import raw
from pyrogram.crypto import mtproto, aes
from pyrogram.session.internals import MsgFactory


class TestKdf:
    def test_kdf_returns_key_iv(self, auth_key):
        msg_key = os.urandom(16)
        key, iv = mtproto.kdf(auth_key, msg_key, True)
        assert len(key) == 32
        assert len(iv) == 32

    def test_kdf_outgoing_vs_incoming(self, auth_key):
        msg_key = os.urandom(16)
        key_out, iv_out = mtproto.kdf(auth_key, msg_key, True)
        key_in, iv_in = mtproto.kdf(auth_key, msg_key, False)
        assert key_out != key_in
        assert iv_out != iv_in


class TestPackStructure:
    def test_pack_includes_auth_key_id(self, auth_key, session_id, auth_key_id):
        factory = MsgFactory()
        body = raw.functions.Ping(ping_id=0)
        msg = factory(body)
        packed = mtproto.pack(msg, 0, session_id, auth_key, auth_key_id)
        assert packed[:8] == auth_key_id

    def test_pack_includes_msg_key(self, auth_key, session_id, auth_key_id):
        factory = MsgFactory()
        body = raw.functions.Ping(ping_id=0)
        msg = factory(body)
        packed = mtproto.pack(msg, 0, session_id, auth_key, auth_key_id)
        assert len(packed[8:24]) == 16

    def test_pack_produces_valid_padding(self, auth_key, session_id, auth_key_id):
        factory = MsgFactory()
        body = raw.functions.Ping(ping_id=0)
        msg = factory(body)
        packed = mtproto.pack(msg, 0, session_id, auth_key, auth_key_id)
        payload = packed[24:]
        assert len(payload) % 16 == 0

    def test_pack_multiple_unique(self, auth_key, session_id, auth_key_id):
        factory = MsgFactory()
        body = raw.functions.Ping(ping_id=0)
        packed_set = set()
        for _ in range(10):
            msg = factory(body)
            p = mtproto.pack(msg, 0, session_id, auth_key, auth_key_id)
            packed_set.add(p)
        assert len(packed_set) == 10


class TestAES:
    def test_ige256_roundtrip(self):
        key = os.urandom(32)
        iv = os.urandom(32)
        plaintext = os.urandom(64)
        encrypted = aes.ige256_encrypt(plaintext, key, iv)
        decrypted = aes.ige256_decrypt(encrypted, key, iv)
        assert decrypted == plaintext

    def test_ctr256_encrypt_decrypt_identity(self):
        key = os.urandom(32)
        iv = bytearray(os.urandom(16))
        plaintext = os.urandom(100)
        encrypted = aes.ctr256_encrypt(plaintext, key, iv.copy())
        decrypted = aes.ctr256_decrypt(encrypted, key, iv.copy())
        assert decrypted == plaintext

    def test_ctr256_double_encrypt(self):
        key = os.urandom(32)
        iv = bytearray(os.urandom(16))
        plaintext = os.urandom(100)
        once = aes.ctr256_encrypt(plaintext, key, iv.copy())
        twice = aes.ctr256_encrypt(once, key, iv.copy())
        assert twice == plaintext

    def test_ctr256_large_data(self):
        key = os.urandom(32)
        iv = bytearray(os.urandom(16))
        plaintext = os.urandom(1024 * 1024)
        encrypted = aes.ctr256_encrypt(plaintext, key, iv.copy())
        decrypted = aes.ctr256_decrypt(encrypted, key, iv.copy())
        assert decrypted == plaintext
