"""Phase 0 reference beam — FEA vs hand calculation."""

from __future__ import annotations

from dataclasses import dataclass

from Pynite import FEModel3D

from core.fea import STEEL_E_MPA, STEEL_G_MPA, STEEL_NU

REFERENCE_BEAM_LENGTH_M = 5.0
REFERENCE_BEAM_LOAD_KN = 10.0
REFERENCE_SECTION_A_M2 = 0.01
REFERENCE_SECTION_I_M4 = 8e-5
REFERENCE_TOLERANCE = 0.02


@dataclass(frozen=True)
class ReferenceBeamResult:
    """Comparison of solver moment to hand calculation."""

    length_m: float
    load_kn: float
    hand_moment_knm: float
    fea_moment_knm: float
    relative_error: float

    @property
    def within_tolerance(self) -> bool:
        return self.relative_error <= REFERENCE_TOLERANCE


def hand_calc_midspan_moment_knm(load_kn: float, span_m: float) -> float:
    """Simply supported beam, midspan point load: M_max = P·L / 4."""
    return load_kn * span_m / 4.0


def run_reference_beam_analysis(
    *,
    length_m: float = REFERENCE_BEAM_LENGTH_M,
    load_kn: float = REFERENCE_BEAM_LOAD_KN,
) -> ReferenceBeamResult:
    """Solve the Phase 0 simply-supported beam reference case in PyNite."""
    hand_moment = hand_calc_midspan_moment_knm(load_kn, length_m)

    model = FEModel3D()
    model.add_node("N1", 0, 0, 0)
    model.add_node("N2", length_m, 0, 0)
    model.add_material("Steel", STEEL_E_MPA, STEEL_G_MPA, STEEL_NU, 0.0)
    model.add_section("SEC", REFERENCE_SECTION_A_M2, REFERENCE_SECTION_I_M4, REFERENCE_SECTION_I_M4, REFERENCE_SECTION_I_M4 / 2)
    model.add_member("M1", "N1", "N2", "Steel", "SEC")
    model.def_support("N1", True, True, True, True, False, False)
    model.def_support("N2", False, True, True, True, False, False)
    model.add_member_pt_load("M1", "Fy", -load_kn, length_m / 2, "D")
    model.add_load_combo("LC1", {"D": 1.0})
    model.analyze(check_stability=True)

    fea_moment = abs(model.members["M1"].min_moment("Mz", "LC1"))
    if hand_moment == 0:
        relative_error = 0.0 if fea_moment == 0 else float("inf")
    else:
        relative_error = abs(fea_moment - hand_moment) / hand_moment

    return ReferenceBeamResult(
        length_m=length_m,
        load_kn=load_kn,
        hand_moment_knm=hand_moment,
        fea_moment_knm=fea_moment,
        relative_error=relative_error,
    )
