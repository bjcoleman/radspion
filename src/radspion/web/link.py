"""Field data deep links (e.g. from QR codes)."""

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for

from radspion.web.link_tokens import decode_link_token, encode_link_token
from radspion.web.session_keys import SESSION_PENDING_SUBMIT_DATA, SESSION_USER_ID

link_bp = Blueprint("link", __name__, url_prefix="/link")


@link_bp.get("/<token>")
def landing(token: str):
    """
    Stage field data from a URL and prompt sign-in or confirmation.

    The token is URL-encoded field data. Logged-in agents confirm and submit
    via POST /api/submit; anonymous visitors sign in with Google first.
    """
    data = decode_link_token(token)
    if data is None:
        flash("Invalid data link.", "error")
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

    # Anonymous visitors need the data carried through OAuth; signed-in agents
    # submit via POST /api/submit on this page (no session staging).
    if not signed_in:
        session[SESSION_PENDING_SUBMIT_DATA] = data
    else:
        session.pop(SESSION_PENDING_SUBMIT_DATA, None)

    return render_template(
        "link.html",
        link_data=data,
        link_token=encode_link_token(data),
        signed_in=signed_in,
    )
