"""Tests for FitSense production & preview CORS configuration."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestCorsConfiguration:
    """Verify CORS policy allows FitSense production, previews, and localhost while rejecting others."""

    def test_localhost_origin_allowed(self, client: TestClient):
        """localhost:3000 is allowed for development."""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
        assert response.headers.get("access-control-allow-credentials") == "true"

    def test_production_vercel_origin_allowed(self, client: TestClient):
        """Production Vercel frontend origin is allowed."""
        prod_origin = "https://universal-shopping-intelligence.vercel.app"
        response = client.get(
            "/health",
            headers={"Origin": prod_origin},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == prod_origin
        assert response.headers.get("access-control-allow-credentials") == "true"

    def test_preview_vercel_origin_allowed(self, client: TestClient):
        """Branch and preview Vercel origins are allowed."""
        preview_origins = [
            "https://universal-shopping-intelligence-git-main-any-5391.vercel.app",
            "https://universal-shopping-intelligence-preview-123.vercel.app",
            "https://universal-shopping-intelligence-feat-darkmode-any-5391.vercel.app",
            "https://universal-shopping-intelligence-any-5391.vercel.app",
        ]
        for origin in preview_origins:
            response = client.get(
                "/health",
                headers={"Origin": origin},
            )
            assert response.status_code == 200, f"Failed for {origin}"
            assert response.headers.get("access-control-allow-origin") == origin, f"Origin not allowed: {origin}"
            assert response.headers.get("access-control-allow-credentials") == "true"

    def test_preflight_options_allowed_for_valid_origin(self, client: TestClient):
        """OPTIONS preflight request responds with permitted methods and headers."""
        origin = "https://universal-shopping-intelligence.vercel.app"
        response = client.options(
            "/v1/recommend",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization,Content-Type",
            },
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == origin
        assert response.headers.get("access-control-allow-credentials") == "true"
        allow_methods = response.headers.get("access-control-allow-methods", "")
        assert "POST" in allow_methods

    def test_unrelated_vercel_origin_rejected(self, client: TestClient):
        """An unrelated Vercel project is strictly rejected."""
        unrelated_origins = [
            "https://some-other-project.vercel.app",
            "https://malicious-app.vercel.app",
            "https://my-store.vercel.app",
            "https://not-universal-shopping-intelligence.vercel.app",
            "https://universal-shopping-intelligence.attacker.com",
            "https://universal-shopping-intelligence.vercel.app.attacker.com",
            "http://universal-shopping-intelligence.vercel.app",  # non-https
        ]
        for origin in unrelated_origins:
            response = client.get(
                "/health",
                headers={"Origin": origin},
            )
            assert response.status_code == 200
            # CORS middleware should omit access-control-allow-origin for unauthorized origins
            assert "access-control-allow-origin" not in response.headers, (
                f"Origin {origin} was improperly granted CORS access!"
            )

