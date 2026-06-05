"""URL token encoding for clearance deep links."""

from urllib.parse import quote, unquote


def encode_clearance_token(clearance_code: str) -> str:
    """Build a path segment for /clearance/<token>."""
    return quote(clearance_code.strip(), safe="")


def decode_clearance_token(token: str) -> str | None:
    """Decode a path segment to the clearance code, or None if empty."""
    code = unquote(token).strip()
    return code if code else None
