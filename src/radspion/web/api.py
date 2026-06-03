"""JSON API blueprint."""

from flask import Blueprint, current_app, g, jsonify, request, session

from radspion.web.guards import api_login_required
from radspion.web.submit_flow import store_staged_submit_result

api_bp = Blueprint("api", __name__, url_prefix="/api")

INVALID_DATA_MESSAGE = "We could not validate that data against agency records."


@api_bp.post("/submit")
@api_login_required
def submit_data():
    """Submit field data (POST /api/submit)."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "missing data"}), 400

    raw_data = payload.get("data")
    if not isinstance(raw_data, str) or not raw_data.strip():
        return jsonify({"error": "missing data"}), 400

    radspion = current_app.extensions["radspion"]
    result = radspion.submit_data(g.user.id, raw_data)
    if result.outcome == "invalid":
        return jsonify(
            {"outcome": "invalid", "message": INVALID_DATA_MESSAGE},
        )

    if result.outcome == "success":
        store_staged_submit_result(session, result)

    return jsonify(result.to_api_dict())
