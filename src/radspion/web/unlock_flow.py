"""Helpers for mission unlock via QR / deep links."""

from radspion.missions import UnlockRedeemResult
from radspion.web.session_keys import SESSION_POST_LOGIN_UNLOCK_RESULT


def store_post_login_unlock_result(session, result: UnlockRedeemResult) -> None:
    """Stage unlock API outcome for the transmission modal on the next dashboard load."""
    session[SESSION_POST_LOGIN_UNLOCK_RESULT] = result.to_api_dict()


def pop_post_login_unlock_result(session) -> dict | None:
    """Read and clear staged unlock outcome (one-shot for dashboard modal)."""
    value = session.get(SESSION_POST_LOGIN_UNLOCK_RESULT)
    session.pop(SESSION_POST_LOGIN_UNLOCK_RESULT, None)
    if isinstance(value, dict) and value.get("outcome"):
        return value
    return None
