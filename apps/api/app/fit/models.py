"""Pydantic data models for the fit engine inputs and outputs."""

from typing import Any, Dict, List, Literal, Optional, Tuple
from pydantic import BaseModel, Field


class BodyMeasurementsInput(BaseModel):
    """Customer body measurements in centimetres (all optional)."""

    chest_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    shoulder_cm: Optional[float] = None
    sleeve_cm: Optional[float] = None
    inseam_cm: Optional[float] = None
    thigh_cm: Optional[float] = None
    torso_length_cm: Optional[float] = None
    kameez_length_cm: Optional[float] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None


class ProductAttributesInput(BaseModel):
    """Product material and cut attributes."""

    stretch_pct: float = Field(default=0.0, ge=0.0, le=40.0)
    thickness: Optional[Literal["light", "medium", "heavy"]] = None
    fit_cut: Optional[Literal["slim", "regular", "relaxed"]] = None
    fabric: Optional[str] = None


class SizeChartRowInput(BaseModel):
    """Single dimension measurement from a retailer size chart."""

    size_label: str
    measurement_key: str
    value_cm: float
    sort_order: int = 0


class PerSizeResult(BaseModel):
    """Size evaluation result."""

    size_label: str
    total_penalty: float
    is_acceptable: bool


class PerDimensionResult(BaseModel):
    """Detailed dimension comparison for the recommended size."""

    dimension: str
    body_cm: float
    garment_cm: float
    ease_cm: float
    target_band: Tuple[float, float]
    verdict: Literal["too_tight", "snug", "good", "roomy", "too_loose"]


class AlternativeSize(BaseModel):
    """Alternative size candidate."""

    size_label: str
    reason: str


class FitRecommendationOutput(BaseModel):
    """Complete output produced by the pure fit engine."""

    recommended_size: str
    confidence_score: int = Field(ge=0, le=100)
    confidence_label: Literal["high", "medium", "low"]
    alternative_size: Optional[AlternativeSize] = None
    per_size: List[PerSizeResult]
    per_dimension: List[PerDimensionResult]
    warnings: List[str]
    explanation_keys: Dict[str, Any]
    no_good_fit: bool = False

