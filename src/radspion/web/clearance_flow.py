"""Helpers for clearance via QR / deep links."""

from radspion.missions import MissionListResult
from radspion.web.session_keys import SESSION_POST_LOGIN_CLEARANCE_RESULT


def store_post_login_clearance_result(session, result: MissionListResult) -> None:
    """Stage clearance API outcome for the transmission modal on the next dashboard load."""
    session[SESSION_POST_LOGIN_CLEARANCE_RESULT] = result.to_api_dict()


def pop_post_login_clearance_result(session) -> dict | None:
    """Read and clear staged clearance outcome (one-shot for dashboard modal)."""
    value = session.get(SESSION_POST_LOGIN_CLEARANCE_RESULT)
    session.pop(SESSION_POST_LOGIN_CLEARANCE_RESULT, None)
    if isinstance(value, dict) and value.get("outcome"):
        return value
    return None
