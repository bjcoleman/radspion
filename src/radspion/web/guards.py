"""Route decorators for authenticated access."""

from functools import wraps

from flask import abort, current_app, flash, g, jsonify, redirect, session, url_for

from radspion.user import User
from radspion.web.session_keys import SESSION_USER_ID

_UNAUTHORIZED_JSON = {"error": "Unauthorized"}


def _resolve_session_user() -> User | None:
    """Load the agent for SESSION_USER_ID, or None if missing or not in the database."""
    user_id = session.get(SESSION_USER_ID)
    if user_id is None:
        return None
    return current_app.extensions["radspion"].get_user(user_id)


def resolve_optional_session_user() -> User | None:
    """Return the signed-in agent when the session is valid, else None."""
    return _resolve_session_user()


def login_required(view):
    """Require a signed-in agent with a live user row; redirect or 401 on failure."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get(SESSION_USER_ID) is None:
            flash("Sign in to continue.", "error")
            return redirect(url_for("main.index"))
        user = _resolve_session_user()
        if user is None:
            abort(401)
        g.user = user
        return view(*args, **kwargs)

    return wrapped


def api_login_required(view):
    """Require a signed-in agent with a live user row; return 401 JSON on failure."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get(SESSION_USER_ID) is None:
            return jsonify(_UNAUTHORIZED_JSON), 401
        user = _resolve_session_user()
        if user is None:
            return jsonify(_UNAUTHORIZED_JSON), 401
        g.user = user
        return view(*args, **kwargs)

    return wrapped
