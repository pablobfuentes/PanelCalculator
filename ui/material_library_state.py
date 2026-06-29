"""Persist material library and role assignments in session state."""

from __future__ import annotations

import streamlit as st

from core.material_library import (
    ELEMENT_ROLES,
    ROLE_LABELS,
    MaterialProfile,
    default_assignments,
    default_library,
    resolve_material_sections,
)
from core.sections import MaterialSections, SteelSection
from ui.session_store import get_persist, init_session_defaults

PERSIST_LIBRARY = "persist_material_library"
PERSIST_ASSIGNMENTS = "persist_material_assignments"

SIDEBAR_ROLE_MAP = {
    "ptr": "column",
    "chord": "truss",
    "beam": "secondary_beam",
}


def init_material_library() -> None:
    """Seed library and assignments on first use."""
    init_session_defaults()
    if PERSIST_LIBRARY not in st.session_state:
        st.session_state[PERSIST_LIBRARY] = [
            profile.to_dict() for profile in default_library()
        ]
    if PERSIST_ASSIGNMENTS not in st.session_state:
        st.session_state[PERSIST_ASSIGNMENTS] = default_assignments()


def get_library() -> list[MaterialProfile]:
    init_material_library()
    return [MaterialProfile.from_dict(item) for item in st.session_state[PERSIST_LIBRARY]]


def set_library(library: list[MaterialProfile]) -> None:
    init_material_library()
    st.session_state[PERSIST_LIBRARY] = [profile.to_dict() for profile in library]


def get_assignments() -> dict[str, str]:
    init_material_library()
    return dict(st.session_state[PERSIST_ASSIGNMENTS])


def set_assignments(assignments: dict[str, str]) -> None:
    init_material_library()
    st.session_state[PERSIST_ASSIGNMENTS] = dict(assignments)


def material_sections_from_library() -> MaterialSections:
    return resolve_material_sections(get_library(), get_assignments())


def _persist_prefix(role_key: str) -> str:
    return f"persist_sec_{role_key}"


def sync_assignments_to_legacy_persist(
    assignments: dict[str, str], library: list[MaterialProfile]
) -> None:
    """Keep sidebar Materials tab widgets aligned with BOM modal selections."""
    by_id = {profile.id: profile for profile in library}
    mapping = {
        "column": "ptr",
        "truss": "chord",
        "secondary_beam": "beam",
    }
    for role, persist_key in mapping.items():
        profile = by_id.get(assignments.get(role, ""))
        if profile is None or profile.kind != "section":
            continue
        prefix = _persist_prefix(persist_key)
        st.session_state[f"{prefix}_a"] = profile.A
        st.session_state[f"{prefix}_ix"] = profile.Ix
        st.session_state[f"{prefix}_fy"] = profile.Fy


def sync_sidebar_edits_to_library() -> None:
    """Push Materials sidebar edits into assigned library profiles."""
    init_material_library()
    library = get_library()
    assignments = get_assignments()
    by_id = {profile.id: profile for profile in library}
    changed = False
    for sidebar_key, role in SIDEBAR_ROLE_MAP.items():
        profile_id = assignments.get(role)
        if not profile_id or profile_id not in by_id:
            continue
        profile = by_id[profile_id]
        if profile.kind != "section":
            continue
        prefix = _persist_prefix(sidebar_key)
        new_a = float(get_persist(f"{prefix}_a"))
        new_ix = float(get_persist(f"{prefix}_ix"))
        new_fy = float(get_persist(f"{prefix}_fy"))
        if (
            profile.A != new_a
            or profile.Ix != new_ix
            or profile.Fy != new_fy
        ):
            profile.A = new_a
            profile.Ix = new_ix
            profile.Fy = new_fy
            changed = True
    if changed:
        set_library(list(by_id.values()))


def assigned_profile_summary(role: str) -> dict[str, object]:
    library = get_library()
    assignments = get_assignments()
    profile = next(
        (item for item in library if item.id == assignments.get(role)),
        None,
    )
    if profile is None:
        return {"Role": ROLE_LABELS.get(role, role), "Profile": "—"}
    row = {"Role": ROLE_LABELS.get(role, role), "Profile": profile.name}
    if profile.kind == "section":
        section = SteelSection(
            name=profile.name,
            A=profile.A,
            Ix=profile.Ix,
            Fy=profile.Fy,
            outer_depth_m=profile.outer_depth_m,
        )
        row["A (m²)"] = section.A
        row["Ix (m⁴)"] = section.Ix
        row["Fy (MPa)"] = section.Fy
        row["Mass"] = f"{section.mass_per_m:.2f} kg/m"
    else:
        row["Area (m²)"] = profile.plate_area_m2
        row["Thickness (m)"] = profile.plate_thickness_m
        row["Fy (MPa)"] = profile.Fy
        mass = profile.plate_area_m2 * profile.plate_thickness_m * 7850.0
        row["Mass"] = f"{mass:.2f} kg/ea"
    return row


def assigned_profiles_table() -> list[dict[str, object]]:
    return [assigned_profile_summary(role) for role in ELEMENT_ROLES]
