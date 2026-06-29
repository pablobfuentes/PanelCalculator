"""CSV import/export for the material profile library."""

from __future__ import annotations

import csv
import io
from typing import Literal

from core.material_library import MaterialProfile, default_library, new_profile_id

ImportMode = Literal["merge", "replace"]

CSV_FIELDNAMES: tuple[str, ...] = (
    "id",
    "name",
    "type",
    "A_m2",
    "Ix_m4",
    "Fy_MPa",
    "outer_depth_m",
    "plate_area_m2",
    "plate_thickness_m",
)

_SECTION_TYPES = {"section", "steel", "beam", "column", "truss", "tube", "angle"}
_BASE_PLATE_TYPES = {"base_plate", "base plate", "plate", "baseplate"}


def _normalize_type(raw: str) -> str | None:
    value = raw.strip().lower().replace("-", "_")
    if value in _SECTION_TYPES or value == "section":
        return "section"
    if value in _BASE_PLATE_TYPES:
        return "base_plate"
    return None


def _parse_float(raw: str | None) -> float | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    return float(text.replace(",", ""))


def _profile_to_csv_row(profile: MaterialProfile) -> dict[str, str]:
    return {
        "id": profile.id,
        "name": profile.name,
        "type": profile.kind,
        "A_m2": f"{profile.A:.8f}" if profile.kind == "section" else "",
        "Ix_m4": f"{profile.Ix:.8e}" if profile.kind == "section" else "",
        "Fy_MPa": f"{profile.Fy:.0f}",
        "outer_depth_m": (
            f"{profile.outer_depth_m:.6f}"
            if profile.outer_depth_m is not None
            else ""
        ),
        "plate_area_m2": (
            f"{profile.plate_area_m2:.6f}" if profile.kind == "base_plate" else ""
        ),
        "plate_thickness_m": (
            f"{profile.plate_thickness_m:.6f}" if profile.kind == "base_plate" else ""
        ),
    }


def profiles_to_csv(profiles: list[MaterialProfile]) -> str:
    """Serialize profiles to CSV text (UTF-8, no BOM — add BOM in UI for Excel)."""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    for profile in profiles:
        writer.writerow(_profile_to_csv_row(profile))
    return buffer.getvalue()


def catalogue_template_csv() -> str:
    """Example CSV with default catalogue rows for Excel editing."""
    return profiles_to_csv(default_library())


def parse_catalogue_csv(text: str) -> tuple[list[MaterialProfile], list[str]]:
    """Parse CSV text into profiles. Returns (profiles, error messages)."""
    if not text.strip():
        return [], ["CSV file is empty."]

    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        return [], ["CSV has no header row."]

    missing = [column for column in CSV_FIELDNAMES if column not in reader.fieldnames]
    if missing:
        return [], [f"Missing columns: {', '.join(missing)}"]

    profiles: list[MaterialProfile] = []
    errors: list[str] = []
    seen_ids: set[str] = set()
    seen_names: set[str] = set()

    for row_number, row in enumerate(reader, start=2):
        name = (row.get("name") or "").strip()
        if not name:
            continue

        kind_raw = (row.get("type") or "").strip()
        kind = _normalize_type(kind_raw)
        if kind is None:
            errors.append(
                f"Row {row_number}: invalid type {kind_raw!r} "
                "(use section or base_plate)."
            )
            continue

        profile_id = (row.get("id") or "").strip() or new_profile_id()
        if profile_id in seen_ids:
            errors.append(f"Row {row_number}: duplicate id {profile_id!r}.")
            continue
        name_key = name.lower()
        if name_key in seen_names:
            errors.append(f"Row {row_number}: duplicate name {name!r}.")
            continue
        seen_ids.add(profile_id)
        seen_names.add(name_key)

        try:
            fy = _parse_float(row.get("Fy_MPa"))
            if fy is None or fy <= 0:
                raise ValueError("Fy_MPa must be a positive number")

            if kind == "section":
                area = _parse_float(row.get("A_m2"))
                ix = _parse_float(row.get("Ix_m4"))
                if area is None or area <= 0:
                    raise ValueError("A_m2 must be a positive number for sections")
                if ix is None or ix <= 0:
                    raise ValueError("Ix_m4 must be a positive number for sections")
                depth = _parse_float(row.get("outer_depth_m"))
                profiles.append(
                    MaterialProfile(
                        id=profile_id,
                        name=name,
                        kind="section",
                        A=area,
                        Ix=ix,
                        Fy=fy,
                        outer_depth_m=depth if depth and depth > 0 else None,
                    )
                )
            else:
                plate_area = _parse_float(row.get("plate_area_m2"))
                thickness = _parse_float(row.get("plate_thickness_m"))
                if plate_area is None or plate_area <= 0:
                    raise ValueError(
                        "plate_area_m2 must be a positive number for base plates"
                    )
                if thickness is None or thickness <= 0:
                    raise ValueError(
                        "plate_thickness_m must be a positive number for base plates"
                    )
                profiles.append(
                    MaterialProfile(
                        id=profile_id,
                        name=name,
                        kind="base_plate",
                        Fy=fy,
                        plate_area_m2=plate_area,
                        plate_thickness_m=thickness,
                    )
                )
        except ValueError as exc:
            errors.append(f"Row {row_number} ({name}): {exc}")

    if not profiles and not errors:
        return [], ["No data rows found below the header."]

    return profiles, errors


def merge_libraries(
    existing: list[MaterialProfile],
    imported: list[MaterialProfile],
    *,
    mode: ImportMode,
) -> list[MaterialProfile]:
    """Combine catalogues by merge (update by id/name) or full replace."""
    if mode == "replace":
        return list(imported)

    by_id = {profile.id: profile for profile in existing}
    by_name = {profile.name.lower(): profile for profile in existing}
    merged = list(existing)

    for profile in imported:
        if profile.id in by_id:
            by_id[profile.id] = profile
            merged = [by_id[p.id] if p.id == profile.id else p for p in merged]
            by_name[profile.name.lower()] = profile
            continue
        existing_by_name = by_name.get(profile.name.lower())
        if existing_by_name is not None:
            idx = next(i for i, p in enumerate(merged) if p.id == existing_by_name.id)
            merged[idx] = profile
            by_id.pop(existing_by_name.id, None)
            by_id[profile.id] = profile
            by_name[profile.name.lower()] = profile
            continue
        merged.append(profile)
        by_id[profile.id] = profile
        by_name[profile.name.lower()] = profile

    return merged
