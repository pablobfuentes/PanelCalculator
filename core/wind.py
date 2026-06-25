"""Wind load helpers (CFE NTC-Viento 2020 inputs)."""

from __future__ import annotations

# Canonical exposure categories — defined here so imports survive Streamlit module cache.
WIND_EXPOSURE_CATEGORIES: tuple[str, ...] = ("A", "B", "C", "D")

EXPOSURE_DESCRIPTIONS: dict[str, str] = {
    "A": "Centers of large cities; surroundings with buildings mostly taller than 15 m.",
    "B": "Urban, suburban, or wooded areas; terrain with numerous closely spaced obstructions.",
    "C": "Open terrain with scattered obstructions; flat open country, grassland, or water surfaces.",
    "D": "Flat, unobstructed coastal areas exposed to wind flow over open water.",
}


def exposure_label(category: str) -> str:
    """Return a sidebar-friendly label for an exposure category."""
    if category not in WIND_EXPOSURE_CATEGORIES:
        raise ValueError(f"Unknown exposure category: {category}")
    return f"{category} — {EXPOSURE_DESCRIPTIONS[category]}"
