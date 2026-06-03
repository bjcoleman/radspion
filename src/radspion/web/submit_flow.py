"""Helpers for staging submit outcomes across redirects."""

from radspion.missions import SubmitDataResult
from radspion.web.session_keys import SESSION_STAGED_SUBMIT_RESULT


def store_staged_submit_result(session, result: SubmitDataResult) -> None:
    """Stage submit API outcome for the transmission modal on the next page load."""
    session[SESSION_STAGED_SUBMIT_RESULT] = result.to_api_dict()


def pop_staged_submit_result(session) -> dict | None:
    """Read and clear staged submit outcome (one-shot)."""
    value = session.get(SESSION_STAGED_SUBMIT_RESULT)
    session.pop(SESSION_STAGED_SUBMIT_RESULT, None)
    if isinstance(value, dict) and value.get("outcome"):
        return value
    return None
