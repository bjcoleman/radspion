"""Google OAuth and logout routes."""

from flask import Blueprint, current_app, flash, redirect, request, session, url_for

from radspion.oauth_types import (
    OAuthCodeError,
    OAuthStateError,
    OAuthVerificationError,
    SignupNotAllowedError,
)
from radspion.web.session_keys import SESSION_REGISTRATION_CLEARED, SESSION_USER_ID

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


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
        return redirect(url_for("main.index"))
    except OAuthCodeError:
        flash("Sign-in was cancelled or expired. Try again.", "error")
        return redirect(url_for("main.index"))
    except OAuthVerificationError:
        flash("Google sign-in could not be verified. Try again.", "error")
        return redirect(url_for("main.index"))

    registration_cleared = bool(session.get(SESSION_REGISTRATION_CLEARED))
    try:
        user = radspion.sign_in_with_google(
            profile,
            registration_cleared=registration_cleared,
        )
    except SignupNotAllowedError:
        flash("Submit a valid access code before signing in with Google.", "error")
        return redirect(url_for("main.index"))

    session[SESSION_USER_ID] = user.id
    session.pop(SESSION_REGISTRATION_CLEARED, None)
    return redirect(url_for("agent.dashboard"))


@auth_bp.post("/logout")
def logout():
    """End the agent session."""
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))
