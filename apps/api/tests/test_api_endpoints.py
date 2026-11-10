"""Integration tests for FastAPI endpoints with mocked Supabase client."""

from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.auth import get_optional_user
from app.main import app
from app.supabase_client import set_supabase_client


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_endpoint(client: TestClient) -> None:
    """GET /health returns status ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_products_lookup_found(client: TestClient) -> None:
    """GET /v1/products/lookup returns product data when found."""
    mock_sb = MagicMock()
    mock_execute = MagicMock()
    mock_execute.data = [
        {
            "id": "p-101",
            "name": "Graphic Tee",
            "category": "tshirt_top",
            "product_url": "https://breakout.com.pk/products/tee",
            "canonical_url": "https://breakout.com.pk/products/tee",
            "retailers": {"id": "r-1", "name": "Breakout", "slug": "breakout", "status": "verified"},
            "size_charts": {"id": "sc-1", "name": "Tee Chart", "verified_at": "2026-01-01", "is_demo": True},
        }
    ]
    mock_sb.table().select().or_().limit().execute.return_value = mock_execute
    set_supabase_client(mock_sb)

    resp = client.get("/v1/products/lookup?url=https://breakout.com.pk/products/tee?utm_source=fb")
    assert resp.status_code == 200
    data = resp.json()
    assert data["covered"] is True
    assert data["product"]["name"] == "Graphic Tee"


def test_products_lookup_not_found(client: TestClient) -> None:
    """GET /v1/products/lookup returns 404 when product not found."""
    mock_sb = MagicMock()
    mock_execute = MagicMock()
    mock_execute.data = []
    mock_sb.table().select().or_().limit().execute.return_value = mock_execute
    set_supabase_client(mock_sb)

    resp = client.get("/v1/products/lookup?url=https://unknown-shop.pk/p/1")
    assert resp.status_code == 404
    assert resp.json()["covered"] is False


def test_retailers_listing(client: TestClient) -> None:
    """GET /v1/retailers returns verified retailers."""
    mock_sb = MagicMock()
    mock_execute = MagicMock()
    mock_execute.data = [
        {"id": "r-1", "name": "Khaadi", "slug": "khaadi", "supports_cod": True},
        {"id": "r-2", "name": "Sapphire", "slug": "sapphire", "supports_cod": True},
    ]
    mock_sb.table().select().eq().order().execute.return_value = mock_execute
    set_supabase_client(mock_sb)

    resp = client.get("/v1/retailers")
    assert resp.status_code == 200
    retailers = resp.json()
    assert len(retailers) == 2
    assert retailers[0]["name"] == "Khaadi"


def test_coverage_request_submission(client: TestClient) -> None:
    """POST /v1/coverage-requests creates a request."""
    mock_sb = MagicMock()
    mock_execute = MagicMock()
    mock_execute.data = [{"id": "cr-1", "domain": "newbrand.pk"}]
    mock_sb.table().insert().execute.return_value = mock_execute
    set_supabase_client(mock_sb)

    resp = client.post(
        "/v1/coverage-requests",
        json={"page_url": "https://newbrand.pk/products/item-1"},
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "received"


def test_recommend_endpoint_guest_mode(client: TestClient) -> None:
    """POST /v1/recommend calculates recommendation with guest measurements."""
    mock_sb = MagicMock()

    # Product mock
    prod_exec = MagicMock()
    prod_exec.data = [
        {
            "id": "p-101",
            "name": "Boxy Tee",
            "category": "tshirt_top",
            "stretch_pct": 0,
            "size_chart_id": "sc-1",
            "size_charts": {
                "id": "sc-1",
                "measured_as": "circumference",
                "verified_at": "2026-01-01",
                "is_demo": False,
            },
        }
    ]

    # Chart rows mock
    chart_exec = MagicMock()
    chart_exec.data = [
        {"size_label": "S", "measurement_key": "chest", "value_cm": 98.0, "sort_order": 1},
        {"size_label": "M", "measurement_key": "chest", "value_cm": 104.0, "sort_order": 2},
        {"size_label": "L", "measurement_key": "chest", "value_cm": 110.0, "sort_order": 3},
        {"size_label": "XL", "measurement_key": "chest", "value_cm": 116.0, "sort_order": 4},
    ]

    def table_router(table_name: str) -> Any:
        tbl = MagicMock()
        if table_name == "products":
            tbl.select().eq().limit().execute.return_value = prod_exec
        elif table_name == "size_chart_rows":
            tbl.select().eq().order().execute.return_value = chart_exec
        return tbl

    mock_sb.table.side_effect = table_router
    set_supabase_client(mock_sb)

    payload = {
        "product_id": "p-101",
        "fit_preference": "regular",
        "measurements": {"chest_cm": 100.0},
    }
    resp = client.post("/v1/recommend?lang=en", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    rec = data["recommendation"]
    assert rec["recommended_size"] == "L"
    assert "explanation" in data
    assert "L is recommended" in data["explanation"]


def test_export_user_data(client: TestClient) -> None:
    """GET /v1/account/export returns customer data payload."""
    from app.auth import get_current_user

    mock_sb = MagicMock()
    mock_exec = MagicMock()
    mock_exec.data = [{"user_id": "u-1", "chest_cm": 100}]
    mock_sb.table().select().eq().execute.return_value = mock_exec
    set_supabase_client(mock_sb)

    # Override get_current_user
    app.dependency_overrides[get_current_user] = lambda: {"id": "u-1", "email": "shopper@example.com"}

    try:
        resp = client.get("/v1/account/export")
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == "u-1"
        assert "body_measurements" in data
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_delete_user_account(client: TestClient) -> None:
    """DELETE /v1/account wipes user data and auth user."""
    from app.auth import get_current_user

    mock_sb = MagicMock()
    set_supabase_client(mock_sb)

    app.dependency_overrides[get_current_user] = lambda: {"id": "u-1", "email": "shopper@example.com"}

    try:
        resp = client.delete("/v1/account")
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
