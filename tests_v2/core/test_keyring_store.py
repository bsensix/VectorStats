"""Tests for secure API key storage backends."""

from vectorstats_v2.core.keyring_store import ensure_secure_backend


def test_key_store_rejects_plaintext_fallback() -> None:
    assert ensure_secure_backend("plaintext") is False


def test_key_store_accepts_vault_backends() -> None:
    assert ensure_secure_backend("windows_credential_manager") is True
    assert ensure_secure_backend("macos_keychain") is True
    assert ensure_secure_backend("linux_libsecret") is True
