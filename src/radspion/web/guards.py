"""Route decorators for authenticated access."""

from functools import wraps

from flask import flash, g, jsonify, redirect, session, url_for

from radspion.web.session_keys import SESSION_USER_ID


def login_required(view):
    """Require a signed-in agent; redirect to landing with flash on failure."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get(SESSION_USER_ID)
        if user_id is None:
            flash("Sign in to continue.", "error")
            return redirect(url_for("main.index"))
        g.user_id = user_id
        return view(*args, **kwargs)

    return wrapped


def api_login_required(view):
    """Require a signed-in agent; return 401 JSON on failure."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get(SESSION_USER_ID)
        if user_id is None:
            return jsonify({"error": "Unauthorized"}), 401
        g.user_id = user_id
        return view(*args, **kwargs)

    return wrapped
