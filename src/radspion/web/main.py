"""Public pages blueprint."""

from flask import Blueprint, current_app, g, render_template, send_from_directory

from radspion.web.guards import resolve_optional_session_user

main_bp = Blueprint("main", __name__)


@main_bp.get("/favicon.ico")
def favicon():
    return send_from_directory(
        current_app.static_folder,
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@main_bp.get("/")
def index():
    return render_template("index.html")


@main_bp.get("/about")
def about():
    return render_template("about.html")


@main_bp.get("/privacy")
def privacy():
    return render_template("privacy.html")


@main_bp.get("/activity")
def activity():
    """Public Field Activity page."""
    radspion = current_app.extensions["radspion"]
    user = resolve_optional_session_user()
    if user is not None:
        g.user = user
    return render_template(
        "activity.html",
        user=user,
        activity=radspion.get_field_activity(),
    )
