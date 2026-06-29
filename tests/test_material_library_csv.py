"""Tests for material catalogue CSV import/export."""

import pytest

from core.material_library import MaterialProfile, default_library
from core.material_library_csv import (
    catalogue_template_csv,
    merge_libraries,
    parse_catalogue_csv,
    profiles_to_csv,
)


def test_template_csv_has_header_and_default_rows():
    text = catalogue_template_csv()
    assert "id,name,type" in text.splitlines()[0]
    assert text.count("\n") >= 4


def test_round_trip_default_library():
    library = default_library()
    csv_text = profiles_to_csv(library)
    parsed, errors = parse_catalogue_csv(csv_text)
    assert not errors
    assert len(parsed) == len(library)
    assert parsed[0].name == library[0].name
    assert parsed[0].A == pytest.approx(library[0].A, rel=1e-5)


def test_parse_custom_section_and_base_plate():
    csv_text = """id,name,type,A_m2,Ix_m4,Fy_MPa,outer_depth_m,plate_area_m2,plate_thickness_m
,custom tube,section,0.0015,2e-06,345,0.12,,
,custom plate,base_plate,,,250,,0.04,0.015
"""
    parsed, errors = parse_catalogue_csv(csv_text)
    assert not errors
    assert len(parsed) == 2
    assert parsed[0].kind == "section"
    assert parsed[0].outer_depth_m == pytest.approx(0.12)
    assert parsed[1].kind == "base_plate"
    assert parsed[1].plate_area_m2 == pytest.approx(0.04)


def test_parse_rejects_invalid_section_row():
    csv_text = """id,name,type,A_m2,Ix_m4,Fy_MPa,outer_depth_m,plate_area_m2,plate_thickness_m
,bad,section,,,345,,,
"""
    parsed, errors = parse_catalogue_csv(csv_text)
    assert not parsed
    assert any("A_m2" in message for message in errors)


def test_merge_updates_by_name():
    existing = default_library()
    imported = [
        MaterialProfile(
            id="new-id",
            name=existing[0].name,
            kind="section",
            A=0.01,
            Ix=1e-5,
            Fy=300.0,
        )
    ]
    merged = merge_libraries(existing, imported, mode="merge")
    assert len(merged) == len(existing)
    updated = next(item for item in merged if item.name == existing[0].name)
    assert updated.A == pytest.approx(0.01)


def test_replace_mode_replaces_library():
    existing = default_library()
    imported = [
        MaterialProfile(
            id="only-one",
            name="Solo",
            kind="section",
            A=0.001,
            Ix=1e-6,
            Fy=250.0,
        )
    ]
    merged = merge_libraries(existing, imported, mode="replace")
    assert len(merged) == 1
    assert merged[0].name == "Solo"
