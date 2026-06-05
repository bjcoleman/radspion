"""Dev-only mission brief/debrief preview routes."""

from flask import Blueprint, abort, current_app, render_template, request

from radspion.markdown_render import render_mission_markdown
from radspion.missions import MissionDetail
from radspion.missions_fs import MissionsFilesystemError, load_mission

preview_bp = Blueprint("preview", __name__)


def _normalize_status(raw: str | None) -> str:
    if raw in (None, "", "active"):
        return "active"
    if raw in ("completed", "complete"):
        return "completed"
    abort(400, description="status must be active or completed")


@preview_bp.get("/")
def mission_detail():
    """Render the launched mission page from on-disk pack markdown."""
    storyline = current_app.config["PREVIEW_STORYLINE"]
    mission_slug = current_app.config["PREVIEW_MISSION_SLUG"]
    status = _normalize_status(request.args.get("status"))

    try:
        source = load_mission(storyline, mission_slug)
    except MissionsFilesystemError as exc:
        abort(404, description=str(exc))

    recovered_data = source.completion_data if status == "completed" else None
    mission = MissionDetail(
        slug=source.slug,
        title=source.title,
        status=status,
        brief_html=render_mission_markdown(source.brief_markdown),
        debrief_html=render_mission_markdown(source.debrief_markdown),
        recovered_data=recovered_data,
    )

    return render_template(
        "preview/mission_detail.html",
        mission=mission,
        preview_status=status,
    )


@preview_bp.errorhandler(404)
def not_found(error):
    description = getattr(error, "description", None) or "Not found"
    return render_template("preview/error.html", message=description), 404


@preview_bp.errorhandler(400)
def bad_request(error):
    description = getattr(error, "description", None) or "Bad request"
    return render_template("preview/error.html", message=description), 400
