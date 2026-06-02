"""Mission unlock deep links (e.g. from QR codes)."""

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for

from radspion.web.session_keys import SESSION_PENDING_UNLOCK, SESSION_USER_ID
from radspion.web.unlock_tokens import decode_unlock_token, encode_unlock_token

unlock_bp = Blueprint("unlock", __name__, url_prefix="/unlock")


@unlock_bp.get("/<token>")
def landing(token: str):
    """
    Stage a mission unlock from a URL and prompt sign-in or confirmation.

    The token is a URL-encoded unlock code. Logged-in agents confirm and redeem
    via POST /api/unlock; anonymous visitors sign in with Google first.
    """
    unlock_code = decode_unlock_token(token)
    if unlock_code is None:
        flash("Invalid mission unlock link.", "error")
        return redirect(url_for("main.index"))

    radspion = current_app.extensions["radspion"]
    user_id = session.get(SESSION_USER_ID)
    signed_in = False
    if user_id is not None:
        user = radspion.get_user(user_id)
        if user is None:
            session.pop(SESSION_USER_ID, None)
        else:
            signed_in = True

    # Anonymous visitors need the code carried through OAuth; signed-in agents
    # redeem via POST /api/unlock on this page (no session staging).
    if not signed_in:
        session[SESSION_PENDING_UNLOCK] = unlock_code
    else:
        session.pop(SESSION_PENDING_UNLOCK, None)

    return render_template(
        "unlock.html",
        unlock_code=unlock_code,
        unlock_token=encode_unlock_token(unlock_code),
        signed_in=signed_in,
    )
