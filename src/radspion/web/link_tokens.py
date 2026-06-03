"""URL token encoding for field data deep links."""

from urllib.parse import quote, unquote


def encode_link_token(data: str) -> str:
    """Build a path segment for /link/<token>."""
    return quote(data.strip(), safe="")


def decode_link_token(token: str) -> str | None:
    """Decode a path segment to field data, or None if empty."""
    value = unquote(token).strip()
    return value if value else None
