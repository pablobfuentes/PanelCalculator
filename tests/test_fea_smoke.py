"""Smoke test: single simply-supported beam via PyNite."""

from Pynite import FEModel3D


def test_single_beam_midspan_point_load():
  """5 m beam, 10 kN midspan load — M_max = P*L/4."""
  length_m = 5.0
  load_kn = 10.0
  expected_moment_knm = load_kn * length_m / 4

  model = FEModel3D()
  model.add_node("N1", 0, 0, 0)
  model.add_node("N2", length_m, 0, 0)
  model.add_material("Steel", 200e3, 77, 0.3, 0)  # E MPa, G MPa, nu, rho
  model.add_section("SEC", 0.01, 8e-5, 8e-5, 4e-5)  # A, Iy, Iz, J m^4
  model.add_member("M1", "N1", "N2", "Steel", "SEC")
  model.def_support("N1", True, True, True, True, False, False)
  model.def_support("N2", False, True, True, True, False, False)
  model.add_member_pt_load("M1", "Fy", -load_kn, length_m / 2, "D")
  model.add_load_combo("LC1", {"D": 1.0})
  model.analyze(check_stability=True)

  moment = model.members["M1"].min_moment("Mz", "LC1")
  assert abs(moment + expected_moment_knm) < 0.01
