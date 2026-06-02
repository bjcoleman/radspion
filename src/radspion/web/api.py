"""JSON API blueprint."""

from flask import Blueprint, current_app, g, jsonify, request

from radspion.web.guards import api_login_required

api_bp = Blueprint("api", __name__, url_prefix="/api")

INVALID_UNLOCK_MESSAGE = "We could not validate that unlock code against agency records."
INVALID_SUBMIT_MESSAGE = (
    "We reviewed your transmission, and the recovered data does not match mission requirements."
)


@api_bp.post("/unlock")
@api_login_required
def redeem_unlock():
    """Redeem a mission unlock code (POST /api/unlock)."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "missing unlock_code"}), 400

    raw_code = payload.get("unlock_code")
    if not isinstance(raw_code, str) or not raw_code.strip():
        return jsonify({"error": "missing unlock_code"}), 400

    radspion = current_app.extensions["radspion"]
    result = radspion.redeem_unlock_code(g.user.id, raw_code)
    if result.outcome == "invalid":
        return jsonify(
            {"outcome": "invalid", "message": INVALID_UNLOCK_MESSAGE},
        )

    return jsonify(result.to_api_dict())


@api_bp.post("/missions/<slug>/submit")
@api_login_required
def submit_mission(slug: str):
    """Submit a mission completion code (POST /api/missions/<slug>/submit)."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "missing completion_code"}), 400

    raw_code = payload.get("completion_code")
    if not isinstance(raw_code, str) or not raw_code.strip():
        return jsonify({"error": "missing completion_code"}), 400

    radspion = current_app.extensions["radspion"]
    result = radspion.submit_mission_completion(g.user.id, slug, raw_code)
    if result is None:
        return jsonify({"error": "Not found"}), 404
    if result.outcome == "invalid":
        return jsonify({"outcome": "invalid", "message": INVALID_SUBMIT_MESSAGE})

    return jsonify(result.to_api_dict())
