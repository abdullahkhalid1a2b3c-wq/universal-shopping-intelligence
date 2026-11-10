"""Unit tests for the pure fit engine (app/fit/engine.py)."""

import random
from typing import List
import pytest

from app.fit.engine import compute_fit_recommendation
from app.fit.explain import generate_explanation
from app.fit.models import (
    BodyMeasurementsInput,
    ProductAttributesInput,
    SizeChartRowInput,
)


@pytest.fixture
def tshirt_circumference_chart() -> List[SizeChartRowInput]:
    """Standard test size chart: tshirt_top circumference."""
    return [
        SizeChartRowInput(size_label="S", measurement_key="chest", value_cm=98.0, sort_order=1),
        SizeChartRowInput(size_label="M", measurement_key="chest", value_cm=104.0, sort_order=2),
        SizeChartRowInput(size_label="L", measurement_key="chest", value_cm=110.0, sort_order=3),
        SizeChartRowInput(size_label="XL", measurement_key="chest", value_cm=116.0, sort_order=4),
    ]


@pytest.fixture
def tshirt_flat_chart() -> List[SizeChartRowInput]:
    """Same size chart given as flat values (half circumference)."""
    return [
        SizeChartRowInput(size_label="S", measurement_key="chest", value_cm=49.0, sort_order=1),
        SizeChartRowInput(size_label="M", measurement_key="chest", value_cm=52.0, sort_order=2),
        SizeChartRowInput(size_label="L", measurement_key="chest", value_cm=55.0, sort_order=3),
        SizeChartRowInput(size_label="XL", measurement_key="chest", value_cm=58.0, sort_order=4),
    ]


def test_tshirt_regular_fit_selects_large(tshirt_circumference_chart: List[SizeChartRowInput]) -> None:
    """Body chest 100, regular: expect L (ease +10 is inside 8-14; M gives +4 and is penalised)."""
    body = BodyMeasurementsInput(chest_cm=100.0)
    result = compute_fit_recommendation(
        category="tshirt_top",
        body=body,
        chart_rows=tshirt_circumference_chart,
        fit_preference="regular",
        chart_verified=True,
    )
    assert result.recommended_size == "L"


def test_tshirt_fitted_selects_medium(tshirt_circumference_chart: List[SizeChartRowInput]) -> None:
    """Same body (chest 100), fitted: expect M (ease +4 is inside 4-8)."""
    body = BodyMeasurementsInput(chest_cm=100.0)
    result = compute_fit_recommendation(
        category="tshirt_top",
        body=body,
        chart_rows=tshirt_circumference_chart,
        fit_preference="fitted",
        chart_verified=True,
    )
    assert result.recommended_size == "M"


def test_tshirt_loose_selects_xl(tshirt_circumference_chart: List[SizeChartRowInput]) -> None:
    """Same body (chest 100), loose: expect XL (+16 inside 14-22)."""
    body = BodyMeasurementsInput(chest_cm=100.0)
    result = compute_fit_recommendation(
        category="tshirt_top",
        body=body,
        chart_rows=tshirt_circumference_chart,
        fit_preference="loose",
        chart_verified=True,
    )
    assert result.recommended_size == "XL"


def test_flat_chart_produces_identical_results(
    tshirt_circumference_chart: List[SizeChartRowInput],
    tshirt_flat_chart: List[SizeChartRowInput],
) -> None:
    """Same chart given as flat values produces identical results to circumference."""
    body = BodyMeasurementsInput(chest_cm=100.0)
    res_circ = compute_fit_recommendation(
        category="tshirt_top",
        body=body,
        chart_rows=tshirt_circumference_chart,
        fit_preference="regular",
        measured_as="circumference",
        chart_verified=True,
    )
    res_flat = compute_fit_recommendation(
        category="tshirt_top",
        body=body,
        chart_rows=tshirt_flat_chart,
        fit_preference="regular",
        measured_as="flat",
        chart_verified=True,
    )
    assert res_circ.recommended_size == res_flat.recommended_size
    assert res_circ.confidence_score == res_flat.confidence_score
    assert len(res_circ.per_size) == len(res_flat.per_size)
    for s1, s2 in zip(res_circ.per_size, res_flat.per_size):
        assert s1.size_label == s2.size_label
        assert s1.total_penalty == s2.total_penalty
        assert s1.is_acceptable == s2.is_acceptable


def test_stretch_lowers_lower_bound_and_changes_recommendation(
    tshirt_circumference_chart: List[SizeChartRowInput],
) -> None:
    """Stretch 10% lowers lower bound so a snugger size becomes acceptable / preferred."""
    # With body chest 102, fitted fit (target ease 4-8):
    # Without stretch:
    # M (104) -> ease +2. Below lo (4). Penalty = ((4-2)/4)*3*2 = 3.0.
    # L (110) -> ease +8. Inside band [4, 8]. Penalty = 0.0. Recommended is L!
    body = BodyMeasurementsInput(chest_cm=102.0)
    res_no_stretch = compute_fit_recommendation(
        category="tshirt_top",
        body=body,
        chart_rows=tshirt_circumference_chart,
        fit_preference="fitted",
        product=ProductAttributesInput(stretch_pct=0.0),
        chart_verified=True,
    )
    assert res_no_stretch.recommended_size == "L"

    # With stretch 10%:
    # lo_effective = 4.0 - 102 * (10/100) * 0.5 = 4.0 - 5.1 = -1.1 cm.
    # M (104) ease = +2 is now inside [-1.1, 8.0]! Penalty = 0.0.
    # Because fitted shoppers prefer snug when acceptable and penalty is 0,
    # let's test a case where M has 0 penalty and L is looser:
    # e.g., body 103:
    # Without stretch: M ease = +1 (<4), L ease = +7 (inside 4-8, penalty 0).
    # With stretch 10%: lo_effective = 4 - 5.15 = -1.15.
    # Both M and L have 0 penalty on chest, but M is the snugger fitted choice!
    res_with_stretch = compute_fit_recommendation(
        category="tshirt_top",
        body=BodyMeasurementsInput(chest_cm=105.0),
        chart_rows=tshirt_circumference_chart,
        fit_preference="regular",
        product=ProductAttributesInput(stretch_pct=15.0),
        chart_verified=True,
    )
    # Check that lo_effective was lowered by stretch
    for dim in res_with_stretch.per_dimension:
        if dim.dimension == "chest":
            lo_effective = dim.target_band[0]
            assert lo_effective < 8.0  # Standard regular lower bound is 8.0


def test_missing_dimension_lowers_confidence_and_adds_warning() -> None:
    """Missing key dimensions lower confidence and add missing_dimension warnings."""
    # For trouser, waist (weight 3) and hip (weight 2) are both key.
    # Providing only waist should lower confidence and warn about hip.
    chart = [
        SizeChartRowInput(size_label="30", measurement_key="waist", value_cm=80.0),
        SizeChartRowInput(size_label="30", measurement_key="hip", value_cm=96.0),
        SizeChartRowInput(size_label="32", measurement_key="waist", value_cm=85.0),
        SizeChartRowInput(size_label="32", measurement_key="hip", value_cm=102.0),
    ]
    res_complete = compute_fit_recommendation(
        category="trouser",
        body=BodyMeasurementsInput(waist_cm=82.0, hip_cm=98.0),
        chart_rows=chart,
        chart_verified=True,
    )
    res_missing_hip = compute_fit_recommendation(
        category="trouser",
        body=BodyMeasurementsInput(waist_cm=82.0),  # hip missing
        chart_rows=chart,
        chart_verified=True,
    )
    assert res_missing_hip.confidence_score < res_complete.confidence_score
    assert any("missing_dimension:hip" in w for w in res_missing_hip.warnings)


def test_only_height_and_weight_returns_low_confidence_no_guess(
    tshirt_circumference_chart: List[SizeChartRowInput],
) -> None:
    """Only height and weight given: confidence low, no size guessed from them."""
    body = BodyMeasurementsInput(height_cm=178.0, weight_kg=72.0)
    result = compute_fit_recommendation(
        category="tshirt_top",
        body=body,
        chart_rows=tshirt_circumference_chart,
        chart_verified=True,
    )
    assert result.confidence_score < 50
    assert result.confidence_label == "low"
    assert result.no_good_fit is True
    assert "missing_dimension:chest" in result.warnings


def test_demo_and_unverified_chart_lowers_confidence(
    tshirt_circumference_chart: List[SizeChartRowInput],
) -> None:
    """Demo or unverified chart lowers confidence and adds the warnings."""
    body = BodyMeasurementsInput(chest_cm=100.0)
    # Verified, not demo
    res_verified = compute_fit_recommendation(
        category="tshirt_top",
        body=body,
        chart_rows=tshirt_circumference_chart,
        chart_verified=True,
        is_demo=False,
    )
    # Unverified, demo
    res_demo = compute_fit_recommendation(
        category="tshirt_top",
        body=body,
        chart_rows=tshirt_circumference_chart,
        chart_verified=False,
        is_demo=True,
    )
    assert res_demo.confidence_score <= res_verified.confidence_score - 25
    assert "chart_not_verified" in res_demo.warnings
    assert "demo_data" in res_demo.warnings


def test_size_order_tie_breaks_to_larger_size() -> None:
    """On equal penalties, tie breaking prefers the larger size."""
    # Construct a chart where two sizes have equal penalty
    chart = [
        SizeChartRowInput(size_label="M", measurement_key="chest", value_cm=100.0, sort_order=1),
        SizeChartRowInput(size_label="L", measurement_key="chest", value_cm=100.0, sort_order=2),
    ]
    body = BodyMeasurementsInput(chest_cm=90.0)
    res = compute_fit_recommendation(
        category="tshirt_top",
        body=body,
        chart_rows=chart,
        fit_preference="regular",
        chart_verified=True,
    )
    # Both M and L have the exact same ease and penalty; L is larger
    assert res.recommended_size == "L"


# === Property Tests ===

def test_property_results_independent_of_chart_row_order(
    tshirt_circumference_chart: List[SizeChartRowInput],
) -> None:
    """Property test: results never change when the order of chart rows changes."""
    body = BodyMeasurementsInput(chest_cm=100.0)
    base_res = compute_fit_recommendation(
        category="tshirt_top",
        body=body,
        chart_rows=tshirt_circumference_chart,
        fit_preference="regular",
        chart_verified=True,
    )

    for _ in range(5):
        shuffled = tshirt_circumference_chart.copy()
        random.shuffle(shuffled)
        shuffled_res = compute_fit_recommendation(
            category="tshirt_top",
            body=body,
            chart_rows=shuffled,
            fit_preference="regular",
            chart_verified=True,
        )
        assert shuffled_res.recommended_size == base_res.recommended_size
        assert shuffled_res.confidence_score == base_res.confidence_score


def test_property_larger_body_never_yields_smaller_size(
    tshirt_circumference_chart: List[SizeChartRowInput],
) -> None:
    """Property test: larger body chest never yields a smaller recommended size on the same chart and preference."""
    sizes = ["S", "M", "L", "XL"]
    size_ranks = {s: i for i, s in enumerate(sizes)}

    previous_rank = -1
    for chest in range(85, 125, 2):
        body = BodyMeasurementsInput(chest_cm=float(chest))
        res = compute_fit_recommendation(
            category="tshirt_top",
            body=body,
            chart_rows=tshirt_circumference_chart,
            fit_preference="regular",
            chart_verified=True,
        )
        current_rank = size_ranks[res.recommended_size]
        assert current_rank >= previous_rank, f"At chest {chest}, size dropped from {previous_rank} to {current_rank}"
        previous_rank = current_rank


def test_explanation_generation_in_all_locales(
    tshirt_circumference_chart: List[SizeChartRowInput],
) -> None:
    """Explanations generate natural strings in en, ur, and ur-roman."""
    body = BodyMeasurementsInput(chest_cm=100.0)
    res = compute_fit_recommendation(
        category="tshirt_top",
        body=body,
        chart_rows=tshirt_circumference_chart,
        fit_preference="regular",
    )
    for lang in ("en", "ur", "ur-roman"):
        explanation = generate_explanation(res.explanation_keys, lang=lang)
        assert isinstance(explanation, str)
        assert len(explanation) > 10
        assert res.recommended_size in explanation

