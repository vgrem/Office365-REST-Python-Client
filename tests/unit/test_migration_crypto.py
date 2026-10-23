"""Tests for the package AES-256-CBC helpers (offline)."""

from __future__ import annotations

import base64

from office365.migration.package.crypto import decrypt, encrypt, normalize_key


def test_normalize_key_decodes_base64_strings():
    raw = bytes(range(32))
    assert normalize_key(base64.b64encode(raw).decode("ascii")) == raw


def test_normalize_key_passes_bytes_through():
    raw = bytes(range(32))
    assert normalize_key(raw) is raw


def test_encrypt_round_trips_with_a_random_iv():
    key = bytes(range(32))
    ciphertext, iv = encrypt(b"hello world", key)

    assert ciphertext != b"hello world"
    assert len(base64.b64decode(iv)) == 16  # noqa: PLR2004
    assert decrypt(ciphertext, key, iv) == b"hello world"
