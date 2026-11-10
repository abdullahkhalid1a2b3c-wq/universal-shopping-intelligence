"""Fit engine configuration and ease bands.

NOTE: These ease bands and weights are starting baseline defaults
and should be tuned after testing against real garments and tailors.
"""

from typing import Dict, List, Tuple

# Named constants
STRETCH_FACTOR: float = 0.5
UNACCEPTABLE_MARGIN_CM: float = 4.0
PENALTY_THRESHOLD: float = 15.0

# Circumference vs length dimension classifications
CIRCUMFERENCE_DIMENSIONS = frozenset({"chest", "waist", "hip", "hem", "thigh"})
LENGTH_DIMENSIONS = frozenset(
    {"length", "inseam", "sleeve", "shoulder", "rise", "torso_length", "kameez_length"}
)

# Standard size label order for ordering and tie-breaking (earlier = smaller, later = larger)
STANDARD_SIZE_ORDER: List[str] = [
    "XXS",
    "2XS",
    "XS",
    "S",
    "M",
    "L",
    "XL",
    "XXL",
    "2XL",
    "3XL",
    "4XL",
    "5XL",
]


def size_sort_key(size_label: str) -> float:
    """Return a sortable numeric key for a size label.

    Handles standard alpha sizes ('S', 'M', 'L') and numeric sizes ('30', '32', '15.5').
    """
    clean = size_label.strip().upper()
    if clean in STANDARD_SIZE_ORDER:
        return float(STANDARD_SIZE_ORDER.index(clean))
    try:
        return float(clean)
    except ValueError:
        return 999.0


# Category Dimension Config: (weight, is_key)
CATEGORY_DIMENSION_WEIGHTS: Dict[str, Dict[str, Tuple[float, bool]]] = {
    "tshirt_top": {
        "chest": (3.0, True),
        "shoulder": (1.5, True),
        "length": (1.0, False),
    },
    "shirt": {
        "chest": (3.0, True),
        "shoulder": (1.5, True),
        "sleeve": (1.0, False),
        "waist": (1.0, False),
    },
    "kurta": {
        "chest": (3.0, True),
        "shoulder": (1.5, True),
        "hip": (1.0, False),
        "sleeve": (1.0, False),
        "length": (1.0, False),
    },
    "trouser": {
        "waist": (3.0, True),
        "hip": (2.0, True),
        "inseam": (1.0, False),
        "thigh": (1.0, False),
    },
    "jeans": {
        "waist": (3.0, True),
        "hip": (2.0, True),
        "inseam": (1.0, False),
        "thigh": (1.0, False),
    },
    "dress": {
        "chest": (2.0, True),
        "waist": (2.0, True),
        "hip": (2.0, True),
    },
}

# Target ease bands in cm: (lo, hi) per (category, dimension, fit_preference)
TARGET_EASE_BANDS: Dict[Tuple[str, str, str], Tuple[float, float]] = {
    # tshirt_top
    ("tshirt_top", "chest", "fitted"): (4.0, 8.0),
    ("tshirt_top", "chest", "regular"): (8.0, 14.0),
    ("tshirt_top", "chest", "loose"): (14.0, 22.0),
    ("tshirt_top", "shoulder", "fitted"): (-1.0, 2.0),
    ("tshirt_top", "shoulder", "regular"): (0.0, 3.0),
    ("tshirt_top", "shoulder", "loose"): (2.0, 6.0),
    ("tshirt_top", "length", "fitted"): (-2.0, 4.0),
    ("tshirt_top", "length", "regular"): (0.0, 6.0),
    ("tshirt_top", "length", "loose"): (2.0, 10.0),
    # shirt
    ("shirt", "chest", "fitted"): (6.0, 10.0),
    ("shirt", "chest", "regular"): (10.0, 16.0),
    ("shirt", "chest", "loose"): (16.0, 24.0),
    ("shirt", "shoulder", "fitted"): (-1.0, 2.0),
    ("shirt", "shoulder", "regular"): (0.0, 3.0),
    ("shirt", "shoulder", "loose"): (2.0, 6.0),
    ("shirt", "sleeve", "fitted"): (-1.0, 2.0),
    ("shirt", "sleeve", "regular"): (-1.0, 2.0),
    ("shirt", "sleeve", "loose"): (-1.0, 2.0),
    ("shirt", "waist", "fitted"): (4.0, 8.0),
    ("shirt", "waist", "regular"): (8.0, 14.0),
    ("shirt", "waist", "loose"): (14.0, 20.0),
    # kurta
    ("kurta", "chest", "fitted"): (8.0, 12.0),
    ("kurta", "chest", "regular"): (12.0, 20.0),
    ("kurta", "chest", "loose"): (20.0, 28.0),
    ("kurta", "shoulder", "fitted"): (-1.0, 2.0),
    ("kurta", "shoulder", "regular"): (0.0, 3.0),
    ("kurta", "shoulder", "loose"): (2.0, 6.0),
    ("kurta", "hip", "fitted"): (6.0, 10.0),
    ("kurta", "hip", "regular"): (10.0, 18.0),
    ("kurta", "hip", "loose"): (18.0, 26.0),
    ("kurta", "sleeve", "fitted"): (-1.0, 2.0),
    ("kurta", "sleeve", "regular"): (-1.0, 2.0),
    ("kurta", "sleeve", "loose"): (-1.0, 2.0),
    ("kurta", "length", "fitted"): (0.0, 10.0),
    ("kurta", "length", "regular"): (0.0, 10.0),
    ("kurta", "length", "loose"): (0.0, 10.0),
    # trouser
    ("trouser", "waist", "fitted"): (0.0, 2.0),
    ("trouser", "waist", "regular"): (2.0, 5.0),
    ("trouser", "waist", "loose"): (5.0, 9.0),
    ("trouser", "hip", "fitted"): (4.0, 8.0),
    ("trouser", "hip", "regular"): (8.0, 14.0),
    ("trouser", "hip", "loose"): (14.0, 20.0),
    ("trouser", "inseam", "fitted"): (-2.0, 3.0),
    ("trouser", "inseam", "regular"): (-2.0, 3.0),
    ("trouser", "inseam", "loose"): (-2.0, 3.0),
    ("trouser", "thigh", "fitted"): (4.0, 8.0),
    ("trouser", "thigh", "regular"): (6.0, 12.0),
    ("trouser", "thigh", "loose"): (10.0, 16.0),
    # jeans
    ("jeans", "waist", "fitted"): (0.0, 1.0),
    ("jeans", "waist", "regular"): (1.0, 3.0),
    ("jeans", "waist", "loose"): (3.0, 6.0),
    ("jeans", "hip", "fitted"): (2.0, 6.0),
    ("jeans", "hip", "regular"): (6.0, 12.0),
    ("jeans", "hip", "loose"): (12.0, 18.0),
    ("jeans", "inseam", "fitted"): (-2.0, 3.0),
    ("jeans", "inseam", "regular"): (-2.0, 3.0),
    ("jeans", "inseam", "loose"): (-2.0, 3.0),
    ("jeans", "thigh", "fitted"): (4.0, 8.0),
    ("jeans", "thigh", "regular"): (6.0, 12.0),
    ("jeans", "thigh", "loose"): (12.0, 18.0),
    # dress
    ("dress", "chest", "fitted"): (3.0, 7.0),
    ("dress", "chest", "regular"): (6.0, 12.0),
    ("dress", "chest", "loose"): (12.0, 20.0),
    ("dress", "waist", "fitted"): (2.0, 6.0),
    ("dress", "waist", "regular"): (6.0, 14.0),
    ("dress", "waist", "loose"): (14.0, 24.0),
    ("dress", "hip", "fitted"): (4.0, 8.0),
    ("dress", "hip", "regular"): (8.0, 16.0),
    ("dress", "hip", "loose"): (16.0, 24.0),
}

