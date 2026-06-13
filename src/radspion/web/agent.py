"""Signed-in agent pages."""

from flask import Blueprint, abort, current_app, g, render_template, session

from radspion.content_files import load_welcome_memo_markdown
from radspion.markdown_render import render_mission_markdown
from radspion.missions import dashboard_completed_total
from radspion.web.clearance_flow import pop_post_login_clearance_result
from radspion.web.guards import login_required

agent_bp = Blueprint("agent", __name__, url_prefix="/agent")


@agent_bp.get("/dashboard")
@login_required
def dashboard():
    """Agent mission dashboard (UC-013)."""
    radspion = current_app.extensions["radspion"]
    radspion.sync_mission_status(g.user.id)
    dashboard_groups = radspion.get_agent_dashboard(g.user.id)
    completed_total = dashboard_completed_total(dashboard_groups)
    welcome_memo_html = None
    if completed_total == 0:
        source = load_welcome_memo_markdown()
        if source is not None:
            welcome_memo_html = render_mission_markdown(source)
    return render_template(
        "agent/dashboard.html",
        user=g.user,
        dashboard_groups=dashboard_groups,
        completed_total=completed_total,
        welcome_memo_html=welcome_memo_html,
        post_login_clearance_result=pop_post_login_clearance_result(session),
    )


@agent_bp.get("/missions/<slug>")
@login_required
def mission_detail(slug: str):
    """Mission detail: brief, debrief, recovered data (UC-016)."""
    radspion = current_app.extensions["radspion"]
    mission = radspion.get_mission_detail(g.user.id, slug)
    if mission is None:
        abort(404)

    return render_template(
        "agent/mission_detail.html",
        user=g.user,
        mission=mission,
    )


@agent_bp.get("/personnel")
@login_required
def personnel():
    """Agent Personnel File."""
    radspion = current_app.extensions["radspion"]
    personnel_file = radspion.get_personnel_file(g.user.id)
    if personnel_file is None:
        abort(404)

    return render_template(
        "agent/personnel.html",
        user=g.user,
        personnel=personnel_file,
    )
