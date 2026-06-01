"""JSON API blueprint."""

from flask import Blueprint, current_app, g, jsonify, request, session

from radspion.web.guards import api_login_required
from radspion.web.session_keys import SESSION_REGISTRATION_CLEARED

api_bp = Blueprint("api", __name__, url_prefix="/api")

INVALID_ACCESS_MESSAGE = "We could not validate that access code against agency records."
INVALID_UNLOCK_MESSAGE = "We could not validate that unlock code against agency records."


@api_bp.post("/access")
def validate_access():
    """Validate a registration access code (POST /api/access)."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "missing access_code"}), 400

    raw_code = payload.get("access_code")
    if not isinstance(raw_code, str) or not raw_code.strip():
        return jsonify({"error": "missing access_code"}), 400

    radspion = current_app.extensions["radspion"]
    if radspion.validate_registration_code(raw_code):
        session[SESSION_REGISTRATION_CLEARED] = True
        return jsonify({"outcome": "success"})

    return jsonify({"outcome": "invalid", "message": INVALID_ACCESS_MESSAGE})


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
