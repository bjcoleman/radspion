"""Google OAuth and logout routes."""

from flask import Blueprint, current_app, flash, redirect, request, session, url_for

from radspion.oauth_types import (
    OAuthCodeError,
    OAuthStateError,
    OAuthVerificationError,
    SignupNotAllowedError,
)
from radspion.web.session_keys import (
    SESSION_PENDING_UNLOCK,
    SESSION_REGISTRATION_CLEARED,
    SESSION_USER_ID,
)
from radspion.web.unlock_flow import store_post_login_unlock_result

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _redirect_after_signup_blocked() -> str:
    """Send new agents back to unlock staging or the landing page."""
    pending = session.get(SESSION_PENDING_UNLOCK)
    if pending:
        # Let Flask encode the path segment once (avoid double-encoding %20).
        return url_for("unlock.landing", token=pending)
    return url_for("main.index")


def _finish_agent_session(user) -> str:
    """Establish the session, apply any pending unlock, and return redirect target."""
    session[SESSION_USER_ID] = user.id
    session.pop(SESSION_REGISTRATION_CLEARED, None)

    radspion = current_app.extensions["radspion"]
    pending_unlock = session.pop(SESSION_PENDING_UNLOCK, None)
    if pending_unlock:
        result = radspion.redeem_unlock_code(user.id, pending_unlock)
        store_post_login_unlock_result(session, result)

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

    registration_cleared = bool(session.get(SESSION_REGISTRATION_CLEARED))
    try:
        user = radspion.sign_in_with_google(
            profile,
            registration_cleared=registration_cleared,
        )
    except SignupNotAllowedError:
        flash(
            "Submit a valid registration access code before signing in with Google. "
            "This is separate from the mission unlock in your QR link.",
            "error",
        )
        return redirect(_redirect_after_signup_blocked())

    return redirect(_finish_agent_session(user))


@auth_bp.post("/logout")
def logout():
    """End the agent session."""
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))
