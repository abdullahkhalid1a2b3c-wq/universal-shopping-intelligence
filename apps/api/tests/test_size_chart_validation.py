"""Unit tests for size chart sanity checks."""

import pytest
from app.validation.size_chart import run_size_chart_sanity_checks


def test_valid_increasing_size_chart():
    """A well-proportioned size chart with increasing values should pass cleanly."""
    rows = [
        {"size_label": "S", "chest": 96.0, "waist": 82.0, "shoulder": 43.0, "length": 70.0},
        {"size_label": "M", "chest": 102.0, "waist": 88.0, "shoulder": 45.0, "length": 72.0},
        {"size_label": "L", "chest": 108.0, "waist": 94.0, "shoulder": 47.0, "length": 74.0},
        {"size_label": "XL", "chest": 114.0, "waist": 100.0, "shoulder": 49.0, "length": 76.0},
    ]

    res = run_size_chart_sanity_checks(rows=rows, measured_as="circumference", category="shirt")
    assert res.is_valid is True
    assert len(res.errors) == 0
    assert len(res.warnings) == 0


def test_non_increasing_size_chart():
    """Size chart where a larger size has smaller measurements should flag warnings."""
    rows = [
        {"size_label": "S", "chest": 96.0, "waist": 82.0},
        {"size_label": "M", "chest": 102.0, "waist": 88.0},
        {"size_label": "L", "chest": 98.0, "waist": 92.0},  # Chest decreased from M (102 -> 98)
    ]

    res = run_size_chart_sanity_checks(rows=rows, measured_as="circumference")
    assert res.is_valid is True  # Warning, not hard fatal error
    assert any("smaller chest" in w.lower() for w in res.warnings)


def test_large_jump_between_sizes():
    """Jump greater than 8 cm between consecutive sizes should flag a warning."""
    rows = [
        {"size_label": "S", "chest": 90.0, "waist": 76.0},
        {"size_label": "M", "chest": 104.0, "waist": 80.0},  # 14 cm jump in chest (> 8 cm)
    ]

    res = run_size_chart_sanity_checks(rows=rows, measured_as="circumference")
    assert res.is_valid is True
    assert any("large jump in chest" in w.lower() and "14.0 cm" in w for w in res.warnings)


def test_values_outside_normal_anatomical_range():
    """Values outside typical ranges should be flagged."""
    rows = [
        {"size_label": "S", "chest": 250.0, "waist": 15.0},  # Absurd values
    ]

    res = run_size_chart_sanity_checks(rows=rows, measured_as="circumference")
    assert res.is_valid is True
    assert any("outside typical range" in w.lower() for w in res.warnings)


def test_suspicious_flat_marked_as_circumference():
    """Chest under 70 cm marked as circumference should be flagged as likely flat."""
    rows = [
        {"size_label": "S", "chest": 52.0, "waist": 44.0},
        {"size_label": "M", "chest": 54.0, "waist": 46.0},
    ]

    res = run_size_chart_sanity_checks(rows=rows, measured_as="circumference")
    assert res.is_valid is True
    assert any("suspicious circumference" in w.lower() and "under 70 cm" in w.lower() for w in res.warnings)


def test_suspicious_circumference_marked_as_flat():
    """Chest over 80 cm marked as flat should be flagged as likely circumference."""
    rows = [
        {"size_label": "M", "chest": 102.0, "waist": 88.0},
    ]

    res = run_size_chart_sanity_checks(rows=rows, measured_as="flat")
    assert res.is_valid is True
    assert any("suspicious flat measurement" in w.lower() and "over 80 cm" in w.lower() for w in res.warnings)


def test_empty_rows_rejected():
    """Empty rows list should fail validation."""
    res = run_size_chart_sanity_checks(rows=[])
    assert res.is_valid is False
    assert len(res.errors) > 0
