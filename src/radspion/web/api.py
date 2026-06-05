"""JSON API blueprint."""

from flask import Blueprint, current_app, g, jsonify, request

from radspion.web.guards import api_login_required

api_bp = Blueprint("api", __name__, url_prefix="/api")

INVALID_CLEARANCE_MESSAGE = "Command could not verify this clearance code against agency records."
INVALID_SUBMIT_MESSAGE = (
    "We received your transmission, but the recovered data does not match mission parameters."
)


@api_bp.post("/clearance")
@api_login_required
def grant_clearance():
    """Grant clearance for matching missions (POST /api/clearance)."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "missing clearance_code"}), 400

    raw_code = payload.get("clearance_code")
    if not isinstance(raw_code, str) or not raw_code.strip():
        return jsonify({"error": "missing clearance_code"}), 400

    radspion = current_app.extensions["radspion"]
    result = radspion.grant_clearance(g.user.id, raw_code)
    if result.outcome == "invalid":
        return jsonify(
            {"outcome": "invalid", "message": INVALID_CLEARANCE_MESSAGE},
        )

    return jsonify(result.to_api_dict())


@api_bp.post("/missions/<slug>/submit")
@api_login_required
def submit_mission(slug: str):
    """Submit mission data (POST /api/missions/<slug>/submit)."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "missing completion_data"}), 400

    raw_data = payload.get("completion_data")
    if not isinstance(raw_data, str) or not raw_data.strip():
        return jsonify({"error": "missing completion_data"}), 400

    radspion = current_app.extensions["radspion"]
    result = radspion.submit_mission_data(g.user.id, slug, raw_data)
    if result is None:
        return jsonify({"error": "Not found"}), 404
    if result.outcome == "invalid":
        return jsonify({"outcome": "invalid", "message": INVALID_SUBMIT_MESSAGE})

    return jsonify(result.to_api_dict())
