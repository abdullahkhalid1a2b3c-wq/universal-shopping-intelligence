"""Pure Fit Engine implementation.

Deterministic, zero-ML rules engine for clothing size recommendations.
Operates on normalized garment measurements, body measurements, ease bands,
and fabric properties.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from app.fit.config import (
    CATEGORY_DIMENSION_WEIGHTS,
    CIRCUMFERENCE_DIMENSIONS,
    PENALTY_THRESHOLD,
    STRETCH_FACTOR,
    TARGET_EASE_BANDS,
    UNACCEPTABLE_MARGIN_CM,
    size_sort_key,
)
from app.fit.models import (
    AlternativeSize,
    BodyMeasurementsInput,
    FitRecommendationOutput,
    PerDimensionResult,
    PerSizeResult,
    ProductAttributesInput,
    SizeChartRowInput,
)


def compute_fit_recommendation(
    category: str,
    body: BodyMeasurementsInput,
    chart_rows: List[SizeChartRowInput],
    fit_preference: str = "regular",
    product: Optional[ProductAttributesInput] = None,
    measured_as: str = "circumference",
    chart_verified: bool = False,
    is_demo: bool = False,
) -> FitRecommendationOutput:
    """Compute product size recommendation using deterministic ease-band rules."""
    if product is None:
        product = ProductAttributesInput()

    fit_pref = fit_preference.lower() if fit_preference in {"fitted", "regular", "loose"} else "regular"

    # Map body fields to standard dimension names
    body_map: Dict[str, float] = {}
    if body.chest_cm is not None:
        body_map["chest"] = float(body.chest_cm)
    if body.waist_cm is not None:
        body_map["waist"] = float(body.waist_cm)
    if body.hip_cm is not None:
        body_map["hip"] = float(body.hip_cm)
    if body.shoulder_cm is not None:
        body_map["shoulder"] = float(body.shoulder_cm)
    if body.sleeve_cm is not None:
        body_map["sleeve"] = float(body.sleeve_cm)
    if body.inseam_cm is not None:
        body_map["inseam"] = float(body.inseam_cm)
    if body.thigh_cm is not None:
        body_map["thigh"] = float(body.thigh_cm)
    if body.torso_length_cm is not None:
        body_map["length"] = float(body.torso_length_cm)
    if body.kameez_length_cm is not None and "length" not in body_map:
        body_map["length"] = float(body.kameez_length_cm)

    # 1. Normalise the size chart
    # If measured_as == 'flat', multiply circumference dimensions by 2.
    is_flat = measured_as.lower() == "flat"
    garment_chart: Dict[str, Dict[str, float]] = {}
    size_sort_orders: Dict[str, int] = {}

    for row in chart_rows:
        val = float(row.value_cm)
        key = row.measurement_key.lower().strip()
        if is_flat and key in CIRCUMFERENCE_DIMENSIONS:
            val *= 2.0

        size = row.size_label.strip()
        if size not in garment_chart:
            garment_chart[size] = {}
            size_sort_orders[size] = row.sort_order

        garment_chart[size][key] = val

    # Order sizes deterministically regardless of input row order
    # Primary: size_sort_key(size), Secondary: size_sort_orders
    sorted_sizes = sorted(
        garment_chart.keys(),
        key=lambda s: (size_sort_key(s), size_sort_orders.get(s, 0)),
    )

    # Handle case: Only height and weight given (no primary measurements)
    has_primary_measurements = any(
        k in body_map for k in ("chest", "waist", "hip")
    )
    if not has_primary_measurements and (body.height_cm is not None or body.weight_kg is not None or not body_map):
        warnings = ["missing_dimension:chest", "missing_dimension:waist", "missing_dimension:hip"]
        if is_demo:
            warnings.append("demo_data")
        if not chart_verified:
            warnings.append("chart_not_verified")

        fallback_size = sorted_sizes[0] if sorted_sizes else "M"
        return FitRecommendationOutput(
            recommended_size=fallback_size,
            confidence_score=20,
            confidence_label="low",
            alternative_size=None,
            per_size=[
                PerSizeResult(size_label=s, total_penalty=99.0, is_acceptable=False)
                for s in sorted_sizes
            ],
            per_dimension=[],
            warnings=warnings,
            explanation_keys={
                "code": "insufficient_measurements",
                "message": "Chest, waist, or hip measurements are required to calculate fit.",
                "missing": ["chest", "waist", "hip"],
            },
            no_good_fit=True,
        )

    # Anthropometric estimation from height: If user provided height alongside primary
    # measurements (chest/waist/hip), estimate secondary dimensions if missing to avoid
    # unfair confidence penalties and provide informed sizing.
    if has_primary_measurements and body.height_cm is not None and float(body.height_cm) >= 100.0:
        h = float(body.height_cm)
        if "shoulder" not in body_map:
            chest_offset = max(0.0, (body_map.get("chest", 96.0) - 86.0) * 0.08)
            body_map["shoulder"] = round(h * 0.245 + chest_offset, 1)
        if "sleeve" not in body_map and category in {"shirt", "kurta"}:
            body_map["sleeve"] = round(h * 0.365, 1)
        if "inseam" not in body_map and category in {"trouser", "jeans"}:
            body_map["inseam"] = round(h * 0.455, 1)
        if "length" not in body_map:
            if category == "kurta":
                body_map["length"] = round(h * 0.585, 1)
            elif category in {"shirt", "tshirt_top"}:
                body_map["length"] = round(h * 0.415, 1)

    # Dimension definitions and weights for this category
    dim_weights = CATEGORY_DIMENSION_WEIGHTS.get(category, {})

    # Evaluate each size
    size_evaluations: List[Dict[str, Any]] = []

    for size_label in sorted_sizes:
        size_dims = garment_chart[size_label]
        total_penalty = 0.0
        is_acceptable = True
        compared_count = 0
        dim_details: List[PerDimensionResult] = []

        for dim_name, body_val in body_map.items():
            if dim_name not in size_dims:
                continue

            garment_val = size_dims[dim_name]
            ease = garment_val - body_val
            weight, is_key = dim_weights.get(dim_name, (1.0, False))

            # Ease band lookup
            lo, hi = TARGET_EASE_BANDS.get(
                (category, dim_name, fit_pref), (0.0, 6.0)
            )

            # Apply stretch to lower bound
            lo_effective = lo - body_val * (product.stretch_pct / 100.0) * STRETCH_FACTOR

            # Compute penalty
            if lo_effective <= ease <= hi:
                penalty = 0.0
            elif ease < lo_effective:
                penalty = ((lo_effective - ease) / 4.0) * weight * 2.0
            else:
                penalty = ((ease - hi) / 4.0) * weight

            total_penalty += penalty
            compared_count += 1

            # Check acceptability on key dimensions
            if is_key and ease < (lo_effective - UNACCEPTABLE_MARGIN_CM):
                is_acceptable = False

            # Verdict determination
            if ease < (lo_effective - UNACCEPTABLE_MARGIN_CM):
                verdict = "too_tight"
            elif ease < lo_effective:
                verdict = "snug"
            elif ease <= hi:
                verdict = "good"
            elif ease <= hi + UNACCEPTABLE_MARGIN_CM:
                verdict = "roomy"
            else:
                verdict = "too_loose"

            dim_details.append(
                PerDimensionResult(
                    dimension=dim_name,
                    body_cm=round(body_val, 1),
                    garment_cm=round(garment_val, 1),
                    ease_cm=round(ease, 1),
                    target_band=(round(lo_effective, 1), round(hi, 1)),
                    verdict=verdict,
                )
            )

        size_evaluations.append(
            {
                "size_label": size_label,
                "total_penalty": total_penalty,
                "is_acceptable": is_acceptable,
                "compared_count": compared_count,
                "dim_details": dim_details,
                "sort_key": size_sort_key(size_label),
            }
        )

    # 6. Pick the best size
    # Acceptable sizes with lowest total penalty; on tie, prefer the larger size (higher sort_key)
    acceptable_sizes = [s for s in size_evaluations if s["is_acceptable"]]

    no_good_fit = False
    if acceptable_sizes:
        # Sort by penalty ascending, then sort_key descending (tie-break to larger size)
        acceptable_sorted = sorted(
            acceptable_sizes,
            key=lambda s: (round(s["total_penalty"], 3), -s["sort_key"]),
        )
        best = acceptable_sorted[0]
        if best["total_penalty"] > PENALTY_THRESHOLD:
            no_good_fit = True
    else:
        # No acceptable size: pick closest size overall
        all_sorted = sorted(
            size_evaluations,
            key=lambda s: (round(s["total_penalty"], 3), -s["sort_key"]),
        )
        best = all_sorted[0]
        no_good_fit = True

    recommended_size = best["size_label"]

    # Candidate for alternative size (second best)
    alternative_size: Optional[AlternativeSize] = None
    all_evaluated_sorted = sorted(
        size_evaluations,
        key=lambda s: (round(s["total_penalty"], 3), -s["sort_key"]),
    )
    second_best = None
    for cand in all_evaluated_sorted:
        if cand["size_label"] != recommended_size:
            second_best = cand
            break

    is_between_sizes = False
    if second_best is not None:
        penalty_diff = abs(best["total_penalty"] - second_best["total_penalty"])
        if penalty_diff <= 0.5:
            is_between_sizes = True
            sec_sort = second_best["sort_key"]
            rec_sort = best["sort_key"]
            rel = "larger" if sec_sort > rec_sort else "more snug"
            alternative_size = AlternativeSize(
                size_label=second_best["size_label"],
                reason=f"Close alternative offering a {rel} fit.",
            )
        elif second_best["is_acceptable"]:
            sec_sort = second_best["sort_key"]
            rec_sort = best["sort_key"]
            rel = "relaxed" if sec_sort > rec_sort else "fitted"
            alternative_size = AlternativeSize(
                size_label=second_best["size_label"],
                reason=f"Alternative {rel} option.",
            )

    # 7. Confidence score calculation
    confidence = 100
    warnings: List[str] = []

    # Missing key dimensions
    key_dims = {
        dim: w
        for dim, (w, is_key) in dim_weights.items()
        if is_key
    }
    total_key_weight = sum(key_dims.values())
    compared_keys: Set[str] = {
        d.dimension for d in best["dim_details"]
    }

    missing_key_weight = sum(
        w for dim, w in key_dims.items() if dim not in compared_keys
    )
    if total_key_weight > 0 and missing_key_weight > 0:
        missing_pct = (missing_key_weight / total_key_weight) * 100.0
        confidence -= int(round(missing_pct * 0.4))  # Proportional impact

    # Missing dimension warnings
    for dim in dim_weights.keys():
        if dim not in body_map or dim not in garment_chart.get(recommended_size, {}):
            warnings.append(f"missing_dimension:{dim}")

    if not chart_verified:
        confidence -= 15
        warnings.append("chart_not_verified")

    if is_demo:
        confidence -= 10
        warnings.append("demo_data")

    if is_between_sizes:
        confidence -= 15
        warnings.append("between_two_sizes")

    if no_good_fit:
        confidence -= 20
        warnings.append("no_good_fit")

    confidence_score = max(0, min(100, confidence))
    if confidence_score >= 75:
        confidence_label = "high"
    elif confidence_score >= 50:
        confidence_label = "medium"
    else:
        confidence_label = "low"

    # Explanation keys structured for explain.py
    explanation_keys: Dict[str, Any] = {
        "category": category,
        "fit_preference": fit_pref,
        "recommended_size": recommended_size,
        "second_best_size": second_best["size_label"] if second_best else None,
        "is_between_sizes": is_between_sizes,
        "no_good_fit": no_good_fit,
        "stretch_pct": product.stretch_pct,
        "dimensions": [
            {
                "name": d.dimension,
                "verdict": d.verdict,
                "ease_cm": d.ease_cm,
            }
            for d in best["dim_details"]
        ],
    }

    per_size_results = [
        PerSizeResult(
            size_label=s["size_label"],
            total_penalty=round(s["total_penalty"], 2),
            is_acceptable=s["is_acceptable"],
        )
        for s in size_evaluations
    ]

    return FitRecommendationOutput(
        recommended_size=recommended_size,
        confidence_score=confidence_score,
        confidence_label=confidence_label,
        alternative_size=alternative_size,
        per_size=per_size_results,
        per_dimension=best["dim_details"],
        warnings=warnings,
        explanation_keys=explanation_keys,
        no_good_fit=no_good_fit,
    )

