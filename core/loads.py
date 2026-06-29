"""Factored load combinations per CFE (NTC) for structural analysis."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoadCombination:
    """One factored load combination for the FEA solver."""

    combo_id: str
    expression: str
    factor_D: float
    factor_L: float
    factor_W: float
    note: str = ""


def load_combinations() -> tuple[LoadCombination, ...]:
    """Return governing factored combinations for solar racking (CFE / LRFD-style).

    Minimum set per project PBS:
    - 1.2D + 1.6L
    - 0.9D + 1.6W
    - 1.2D + 1.0W + 1.0L
    """
    return (
        LoadCombination(
            combo_id="LC1",
            expression="1.2D + 1.6L",
            factor_D=1.2,
            factor_L=1.6,
            factor_W=0.0,
            note="Gravity + live (maintenance / equipment)",
        ),
        LoadCombination(
            combo_id="LC2",
            expression="0.9D + 1.6W",
            factor_D=0.9,
            factor_L=0.0,
            factor_W=1.6,
            note="Wind uplift / lateral dominant (NTC-Viento 2020)",
        ),
        LoadCombination(
            combo_id="LC3",
            expression="1.2D + 1.0W + 1.0L",
            factor_D=1.2,
            factor_L=1.0,
            factor_W=1.0,
            note="Combined gravity, wind, and live",
        ),
    )


def load_combination_rows() -> list[dict[str, object]]:
    """Flatten combinations for UI tables."""
    return [
        {
            "ID": combo.combo_id,
            "Combination": combo.expression,
            "D": combo.factor_D,
            "L": combo.factor_L,
            "W": combo.factor_W,
            "Note": combo.note,
        }
        for combo in load_combinations()
    ]
