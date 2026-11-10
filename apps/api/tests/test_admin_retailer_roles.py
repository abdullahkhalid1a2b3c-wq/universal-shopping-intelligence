"""Unit tests for retailer and admin endpoints and role enforcement."""

import jwt
import pytest
from fastapi.testclient import TestClient

from app.auth import decode_token
from app.config import settings
from app.main import app
from app.supabase_client import set_supabase_client


def make_test_token(user_id: str, email: str, role: str) -> str:
    """Generate a test JWT token containing application role claim."""
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "app_metadata": {"role": role},
        "user_metadata": {"role": role},
        "app_role": role,
    }
    if settings.supabase_jwt_secret:
        return jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")
    return jwt.encode(payload, "secret", algorithm="HS256")


class MockTable:
    def __init__(self, name: str):
        self.name = name
        self._data = []

    def select(self, *args, **kwargs):
        return self

    def insert(self, data):
        self._data = [data] if isinstance(data, dict) else data
        return self

    def upsert(self, data, *args, **kwargs):
        self._data = [data] if isinstance(data, dict) else data
        return self

    def update(self, data):
        self._data = [data] if isinstance(data, dict) else data
        return self

    def eq(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def execute(self):
        class MockRes:
            def __init__(self, data):
                self.data = data
                self.count = len(data)

        if self.name == "retailers":
            return MockRes([{"id": "ret-1", "name": "Khaadi", "slug": "khaadi", "status": "pending"}])
        elif self.name == "retailer_members":
            return MockRes([{"id": "mem-1", "retailer_id": "ret-1", "user_id": "ret-user-1", "member_role": "owner"}])
        elif self.name == "coverage_requests":
            return MockRes([{"domain": "sapphire.pk", "page_url": "https://sapphire.pk/p1", "created_at": "2026-11-01"}])
        elif self.name == "store_adapters":
            return MockRes([{"domain": "khaadi.com", "platform": "shopify", "is_enabled": True}])
        elif self.name == "size_charts":
            return MockRes([{"id": "sc-1", "name": "Kurta Chart", "category": "kurta", "verified_at": None, "is_demo": True, "retailers": {"name": "Khaadi"}}])
        elif self.name == "size_chart_rows":
            return MockRes([{"size_label": "S", "measurement_key": "chest", "value_cm": 96.0}])
        elif self.name == "v_product_fit_stats":
            return MockRes([
                {
                    "product_id": "p-1",
                    "product_name": "Kurta M",
                    "size_bought": "M",
                    "total_feedback": 15,
                    "pct_too_tight": 33.3,
                    "pct_perfect": 60.0,
                    "pct_too_loose": 6.7,
                    "return_count": 4,
                }
            ])
        elif self.name == "v_product_recommendation_counts":
            return MockRes([{"week_start": "2026-11-02", "recommendation_count": 25, "product_name": "Kurta M"}])

        return MockRes(self._data)


class MockSupabase:
    def table(self, name: str):
        return MockTable(name)


@pytest.fixture(autouse=True)
def setup_mock_db():
    set_supabase_client(MockSupabase())
    yield
    set_supabase_client(None)


def test_customer_cannot_access_admin_endpoints():
    """A user with standard 'customer' role should get 403 on admin endpoints."""
    token = make_test_token("cust-1", "cust@example.com", "customer")
    client = TestClient(app)

    res = client.get(
        "/v1/admin/retailers",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403
    assert "Admin privileges required" in res.json()["detail"]


def test_admin_can_access_admin_retailers():
    """An admin user can list retailers."""
    token = make_test_token("admin-1", "admin@fitsense.pk", "admin")
    client = TestClient(app)

    res = client.get(
        "/v1/admin/retailers",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_admin_data_quality_audit():
    """Admin data quality endpoint audits unverified and warned charts."""
    token = make_test_token("admin-1", "admin@fitsense.pk", "admin")
    client = TestClient(app)

    res = client.get(
        "/v1/admin/data-quality",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "unverified_charts" in data
    assert "demo_charts" in data
    assert "total_charts" in data


def test_retailer_can_validate_size_chart():
    """Retailer can validate a size chart."""
    token = make_test_token("ret-1", "retailer@brand.pk", "retailer")
    client = TestClient(app)

    payload = {
        "rows": [
            {"size_label": "S", "chest": 96.0, "waist": 82.0},
            {"size_label": "M", "chest": 102.0, "waist": 88.0},
        ],
        "measured_as": "circumference",
        "category": "shirt",
    }
    res = client.post(
        "/v1/retailer/size-charts/validate",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert len(data["warnings"]) == 0


def test_retailer_analytics_computation():
    """Retailer analytics endpoint aggregates recommendations, feedback, and hints."""
    token = make_test_token("ret-user-1", "retailer@brand.pk", "retailer")
    client = TestClient(app)

    res = client.get(
        "/v1/retailer/analytics?retailer_id=ret-1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "recommendations_per_week" in data
    assert "feedback_distribution" in data
    assert "problem_products" in data
    assert len(data["problem_products"]) > 0
    assert "Size M of 'Kurta M' runs small" in data["plain_language_hints"][0]
