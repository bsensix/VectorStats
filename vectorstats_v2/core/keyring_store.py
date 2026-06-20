"""Secure key storage backend policy helpers."""

SECURE_BACKENDS = {
    "windows_credential_manager",
    "macos_keychain",
    "linux_libsecret",
}


def ensure_secure_backend(backend_name: str) -> bool:
    return backend_name in SECURE_BACKENDS


__all__ = ["SECURE_BACKENDS", "ensure_secure_backend"]
