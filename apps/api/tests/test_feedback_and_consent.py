"""Unit tests for fit feedback, k-anonymity peer summaries, and privacy/consent enforcement."""

import uuid
from typing import Any, Dict, List, Optional
import jwt
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.fit.feedback_rules import evaluate_size_chart_review_need
from app.main import app
from app.supabase_client import set_supabase_client


def make_test_token(user_id: str, email: str = "shopper@example.com") -> str:
    """Generate a valid HS256 test JWT."""
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "app_role": "customer",
    }
    secret = settings.supabase_jwt_secret or "secret"
    return jwt.encode(payload, secret, algorithm="HS256")


class MockDatabase:
    """In-memory mock database for Supabase table queries in tests."""

    def __init__(self):
        self.consents: List[Dict[str, Any]] = []
        self.body_measurements: List[Dict[str, Any]] = []
        self.fit_feedback: List[Dict[str, Any]] = []
        self.products: List[Dict[str, Any]] = []
        self.size_charts: List[Dict[str, Any]] = []
        self.saved_items: List[Dict[str, Any]] = []
        self.profiles: List[Dict[str, Any]] = []
        self.recommendations: List[Dict[str, Any]] = []
        self.reference_garments: List[Dict[str, Any]] = []
        self.fit_preferences: List[Dict[str, Any]] = []


class MockQueryBuilder:
    def __init__(self, db: MockDatabase, table_name: str):
        self.db = db
        self.table_name = table_name
        self._filters: List[tuple] = []
        self._update_data: Optional[Dict[str, Any]] = None
        self._insert_data: Optional[Any] = None
        self._action = "select"
        self._limit: Optional[int] = None

    def select(self, *args, **kwargs):
        self._action = "select"
        return self

    def insert(self, data):
        self._action = "insert"
        self._insert_data = data
        return self

    def update(self, data):
        self._action = "update"
        self._update_data = data
        return self

    def delete(self):
        self._action = "delete"
        return self

    def eq(self, column: str, value: Any):
        self._filters.append((column, value))
        return self

    def limit(self, count: int):
        self._limit = count
        return self

    def execute(self):
        table: List[Dict[str, Any]] = getattr(self.db, self.table_name, [])

        class MockResult:
            def __init__(self, data):
                self.data = data
                self.count = len(data)

        if self._action == "insert":
            inserted = []
            rows = [self._insert_data] if isinstance(self._insert_data, dict) else self._insert_data
            for r in rows:
                item = dict(r)
                if "id" not in item:
                    item["id"] = str(uuid.uuid4())
                table.append(item)
                inserted.append(item)
            return MockResult(inserted)

        # Filter matching rows
        matched_indices = []
        for idx, row in enumerate(table):
            match = True
            for col, val in self._filters:
                if str(row.get(col)) != str(val):
                    match = False
                    break
            if match:
                matched_indices.append(idx)

        if self._action == "delete":
            deleted = [table[i] for i in matched_indices]
            for idx in sorted(matched_indices, reverse=True):
                del table[idx]
            return MockResult(deleted)

        if self._action == "update":
            updated = []
            for idx in matched_indices:
                table[idx].update(self._update_data)
                updated.append(table[idx])
            return MockResult(updated)

        # Action == select
        results = [table[i] for i in matched_indices]
        if self._limit:
            results = results[: self._limit]
        return MockResult(results)


class MockSupabaseClient:
    def __init__(self, db: MockDatabase):
        self.db = db

        class MockAuthAdmin:
            def delete_user(self, user_id):
                return True

        class MockAuth:
            admin = MockAuthAdmin()

        self.auth = MockAuth()

    def table(self, name: str):
        return MockQueryBuilder(self.db, name)


@pytest.fixture
def test_db():
    db = MockDatabase()
    client = MockSupabaseClient(db)
    set_supabase_client(client)
    yield db
    set_supabase_client(None)


def test_pure_feedback_review_rules():
    """Verify tunable size chart review rule evaluation function."""
    # Under min_count (< 10)
    rows_few = [{"fit_result": "too_tight"}] * 9
    res = evaluate_size_chart_review_need(rows_few, min_count=10, threshold_pct=30.0)
    assert res["needs_review"] is False
    assert res["total_count"] == 9

    # 10 rows with 4 too_tight (40% > 30%)
    rows_tight = [{"fit_result": "too_tight"}] * 4 + [{"fit_result": "perfect"}] * 6
    res = evaluate_size_chart_review_need(rows_tight, min_count=10, threshold_pct=30.0)
    assert res["needs_review"] is True
    assert "High tight rate" in res["trigger_reason"]

    # 10 rows with 4 too_loose (40% > 30%)
    rows_loose = [{"fit_result": "too_loose"}] * 4 + [{"fit_result": "perfect"}] * 6
    res = evaluate_size_chart_review_need(rows_loose, min_count=10, threshold_pct=30.0)
    assert res["needs_review"] is True
    assert "High loose rate" in res["trigger_reason"]

    # 10 rows with 8 perfect (80%), acceptable fit
    rows_perfect = [{"fit_result": "perfect"}] * 8 + [{"fit_result": "too_tight"}] * 2
    res = evaluate_size_chart_review_need(rows_perfect, min_count=10, threshold_pct=30.0)
    assert res["needs_review"] is False


def test_feedback_submission_one_per_user_per_product_per_size(test_db):
    """Submitting feedback twice for the same user, product, and size returns 409 Conflict."""
    token = make_test_token("user-101")
    prod_id = str(uuid.uuid4())
    client = TestClient(app)

    payload = {
        "product_id": prod_id,
        "size_bought": "M",
        "fit_result": "perfect",
        "was_returned": False,
    }

    # First submission -> 201
    res1 = client.post("/v1/feedback", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res1.status_code == 201
    assert res1.json()["status"] == "submitted"

    # Second submission with same size -> 409 Conflict
    res2 = client.post("/v1/feedback", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res2.status_code == 409
    assert "already submitted feedback" in res2.json()["detail"]


def test_feedback_respects_measurement_consent(test_db):
    """Only stores body_snapshot in feedback when store_measurements consent is explicitly true."""
    client = TestClient(app)
    prod_id = str(uuid.uuid4())

    # User 1: No consent granted
    token1 = make_test_token("user-no-consent")
    test_db.body_measurements.append({"user_id": "user-no-consent", "chest_cm": 98.0, "waist_cm": 84.0})
    test_db.consents.append({"user_id": "user-no-consent", "consent_type": "store_measurements", "granted": False})

    res1 = client.post(
        "/v1/feedback",
        json={"product_id": prod_id, "size_bought": "M", "fit_result": "perfect"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert res1.status_code == 201
    fb_no_consent = next(r for r in test_db.fit_feedback if r["user_id"] == "user-no-consent")
    assert fb_no_consent["body_snapshot"] is None

    # User 2: Consent granted
    token2 = make_test_token("user-with-consent")
    test_db.body_measurements.append({"user_id": "user-with-consent", "chest_cm": 102.0, "waist_cm": 88.0})
    test_db.consents.append({"user_id": "user-with-consent", "consent_type": "store_measurements", "granted": True})

    res2 = client.post(
        "/v1/feedback",
        json={"product_id": prod_id, "size_bought": "L", "fit_result": "perfect"},
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert res2.status_code == 201
    fb_with_consent = next(r for r in test_db.fit_feedback if r["user_id"] == "user-with-consent")
    assert fb_with_consent["body_snapshot"] is not None
    assert fb_with_consent["body_snapshot"]["chest_cm"] == 102.0


def test_peer_feedback_summary_k_anonymity(test_db):
    """Peer feedback summary guarantees k-anonymity (>= 5 similar shoppers within 6 cm chest)."""
    prod_id = str(uuid.uuid4())
    client = TestClient(app)

    # 1. Less than 5 shoppers (e.g. 4) -> has_summary = False
    for i in range(4):
        test_db.fit_feedback.append({
            "product_id": prod_id,
            "size_bought": "M",
            "fit_result": "perfect",
            "body_snapshot": {"chest_cm": 100.0 + i},  # diff <= 6 cm from 100
        })

    res = client.get(f"/v1/feedback/summary?product_id={prod_id}&recommended_size=M&chest_cm=100.0&lang=en")
    assert res.status_code == 200
    data = res.json()
    assert data["has_summary"] is False
    assert data["sample_size"] == 4
    assert data["summary_text"] is None

    # 2. Add 2 more shoppers (total 6 similar) -> has_summary = True
    test_db.fit_feedback.append({
        "product_id": prod_id,
        "size_bought": "M",
        "fit_result": "perfect",
        "body_snapshot": {"chest_cm": 101.0},
    })
    test_db.fit_feedback.append({
        "product_id": prod_id,
        "size_bought": "M",
        "fit_result": "slightly_tight",
        "body_snapshot": {"chest_cm": 102.0},
    })

    # Test English
    res_en = client.get(f"/v1/feedback/summary?product_id={prod_id}&recommended_size=M&chest_cm=100.0&lang=en")
    assert res_en.status_code == 200
    data_en = res_en.json()
    assert data_en["has_summary"] is True
    assert "people with a similar chest size said M fit well" in data_en["summary_text"]

    # Test Urdu
    res_ur = client.get(f"/v1/feedback/summary?product_id={prod_id}&recommended_size=M&chest_cm=100.0&lang=ur")
    assert res_ur.status_code == 200
    assert "خریداروں نے بتایا" in res_ur.json()["summary_text"]

    # Test Roman Urdu
    res_rom = client.get(f"/v1/feedback/summary?product_id={prod_id}&recommended_size=M&chest_cm=100.0&lang=ur-roman")
    assert res_rom.status_code == 200
    assert "Miltay jultay chest size" in res_rom.json()["summary_text"]


def test_withdraw_consent_clears_measurements_and_snapshots(test_db):
    """POST /v1/account/withdraw-consent wipes body measurements and clears feedback snapshots."""
    user_id = "user-withdraw"
    token = make_test_token(user_id)
    client = TestClient(app)

    test_db.consents.append({"user_id": user_id, "consent_type": "store_measurements", "granted": True})
    test_db.body_measurements.append({"user_id": user_id, "chest_cm": 95.0})
    test_db.fit_feedback.append({"user_id": user_id, "product_id": "p1", "body_snapshot": {"chest_cm": 95.0}})

    res = client.post("/v1/account/withdraw-consent", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "withdrawn"

    # Consents updated to false
    assert test_db.consents[0]["granted"] is False
    # Measurements deleted
    assert len(test_db.body_measurements) == 0
    # Snapshot wiped
    assert test_db.fit_feedback[0]["body_snapshot"] is None


def test_delete_account_anonymize_vs_delete_feedback(test_db):
    """DELETE /v1/account properly anonymizes or deletes user data based on keep_anonymous_feedback."""
    client = TestClient(app)

    # 1. keep_anonymous_feedback = True
    uid1 = "user-delete-anon"
    token1 = make_test_token(uid1)
    test_db.profiles.append({"user_id": uid1, "email": "del1@example.com"})
    test_db.fit_feedback.append({"user_id": uid1, "product_id": "p1", "fit_result": "perfect", "body_snapshot": {"chest_cm": 100.0}})

    res1 = client.delete("/v1/account?keep_anonymous_feedback=true", headers={"Authorization": f"Bearer {token1}"})
    assert res1.status_code == 200
    # Profile deleted
    assert not any(p["user_id"] == uid1 for p in test_db.profiles)
    # Feedback preserved but disassociated
    fb1 = test_db.fit_feedback[0]
    assert fb1["user_id"] is None
    assert fb1["body_snapshot"] is None

    # 2. keep_anonymous_feedback = False
    uid2 = "user-delete-purge"
    token2 = make_test_token(uid2)
    test_db.profiles.append({"user_id": uid2, "email": "del2@example.com"})
    test_db.fit_feedback.append({"user_id": uid2, "product_id": "p2", "fit_result": "too_tight", "body_snapshot": {"chest_cm": 90.0}})

    res2 = client.delete("/v1/account?keep_anonymous_feedback=false", headers={"Authorization": f"Bearer {token2}"})
    assert res2.status_code == 200
    # Profile deleted
    assert not any(p["user_id"] == uid2 for p in test_db.profiles)
    # Feedback completely deleted
    assert not any(fb.get("user_id") == uid2 for fb in test_db.fit_feedback)
