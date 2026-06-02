"""URL token encoding for mission unlock links."""

from urllib.parse import quote, unquote


def encode_unlock_token(unlock_code: str) -> str:
    """Build a path segment for /unlock/<token>."""
    return quote(unlock_code.strip(), safe="")


def decode_unlock_token(token: str) -> str | None:
    """Decode a path segment to the unlock code, or None if empty."""
    code = unquote(token).strip()
    return code if code else None
