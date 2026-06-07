"""Dev-only mission brief/debrief preview routes."""

from flask import Blueprint, abort, current_app, render_template, request

from radspion.markdown_render import render_mission_markdown
from radspion.markdown_themes import resolve_markdown_theme
from radspion.mission_files import MissionFilesError, load_mission
from radspion.missions import MissionDetail

preview_bp = Blueprint("preview", __name__)


def _normalize_status(raw: str | None) -> str:
    if raw in (None, "", "active"):
        return "active"
    if raw in ("completed", "complete"):
        return "completed"
    abort(400, description="status must be active or completed")


def _resolve_preview_theme_key() -> str:
    raw = request.args.get("theme")
    if raw:
        try:
            return resolve_markdown_theme(raw).key
        except ValueError as exc:
            abort(400, description=str(exc))
    return resolve_markdown_theme(current_app.config.get("MARKDOWN_THEME")).key


@preview_bp.get("/")
def mission_detail():
    """Render the launched mission page from on-disk pack markdown."""
    storyline = current_app.config["PREVIEW_STORYLINE"]
    mission_slug = current_app.config["PREVIEW_MISSION_SLUG"]
    status = _normalize_status(request.args.get("status"))
    theme_key = _resolve_preview_theme_key()

    try:
        source = load_mission(storyline, mission_slug)
    except MissionFilesError as exc:
        abort(404, description=str(exc))

    recovered_data = source.completion_data if status == "completed" else None
    mission = MissionDetail(
        slug=source.slug,
        title=source.title,
        status=status,
        brief_html=render_mission_markdown(source.brief_markdown, theme_key=theme_key),
        debrief_html=render_mission_markdown(source.debrief_markdown, theme_key=theme_key),
        recovered_data=recovered_data,
    )

    return render_template(
        "preview/mission_detail.html",
        mission=mission,
        preview_status=status,
        preview_theme=theme_key,
    )


@preview_bp.errorhandler(404)
def not_found(error):
    description = getattr(error, "description", None) or "Not found"
    return render_template("preview/error.html", message=description), 404


@preview_bp.errorhandler(400)
def bad_request(error):
    description = getattr(error, "description", None) or "Bad request"
    return render_template("preview/error.html", message=description), 400
