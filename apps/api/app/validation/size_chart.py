"""Validation logic and sanity checks for fashion size charts."""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel


class SanityCheckResult(BaseModel):
    """Result of size chart sanity checks."""

    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []


# Expected anatomical garment ranges in centimetres [min, max]
EXPECTED_GARMENT_RANGES: Dict[str, Tuple[float, float]] = {
    "chest": (50.0, 160.0),
    "waist": (40.0, 150.0),
    "hip": (50.0, 160.0),
    "shoulder": (25.0, 70.0),
    "sleeve": (20.0, 100.0),
    "length": (30.0, 160.0),
    "inseam": (30.0, 110.0),
    "thigh": (25.0, 90.0),
    "rise": (18.0, 45.0),
    "hem": (15.0, 80.0),
}

# Standard size label order rank for comparison
STANDARD_SIZE_ORDER: Dict[str, int] = {
    "XXXS": 1,
    "3XS": 1,
    "XXS": 2,
    "2XS": 2,
    "XS": 3,
    "S": 4,
    "SMALL": 4,
    "M": 5,
    "MEDIUM": 5,
    "L": 6,
    "LARGE": 6,
    "XL": 7,
    "1XL": 7,
    "XXL": 8,
    "2XL": 8,
    "XXXL": 9,
    "3XL": 9,
    "4XL": 10,
    "5XL": 11,
}


def parse_size_rank(size_label: str) -> Optional[float]:
    """Determine sorting rank from size label (standard alphanumeric or numeric waist/chest)."""
    clean = size_label.strip().upper()
    if clean in STANDARD_SIZE_ORDER:
        return float(STANDARD_SIZE_ORDER[clean])
    # Check if purely numeric (e.g. 28, 30, 32, 34 or 38, 40, 42)
    try:
        return float(clean)
    except ValueError:
        return None


def run_size_chart_sanity_checks(
    rows: List[Dict[str, Any]],
    measured_as: str = "circumference",
    category: Optional[str] = None,
    gender_category: Optional[str] = None,
) -> SanityCheckResult:
    """Run comprehensive sanity checks on a set of size chart rows.

    Checks:
    1. Values should increase with size.
    2. Flag jumps larger than 8 cm between consecutive sizes.
    3. Flag values outside normal anatomical/garment ranges.
    4. Flag a chart that looks 'flat' while marked 'circumference' (chest under 70 cm).
    5. Flag a chart that looks 'circumference' while marked 'flat' (chest over 80 cm).
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not rows:
        return SanityCheckResult(
            is_valid=False,
            errors=["Size chart contains no measurement rows."],
            warnings=[],
        )

    # Group measurements by key and size_label
    # rows structure: [{"size_label": "S", "measurement_key": "chest", "value_cm": 96.0}, ...]
    # or tabular: [{"size_label": "S", "chest": 96.0, "waist": 80.0}, ...]
    normalized_data: Dict[str, Dict[str, float]] = {}

    for row in rows:
        size = str(row.get("size_label", "")).strip()
        if not size:
            errors.append("Encountered row with empty or missing size label.")
            continue

        if size not in normalized_data:
            normalized_data[size] = {}

        if "measurement_key" in row and "value_cm" in row:
            key = str(row["measurement_key"]).strip().lower()
            val = float(row["value_cm"])
            normalized_data[size][key] = val
        else:
            # Tabular row
            for k, v in row.items():
                if k in ("size_label", "sort_order", "id", "size_chart_id"):
                    continue
                if v is not None and str(v).strip() != "":
                    try:
                        normalized_data[size][k.lower()] = float(v)
                    except ValueError:
                        errors.append(f"Invalid non-numeric value '{v}' for {k} in size {size}")

    if not normalized_data:
        return SanityCheckResult(
            is_valid=False,
            errors=errors or ["No valid size data found."],
            warnings=warnings,
        )

    # Order sizes if possible
    size_rank_pairs = [(size, parse_size_rank(size)) for size in normalized_data.keys()]
    has_full_ranks = all(rank is not None for _, rank in size_rank_pairs)

    if has_full_ranks:
        ordered_sizes = [s for s, _ in sorted(size_rank_pairs, key=lambda p: p[1])]
    else:
        # Keep insertion order
        ordered_sizes = list(normalized_data.keys())

    # All unique measurement keys
    all_keys = set()
    for dims in normalized_data.values():
        all_keys.update(dims.keys())

    # 1. Sane ranges check & Flat vs Circumference checks
    for size, dims in normalized_data.items():
        for key, val in dims.items():
            if val <= 0:
                errors.append(f"Measurement {key} for size {size} must be greater than 0.")
                continue

            # Expected range check
            if key in EXPECTED_GARMENT_RANGES:
                exp_min, exp_max = EXPECTED_GARMENT_RANGES[key]
                if measured_as == "flat":
                    # For flat measurements, expected half-values
                    exp_min_flat = exp_min / 2.0
                    exp_max_flat = exp_max / 2.0
                    if val < exp_min_flat or val > exp_max_flat:
                        warnings.append(
                            f"Size {size} {key} ({val:.1f} cm) is outside typical flat range ({exp_min_flat:.0f}–{exp_max_flat:.0f} cm)."
                        )
                else:
                    if val < exp_min or val > exp_max:
                        warnings.append(
                            f"Size {size} {key} ({val:.1f} cm) is outside typical range ({exp_min:.0f}–{exp_max:.0f} cm)."
                        )

            # Flat vs Circumference Suspicion Check
            if key == "chest":
                if measured_as == "circumference" and val < 70.0:
                    warnings.append(
                        f"Suspicious circumference: Size {size} chest is {val:.1f} cm (under 70 cm). This chart may have been measured flat instead of circumference."
                    )
                elif measured_as == "flat" and val > 80.0:
                    warnings.append(
                        f"Suspicious flat measurement: Size {size} chest is {val:.1f} cm (over 80 cm). This chart may have been measured as circumference instead of flat."
                    )

            if key == "waist" and category in ("trouser", "jeans"):
                if measured_as == "circumference" and val < 50.0:
                    warnings.append(
                        f"Suspicious circumference: Size {size} waist is {val:.1f} cm. This may be a flat measurement."
                    )
                elif measured_as == "flat" and val > 75.0:
                    warnings.append(
                        f"Suspicious flat measurement: Size {size} waist is {val:.1f} cm. This may be a circumference measurement."
                    )

    # 2. Sequential checks: Values should increase with size & Jumps <= 8 cm
    for key in all_keys:
        # Check consecutive pairs in ordered sizes
        for i in range(len(ordered_sizes) - 1):
            s_curr = ordered_sizes[i]
            s_next = ordered_sizes[i + 1]

            v_curr = normalized_data[s_curr].get(key)
            v_next = normalized_data[s_next].get(key)

            if v_curr is not None and v_next is not None:
                # Value should not decrease as size increases
                if v_next < v_curr:
                    warnings.append(
                        f"Size {s_next} has smaller {key} ({v_next:.1f} cm) than size {s_curr} ({v_curr:.1f} cm). Values should increase with size."
                    )
                elif v_next == v_curr:
                    warnings.append(
                        f"Size {s_next} and {s_curr} have identical {key} ({v_curr:.1f} cm)."
                    )

                # Jump threshold check (> 8 cm)
                jump = v_next - v_curr
                max_jump = 8.0 if measured_as == "circumference" else 5.0
                if jump > max_jump:
                    warnings.append(
                        f"Large jump in {key}: {jump:.1f} cm difference between size {s_curr} ({v_curr:.1f} cm) and size {s_next} ({v_next:.1f} cm) exceeds {max_jump:.0f} cm limit."
                    )

    return SanityCheckResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
