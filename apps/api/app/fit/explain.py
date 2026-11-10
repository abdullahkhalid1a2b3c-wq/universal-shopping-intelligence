"""Localized explanation generator for FitSense recommendations.

Converts structured explanation_keys into natural localized sentences
in English, Urdu, and Roman Urdu.
"""

import json
from pathlib import Path
from typing import Any, Dict

_I18N_DIR = Path(__file__).parent / "i18n"
_TEMPLATES: Dict[str, Dict[str, str]] = {}


def _load_templates(lang: str) -> Dict[str, str]:
    if lang not in _TEMPLATES:
        file_path = _I18N_DIR / f"{lang}.json"
        if not file_path.exists():
            file_path = _I18N_DIR / "en.json"
        with open(file_path, "r", encoding="utf-8") as f:
            _TEMPLATES[lang] = json.load(f)
    return _TEMPLATES[lang]


DIMENSION_NAMES = {
    "en": {"chest": "chest", "waist": "waist", "hip": "hips", "shoulder": "shoulders"},
    "ur": {"chest": "سینے", "waist": "کمر", "hip": "ہپ", "shoulder": "کندھوں"},
    "ur-roman": {"chest": "chest", "waist": "kamar", "hip": "hip", "shoulder": "kandhe"},
}


def generate_explanation(explanation_keys: Dict[str, Any], lang: str = "en") -> str:
    """Generate a localized human-readable sentence from structured explanation keys."""
    lang_key = lang.lower() if lang in {"en", "ur", "ur-roman"} else "en"
    templates = _load_templates(lang_key)

    if explanation_keys.get("code") == "insufficient_measurements":
        return templates.get("insufficient_measurements", "")

    rec_size = explanation_keys.get("recommended_size", "")
    sec_size = explanation_keys.get("second_best_size") or ""
    fit_pref = explanation_keys.get("fit_preference", "regular")
    is_between = explanation_keys.get("is_between_sizes", False)
    no_good_fit = explanation_keys.get("no_good_fit", False)

    if no_good_fit:
        tmpl = templates.get("no_good_fit", "")
        return tmpl.format(recommended_size=rec_size)

    if is_between and sec_size:
        tmpl = templates.get("between_sizes", "")
        return tmpl.format(recommended_size=rec_size, second_best_size=sec_size)

    # Check if a smaller size was tight on any dimension
    problem_dim = "chest"
    dims = explanation_keys.get("dimensions", [])
    for d in dims:
        if d.get("verdict") in {"snug", "good"}:
            problem_dim = d.get("name", "chest")
            break

    localized_dim = DIMENSION_NAMES.get(lang_key, {}).get(problem_dim, problem_dim)

    if sec_size:
        tmpl = templates.get("recommendation_tight_alt", "")
        return tmpl.format(
            recommended_size=rec_size,
            second_best_size=sec_size,
            problem_dim=localized_dim,
            fit_preference=fit_pref,
        )

    tmpl = templates.get("recommendation_normal", "")
    return tmpl.format(recommended_size=rec_size, fit_preference=fit_pref)

