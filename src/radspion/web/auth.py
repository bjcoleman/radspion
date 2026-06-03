"""Google OAuth and logout routes."""

from flask import Blueprint, current_app, flash, redirect, request, session, url_for

from radspion.oauth_types import (
    OAuthCodeError,
    OAuthStateError,
    OAuthVerificationError,
)
from radspion.web.session_keys import (
    SESSION_PENDING_SUBMIT_DATA,
    SESSION_USER_ID,
)
from radspion.web.submit_flow import store_staged_submit_result

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _redirect_after_signup_blocked() -> str:
    """Send new agents back to link staging or the landing page."""
    pending = session.get(SESSION_PENDING_SUBMIT_DATA)
    if pending:
        # Let Flask encode the path segment once (avoid double-encoding %20).
        return url_for("link.landing", token=pending)
    return url_for("main.index")


def _finish_agent_session(user) -> str:
    """Establish the session, apply any pending data, and return redirect target."""
    session[SESSION_USER_ID] = user.id

    radspion = current_app.extensions["radspion"]
    pending_data = session.pop(SESSION_PENDING_SUBMIT_DATA, None)
    if pending_data:
        result = radspion.submit_data(user.id, pending_data)
        store_staged_submit_result(session, result)

    return url_for("agent.dashboard")


@auth_bp.get("/google")
def google_login():
    """Redirect the browser to Google OAuth."""
    oauth = current_app.extensions["oauth"]
    authorization_url = oauth.authorization_url(session)
    return redirect(authorization_url)


@auth_bp.get("/google/callback")
def google_callback():
    """Complete Google OAuth and establish the agent session."""
    oauth = current_app.extensions["oauth"]
    radspion = current_app.extensions["radspion"]

    code = request.args.get("code", "")
    state = request.args.get("state")

    try:
        profile = oauth.profile_from_callback(session, code=code, state=state)
    except OAuthStateError:
        flash("Sign-in could not be verified. Try again.", "error")
        return redirect(_redirect_after_signup_blocked())
    except OAuthCodeError:
        flash("Sign-in was cancelled or expired. Try again.", "error")
        return redirect(_redirect_after_signup_blocked())
    except OAuthVerificationError:
        flash("Google sign-in could not be verified. Try again.", "error")
        return redirect(_redirect_after_signup_blocked())

    user = radspion.sign_in_with_google(profile)

    return redirect(_finish_agent_session(user))


@auth_bp.post("/logout")
def logout():
    """End the agent session."""
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))
