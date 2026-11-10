"""Feedback-driven quality control rules for retailer size charts.

Rule Specification:
When a product's size receives at least 10 feedback submissions and more than 30%
report either 'too_tight' (or 'too_loose'), flag the product's size chart
with needs_review = true.

NOTE: Recommendations are NOT changed automatically by this rule.
It flags the size chart in retailer and admin portals for manual brand audit.
"""

from typing import Any, Dict, List, Optional

MIN_FEEDBACK_THRESHOLD = 10
DISSATISFACTION_THRESHOLD_PCT = 30.0


def evaluate_size_chart_review_need(
    feedback_rows: List[Dict[str, Any]],
    min_count: int = MIN_FEEDBACK_THRESHOLD,
    threshold_pct: float = DISSATISFACTION_THRESHOLD_PCT,
) -> Dict[str, Any]:
    """Evaluate whether customer feedback indicates a size chart calibration issue.

    Parameters
    ----------
    feedback_rows : List[Dict[str, Any]]
        List of fit_feedback entries for a specific size.
        Must contain 'fit_result' in ('too_tight', 'slightly_tight', 'perfect', 'slightly_loose', 'too_loose').
    min_count : int, default 10
        Minimum number of feedback submissions required before triggering the flag.
    threshold_pct : float, default 30.0
        Percentage threshold of extreme dissatisfaction ('too_tight' or 'too_loose').

    Returns
    -------
    Dict[str, Any]
        Dictionary with evaluation result, statistics, and trigger reason.
    """
    total = len(feedback_rows)
    if total < min_count:
        return {
            "needs_review": False,
            "total_count": total,
            "min_required": min_count,
            "too_tight_pct": 0.0,
            "too_loose_pct": 0.0,
            "trigger_reason": None,
        }

    too_tight_count = sum(1 for r in feedback_rows if r.get("fit_result") == "too_tight")
    too_loose_count = sum(1 for r in feedback_rows if r.get("fit_result") == "too_loose")

    too_tight_pct = round((too_tight_count / total) * 100, 2)
    too_loose_pct = round((too_loose_count / total) * 100, 2)

    needs_review = False
    trigger_reason: Optional[str] = None

    if too_tight_pct > threshold_pct:
        needs_review = True
        trigger_reason = f"High tight rate: {too_tight_pct}% reported 'too_tight' (threshold {threshold_pct}%)"
    elif too_loose_pct > threshold_pct:
        needs_review = True
        trigger_reason = f"High loose rate: {too_loose_pct}% reported 'too_loose' (threshold {threshold_pct}%)"

    return {
        "needs_review": needs_review,
        "total_count": total,
        "min_required": min_count,
        "too_tight_pct": too_tight_pct,
        "too_loose_pct": too_loose_pct,
        "trigger_reason": trigger_reason,
    }

