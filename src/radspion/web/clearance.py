"""Clearance deep links (e.g. from QR codes)."""

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for

from radspion.web.clearance_tokens import decode_clearance_token, encode_clearance_token
from radspion.web.session_keys import SESSION_PENDING_CLEARANCE, SESSION_USER_ID

clearance_bp = Blueprint("clearance", __name__, url_prefix="/clearance")


@clearance_bp.get("/<token>")
def landing(token: str):
    """
    Stage clearance from a URL and prompt sign-in or confirmation.

    The token is a URL-encoded clearance code. Logged-in agents confirm and grant
    via POST /api/clearance; anonymous visitors sign in with Google first.
    """
    clearance_code = decode_clearance_token(token)
    if clearance_code is None:
        flash("Invalid clearance link.", "error")
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
    # grant via POST /api/clearance on this page (no session staging).
    if not signed_in:
        session[SESSION_PENDING_CLEARANCE] = clearance_code
    else:
        session.pop(SESSION_PENDING_CLEARANCE, None)

    return render_template(
        "clearance.html",
        clearance_code=clearance_code,
        clearance_token=encode_clearance_token(clearance_code),
        signed_in=signed_in,
    )
