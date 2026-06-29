"""Streamlit UI for material catalogue CSV import/export."""

from __future__ import annotations

import streamlit as st

from core.material_library import ELEMENT_ROLES, find_profile, profiles_for_role
from core.material_library_csv import (
    ImportMode,
    catalogue_template_csv,
    merge_libraries,
    parse_catalogue_csv,
    profiles_to_csv,
)
from ui.material_library_state import (
    get_assignments,
    get_library,
    set_assignments,
    set_library,
    sync_assignments_to_legacy_persist,
)


def _csv_download_bytes(text: str) -> bytes:
    """UTF-8 with BOM so Excel opens accents and decimals correctly."""
    return ("\ufeff" + text).encode("utf-8")


def reconcile_assignments(
    library: list,
    assignments: dict[str, str],
) -> dict[str, str]:
    """Keep valid assignments; pick first compatible profile per role if missing."""
    updated = dict(assignments)
    for role in ELEMENT_ROLES:
        profile_id = updated.get(role)
        if profile_id and find_profile(library, profile_id):
            continue
        options = profiles_for_role(library, role)
        if options:
            updated[role] = options[0].id
    return updated


def render_catalogue_import_export(*, key_prefix: str = "catalogue") -> None:
    """Download template, export library, and import CSV."""
    library = get_library()

    st.markdown("**Import / export catalogue**")
    st.caption(
        "Download a CSV template, edit in Excel, then import. "
        "Units: A (m²), Ix (m⁴), Fy (MPa), depths/areas in metres."
    )

    dl_col, export_col = st.columns(2)
    with dl_col:
        st.download_button(
            "Download template (CSV)",
            data=_csv_download_bytes(catalogue_template_csv()),
            file_name="section_catalogue_template.csv",
            mime="text/csv",
            key=f"{key_prefix}_download_template",
            width="stretch",
        )
    with export_col:
        st.download_button(
            "Export current library (CSV)",
            data=_csv_download_bytes(profiles_to_csv(library)),
            file_name="section_catalogue.csv",
            mime="text/csv",
            key=f"{key_prefix}_export_library",
            width="stretch",
        )

    import_mode: ImportMode = st.radio(
        "Import mode",
        options=["merge", "replace"],
        format_func=lambda value: (
            "Merge — add new rows and update matching id/name"
            if value == "merge"
            else "Replace — use imported rows as the full library"
        ),
        horizontal=True,
        key=f"{key_prefix}_import_mode",
    )

    uploaded = st.file_uploader(
        "Import catalogue (CSV)",
        type=["csv"],
        key=f"{key_prefix}_upload",
    )
    if uploaded is not None:
        raw = uploaded.getvalue().decode("utf-8-sig")
        imported, errors = parse_catalogue_csv(raw)
        if errors:
            for message in errors:
                st.error(message)
        if imported:
            merged = merge_libraries(library, imported, mode=import_mode)
            set_library(merged)
            assignments = reconcile_assignments(merged, get_assignments())
            set_assignments(assignments)
            sync_assignments_to_legacy_persist(assignments, merged)
            st.success(
                f"Imported {len(imported)} profile(s) — library now has "
                f"{len(merged)} entr{'y' if len(merged) == 1 else 'ies'}."
            )
            st.rerun()
