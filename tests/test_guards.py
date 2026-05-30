"""Tests for login decorators."""

from flask import jsonify

from radspion.web.guards import api_login_required, login_required
from radspion.web.session_keys import SESSION_USER_ID


def test_api_login_required_returns_401_when_anonymous(client, app):
    @app.get("/test-api-guard")
    @api_login_required
    def _protected_api():
        return jsonify({"ok": True})

    response = client.get("/test-api-guard")

    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"}


def test_api_login_required_allows_signed_in_user(client, app, existing_user):
    @app.get("/test-api-guard-ok")
    @api_login_required
    def _protected_api_ok():
        return jsonify({"ok": True})

    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = existing_user.id

    response = client.get("/test-api-guard-ok")

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}


def test_login_required_sets_g_user_id(client, app, existing_user):
    @app.get("/test-html-guard")
    @login_required
    def _protected_html():
        from flask import g

        return jsonify(user_id=g.user_id)

    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = existing_user.id

    response = client.get("/test-html-guard")

    assert response.status_code == 200
    assert response.get_json() == {"user_id": existing_user.id}
