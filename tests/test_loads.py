"""Tests for load combinations (Phase 5.2)."""

from core.loads import load_combination_rows, load_combinations


def test_load_combinations_minimum_set():
    combos = load_combinations()
    expressions = {combo.expression for combo in combos}
    assert "1.2D + 1.6L" in expressions
    assert "0.9D + 1.6W" in expressions
    assert "1.2D + 1.0W + 1.0L" in expressions
    assert len(combos) >= 3


def test_load_combination_factors():
    by_id = {combo.combo_id: combo for combo in load_combinations()}
    assert by_id["LC1"].factor_D == 1.2
    assert by_id["LC1"].factor_L == 1.6
    assert by_id["LC2"].factor_W == 1.6
    assert by_id["LC2"].factor_D == 0.9
    assert by_id["LC3"].factor_L == 1.0
    assert by_id["LC3"].factor_W == 1.0


def test_load_combination_rows_for_ui():
    rows = load_combination_rows()
    assert rows[0]["ID"] == "LC1"
    assert "Combination" in rows[0]
