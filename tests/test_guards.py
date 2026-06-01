"""Tests for login decorators."""

from flask import g, jsonify

from radspion.web.guards import api_login_required, login_required
from radspion.web.session_keys import SESSION_USER_ID

_STALE_USER_ID = 99_999


def test_api_login_required_returns_401_when_anonymous(client, app):
    @app.get("/test-api-guard")
    @api_login_required
    def _protected_api():
        return jsonify({"ok": True})

    response = client.get("/test-api-guard")

    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"}


def test_api_login_required_returns_401_when_session_user_missing_from_db(client, app):
    @app.get("/test-api-guard-stale")
    @api_login_required
    def _protected_api_stale():
        return jsonify({"ok": True})

    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = _STALE_USER_ID

    response = client.get("/test-api-guard-stale")

    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"}


def test_api_login_required_sets_g_user(client, app, existing_user):
    @app.get("/test-api-guard-ok")
    @api_login_required
    def _protected_api_ok():
        return jsonify(
            {
                "ok": True,
                "user_id": g.user.id,
                "email": g.user.email,
                "is_operator": g.user.is_operator,
            }
        )

    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = existing_user.id

    response = client.get("/test-api-guard-ok")

    assert response.status_code == 200
    assert response.get_json() == {
        "ok": True,
        "user_id": existing_user.id,
        "email": existing_user.email,
        "is_operator": existing_user.is_operator,
    }


def test_login_required_returns_401_when_session_user_missing_from_db(client, app):
    @app.get("/test-html-guard-stale")
    @login_required
    def _protected_html_stale():
        return jsonify({"ok": True})

    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = _STALE_USER_ID

    response = client.get("/test-html-guard-stale")

    assert response.status_code == 401


def test_login_required_sets_g_user(client, app, existing_user):
    @app.get("/test-html-guard")
    @login_required
    def _protected_html():
        return jsonify(
            {
                "user_id": g.user.id,
                "display_name": g.user.display_name,
            }
        )

    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = existing_user.id

    response = client.get("/test-html-guard")

    assert response.status_code == 200
    assert response.get_json() == {
        "user_id": existing_user.id,
        "display_name": existing_user.display_name,
    }
