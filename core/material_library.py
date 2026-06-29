"""Material profile library and role assignments for BOM / FEA."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal
from uuid import uuid4

from core.sections import (
    BasePlateProfile,
    MaterialSections,
    SteelSection,
    default_material_sections,
)

ProfileKind = Literal["section", "base_plate"]
ElementRole = Literal["column", "truss", "secondary_beam", "base_plate"]

ELEMENT_ROLES: tuple[ElementRole, ...] = (
    "column",
    "truss",
    "secondary_beam",
    "base_plate",
)

ROLE_LABELS: dict[ElementRole, str] = {
    "column": "Columns",
    "truss": "Beams / trusses",
    "secondary_beam": "Secondary beams",
    "base_plate": "Base plate",
}

DEFAULT_LIBRARY_IDS = {
    "column": "default-column",
    "truss": "default-truss",
    "secondary_beam": "default-secondary",
    "base_plate": "default-base-plate",
}


@dataclass
class MaterialProfile:
    """Serializable profile stored in the in-memory library."""

    id: str
    name: str
    kind: ProfileKind
    A: float = 0.0
    Ix: float = 0.0
    Fy: float = 0.0
    outer_depth_m: float | None = None
    plate_area_m2: float = 0.0
    plate_thickness_m: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "A": self.A,
            "Ix": self.Ix,
            "Fy": self.Fy,
            "outer_depth_m": self.outer_depth_m,
            "plate_area_m2": self.plate_area_m2,
            "plate_thickness_m": self.plate_thickness_m,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MaterialProfile:
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            kind=data["kind"],  # type: ignore[arg-type]
            A=float(data.get("A", 0.0)),
            Ix=float(data.get("Ix", 0.0)),
            Fy=float(data.get("Fy", 0.0)),
            outer_depth_m=(
                float(data["outer_depth_m"])
                if data.get("outer_depth_m") is not None
                else None
            ),
            plate_area_m2=float(data.get("plate_area_m2", 0.0)),
            plate_thickness_m=float(data.get("plate_thickness_m", 0.0)),
        )


def profile_from_steel_section(section: SteelSection, profile_id: str) -> MaterialProfile:
    return MaterialProfile(
        id=profile_id,
        name=section.name,
        kind="section",
        A=section.A,
        Ix=section.Ix,
        Fy=section.Fy,
        outer_depth_m=section.outer_depth_m,
    )


def profile_from_base_plate(plate: BasePlateProfile, profile_id: str) -> MaterialProfile:
    return MaterialProfile(
        id=profile_id,
        name=plate.name,
        kind="base_plate",
        Fy=plate.Fy,
        plate_area_m2=plate.area_m2,
        plate_thickness_m=plate.thickness_m,
    )


def to_steel_section(profile: MaterialProfile) -> SteelSection:
    if profile.kind != "section":
        raise ValueError(f"Profile {profile.id!r} is not a steel section")
    return SteelSection(
        name=profile.name,
        A=profile.A,
        Ix=profile.Ix,
        Fy=profile.Fy,
        outer_depth_m=profile.outer_depth_m,
    )


def to_base_plate(profile: MaterialProfile) -> BasePlateProfile:
    if profile.kind != "base_plate":
        raise ValueError(f"Profile {profile.id!r} is not a base plate")
    return BasePlateProfile(
        name=profile.name,
        area_m2=profile.plate_area_m2,
        thickness_m=profile.plate_thickness_m,
        Fy=profile.Fy,
    )


def default_library() -> list[MaterialProfile]:
    defaults = default_material_sections()
    return [
        profile_from_steel_section(defaults.ptr_post, DEFAULT_LIBRARY_IDS["column"]),
        profile_from_steel_section(defaults.truss_chord, DEFAULT_LIBRARY_IDS["truss"]),
        profile_from_steel_section(
            defaults.secondary_beam, DEFAULT_LIBRARY_IDS["secondary_beam"]
        ),
        profile_from_base_plate(defaults.base_plate, DEFAULT_LIBRARY_IDS["base_plate"]),
    ]


def default_assignments() -> dict[str, str]:
    return dict(DEFAULT_LIBRARY_IDS)


def profiles_for_role(
    library: list[MaterialProfile], role: ElementRole
) -> list[MaterialProfile]:
    if role == "base_plate":
        return [profile for profile in library if profile.kind == "base_plate"]
    return [profile for profile in library if profile.kind == "section"]


def find_profile(library: list[MaterialProfile], profile_id: str) -> MaterialProfile | None:
    for profile in library:
        if profile.id == profile_id:
            return profile
    return None


def resolve_material_sections(
    library: list[MaterialProfile],
    assignments: dict[str, str],
) -> MaterialSections:
    """Build active catalog from library role assignments."""
    column = find_profile(library, assignments["column"])
    truss = find_profile(library, assignments["truss"])
    secondary = find_profile(library, assignments["secondary_beam"])
    base = find_profile(library, assignments["base_plate"])
    if column is None or truss is None or secondary is None or base is None:
        return default_material_sections()
    return MaterialSections(
        ptr_post=to_steel_section(column),
        truss_chord=to_steel_section(truss),
        secondary_beam=to_steel_section(secondary),
        base_plate=to_base_plate(base),
    )


def library_table_row(profile: MaterialProfile) -> dict[str, object]:
    if profile.kind == "base_plate":
        plate = to_base_plate(profile)
        return {
            "Name": profile.name,
            "Type": "Base plate",
            "A (m²)": "—",
            "Ix (m⁴)": "—",
            "Fy (MPa)": f"{profile.Fy:.0f}",
            "Depth (m)": "—",
            "Plate area (m²)": f"{plate.area_m2:.4f}",
            "Thickness (m)": f"{plate.thickness_m:.4f}",
            "Mass": f"{plate.mass_kg:.2f} kg/ea",
        }
    section = to_steel_section(profile)
    depth = (
        f"{profile.outer_depth_m:.4f}"
        if profile.outer_depth_m is not None
        else "—"
    )
    return {
        "Name": profile.name,
        "Type": "Section",
        "A (m²)": f"{profile.A:.6f}",
        "Ix (m⁴)": f"{profile.Ix:.3e}",
        "Fy (MPa)": f"{profile.Fy:.0f}",
        "Depth (m)": depth,
        "Plate area (m²)": "—",
        "Thickness (m)": "—",
        "Mass": f"{section.mass_per_m:.2f} kg/m",
    }


def new_profile_id() -> str:
    return f"user-{uuid4().hex[:8]}"
