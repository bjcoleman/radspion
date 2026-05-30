"""Signed-in agent pages."""

from flask import Blueprint, abort, current_app, g, render_template

from radspion.web.guards import login_required

agent_bp = Blueprint("agent", __name__, url_prefix="/agent")


@agent_bp.get("/dashboard")
@login_required
def dashboard():
    """Agent home (stub until full mission dashboard)."""
    user = current_app.extensions["radspion"].get_user(g.user_id)
    if user is None:
        abort(404)
    return render_template("agent/dashboard.html", user=user)
