"""Tests for steel section properties (Phase 5.1)."""

import pytest

from core.sections import (
    DEFAULT_PTR_4X4,
    DEFAULT_TRUSS_CHORD,
    IN4_TO_M4,
    SteelSection,
    default_material_sections,
    section_summary_row,
)


def test_steel_section_rejects_non_positive_area():
    with pytest.raises(ValueError, match="A must be positive"):
        SteelSection(name="bad", A=0.0, Ix=1e-6, Fy=250.0)


def test_ptr_4x4_ix_is_in_m4_not_mm4():
    # 4.59 in⁴ ≈ 1.91e-6 m⁴ — orders of magnitude below 1 mm⁴ (= 1e-12 m⁴) confusion
    assert DEFAULT_PTR_4X4.Ix == pytest.approx(4.59 * IN4_TO_M4)
    assert DEFAULT_PTR_4X4.Ix > 1e-7
    assert DEFAULT_PTR_4X4.Ix < 1e-4


def test_mass_per_m_from_area():
    section = SteelSection(name="test", A=0.001, Ix=1e-6, Fy=250.0)
    assert section.mass_per_m == pytest.approx(7.85)


def test_section_modulus_with_depth():
    section = SteelSection(
        name="test", A=0.001, Ix=1e-6, Fy=250.0, outer_depth_m=0.1
    )
    assert section.Sx == pytest.approx(2e-5)


def test_default_material_sections_has_four_roles():
    materials = default_material_sections()
    assert materials.ptr_post.name
    assert materials.secondary_beam.name
    assert materials.truss_chord.name
    assert materials.base_plate.name
    assert materials.truss_chord.mass_per_m < materials.ptr_post.mass_per_m
    assert materials.base_plate.mass_kg > 0


def test_section_summary_row():
    row = section_summary_row("Post", DEFAULT_PTR_4X4)
    assert row["Role"] == "Post"
    assert row["Ix (m⁴)"] == DEFAULT_PTR_4X4.Ix
