"""Tests for material profile library (BOM settings)."""

import pytest

from core.material_library import (
    MaterialProfile,
    default_assignments,
    default_library,
    resolve_material_sections,
    to_steel_section,
)
from core.sections import default_material_sections


def test_default_library_has_four_profiles():
    library = default_library()
    assert len(library) == 4
    kinds = {profile.kind for profile in library}
    assert kinds == {"section", "base_plate"}


def test_default_assignments_reference_library_ids():
    library = default_library()
    assignments = default_assignments()
    ids = {profile.id for profile in library}
    assert set(assignments.values()).issubset(ids)


def test_resolve_material_sections_matches_defaults():
    library = default_library()
    assignments = default_assignments()
    resolved = resolve_material_sections(library, assignments)
    defaults = default_material_sections()
    assert resolved.ptr_post.A == pytest.approx(defaults.ptr_post.A)
    assert resolved.truss_chord.Fy == pytest.approx(defaults.truss_chord.Fy)
    assert resolved.base_plate.mass_kg == pytest.approx(defaults.base_plate.mass_kg)


def test_custom_column_profile_changes_resolved_post():
    library = default_library()
    assignments = default_assignments()
    custom = MaterialProfile(
        id="custom-col",
        name="Custom column",
        kind="section",
        A=0.01,
        Ix=2e-5,
        Fy=300.0,
        outer_depth_m=0.15,
    )
    library.append(custom)
    assignments["column"] = custom.id
    resolved = resolve_material_sections(library, assignments)
    assert resolved.ptr_post.A == pytest.approx(0.01)
    assert to_steel_section(custom).mass_per_m == pytest.approx(78.5)
