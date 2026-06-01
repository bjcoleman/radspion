"""Signed-in agent pages."""

from flask import Blueprint, abort, current_app, g, render_template

from radspion.web.guards import login_required

agent_bp = Blueprint("agent", __name__, url_prefix="/agent")


@agent_bp.get("/dashboard")
@login_required
def dashboard():
    """Agent mission dashboard (UC-013)."""
    radspion = current_app.extensions["radspion"]
    radspion.sync_mission_status(g.user.id)
    dashboard_groups = radspion.get_agent_dashboard(g.user.id)
    return render_template(
        "agent/dashboard.html",
        user=g.user,
        dashboard_groups=dashboard_groups,
    )


@agent_bp.get("/missions/<slug>")
@login_required
def mission_detail(slug: str):
    """Mission detail placeholder until full brief/debrief UI (UC-016 stub)."""
    radspion = current_app.extensions["radspion"]
    mission = radspion.find_listed_mission(g.user.id, slug)
    if mission is None:
        abort(404)

    return render_template(
        "agent/mission_detail.html",
        user=g.user,
        mission=mission,
    )
