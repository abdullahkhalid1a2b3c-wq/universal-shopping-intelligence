"""Unit tests for Pakistan-wide Brand Directory endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_directory_returns_curated_pakistani_brands():
    """Verify directory returns 20+ verified Pakistani brands."""
    resp = client.get("/v1/retailers/directory")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 25
    slugs = [b["slug"] for b in data["brands"]]
    assert "khaadi" in slugs
    assert "sapphire" in slugs
    assert "outfitters" in slugs
    assert "junaid-jamshed" in slugs


def test_directory_filters_by_category():
    """Verify category filtering for women/eastern/kids."""
    resp = client.get("/v1/retailers/directory?category=eastern")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] > 0
    for b in data["brands"]:
        assert "eastern" in [c.lower() for c in b["categories"]]


def test_directory_filters_by_letter():
    """Verify A-Z initial letter filtering."""
    resp = client.get("/v1/retailers/directory?letter=K")
    assert resp.status_code == 200
    data = resp.json()
    assert all(b["name"].upper().startswith("K") for b in data["brands"])


def test_get_single_brand_detail():
    """Verify detail lookup for a brand slug."""
    resp = client.get("/v1/retailers/khaadi")
    assert resp.status_code == 200
    b = resp.json()
    assert b["slug"] == "khaadi"
    assert b["name"] == "Khaadi"
    assert "official_size_chart_url" in b
    assert b["verification_status"] == "verified"

