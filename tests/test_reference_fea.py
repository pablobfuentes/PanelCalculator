"""Phase 0 reference beam — FEA vs hand calc within ±2%."""

from core.reference_fea import (
    REFERENCE_TOLERANCE,
    hand_calc_midspan_moment_knm,
    run_reference_beam_analysis,
)


def test_hand_calc_midspan_moment():
    assert hand_calc_midspan_moment_knm(10.0, 5.0) == 12.5


def test_reference_beam_within_two_percent():
    result = run_reference_beam_analysis()
    assert result.hand_moment_knm == 12.5
    assert result.within_tolerance
    assert result.relative_error <= REFERENCE_TOLERANCE
