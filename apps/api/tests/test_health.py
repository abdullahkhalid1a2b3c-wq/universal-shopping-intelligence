"""Tests for the health-check endpoint."""

from fastapi.testclient import TestClient

from app.main import app


def _client() -> TestClient:
    return TestClient(app)


def test_health_returns_ok() -> None:
    """GET /health returns 200 with status 'ok'."""
    response = _client().get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_health_includes_version() -> None:
    """GET /health includes a version string."""
    response = _client().get("/health")
    body = response.json()
    assert "version" in body
    assert isinstance(body["version"], str)
    assert len(body["version"]) > 0

