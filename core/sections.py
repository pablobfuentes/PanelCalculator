"""Steel section properties for structural analysis (Phase 5.1)."""

from __future__ import annotations

from dataclasses import dataclass

STEEL_DENSITY_KG_M3 = 7850.0
IN2_TO_M2 = 0.0254**2
IN4_TO_M4 = 0.0254**4


@dataclass(frozen=True)
class SteelSection:
    """Prismatic steel section for strength and FEA models.

    Units (SI throughout):
    - ``A`` — cross-sectional area (m²)
    - ``Ix`` — strong-axis moment of inertia (m⁴), **not** mm⁴ or cm⁴
    - ``Fy`` — yield strength (MPa)
    - ``outer_depth_m`` — optional outer depth for section modulus estimate (m)
    """

    name: str
    A: float
    Ix: float
    Fy: float
    outer_depth_m: float | None = None

    def __post_init__(self) -> None:
        if self.A <= 0:
            raise ValueError("A must be positive")
        if self.Ix <= 0:
            raise ValueError("Ix must be positive")
        if self.Fy <= 0:
            raise ValueError("Fy must be positive")
        if self.outer_depth_m is not None and self.outer_depth_m <= 0:
            raise ValueError("outer_depth_m must be positive when provided")

    @property
    def mass_per_m(self) -> float:
        """Linear mass from area × steel density (kg/m)."""
        return self.A * STEEL_DENSITY_KG_M3

    @property
    def Sx(self) -> float | None:
        """Elastic section modulus about strong axis (m³), if depth is known."""
        if self.outer_depth_m is None:
            return None
        return 2.0 * self.Ix / self.outer_depth_m


@dataclass(frozen=True)
class BasePlateProfile:
    """Square base plate at column foot."""

    name: str
    area_m2: float
    thickness_m: float
    Fy: float

    def __post_init__(self) -> None:
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be positive")
        if self.thickness_m <= 0:
            raise ValueError("thickness_m must be positive")
        if self.Fy <= 0:
            raise ValueError("Fy must be positive")

    @property
    def mass_kg(self) -> float:
        """Plate mass from area × thickness × steel density."""
        return self.area_m2 * self.thickness_m * STEEL_DENSITY_KG_M3


@dataclass(frozen=True)
class MaterialSections:
    """Catalog of sections used in the racking system."""

    ptr_post: SteelSection
    secondary_beam: SteelSection
    truss_chord: SteelSection
    base_plate: BasePlateProfile


# AISC HSS4X4X1/4 (imperial catalog converted to SI).
# A = 2.21 in², Ix = 4.59 in⁴, Fy = 345 MPa (A500 Gr. B), depth = 4.000 in.
DEFAULT_PTR_4X4 = SteelSection(
    name='PTR 4×4×¼" (HSS4X4X1/4)',
    A=2.21 * IN2_TO_M2,
    Ix=4.59 * IN4_TO_M4,
    Fy=345.0,
    outer_depth_m=4.0 * 0.0254,
)

# AISC HSS3X2X1/4 — typical secondary beam / purlin tube.
DEFAULT_SECONDARY_BEAM = SteelSection(
    name='HSS 3×2×¼" (secondary beam)',
    A=1.53 * IN2_TO_M2,
    Ix=1.53 * IN4_TO_M4,
    Fy=345.0,
    outer_depth_m=3.0 * 0.0254,
)

# AISC L2X2X1/4 — Warren truss chord (angle).
DEFAULT_TRUSS_CHORD = SteelSection(
    name='L 2×2×¼" (truss chord)',
    A=0.719 * IN2_TO_M2,
    Ix=0.321 * IN4_TO_M4,
    Fy=250.0,
    outer_depth_m=2.0 * 0.0254,
)

DEFAULT_BASE_PLATE = BasePlateProfile(
    name="200×200×12 mm base plate",
    area_m2=0.2 * 0.2,
    thickness_m=0.012,
    Fy=250.0,
)


def default_material_sections() -> MaterialSections:
    """Default section catalog from AISC tables (SI units)."""
    return MaterialSections(
        ptr_post=DEFAULT_PTR_4X4,
        secondary_beam=DEFAULT_SECONDARY_BEAM,
        truss_chord=DEFAULT_TRUSS_CHORD,
        base_plate=DEFAULT_BASE_PLATE,
    )


def base_plate_summary_row(role: str, plate: BasePlateProfile) -> dict[str, object]:
    """Flatten a base plate for UI tables."""
    return {
        "Role": role,
        "Section": plate.name,
        "Area (m²)": plate.area_m2,
        "Thickness (m)": plate.thickness_m,
        "Fy (MPa)": plate.Fy,
        "Mass (kg/ea)": plate.mass_kg,
    }


def section_summary_row(role: str, section: SteelSection) -> dict[str, object]:
    """Flatten a section for UI tables."""
    sx = section.Sx
    return {
        "Role": role,
        "Section": section.name,
        "A (m²)": section.A,
        "Ix (m⁴)": section.Ix,
        "Fy (MPa)": section.Fy,
        "Sx (m³)": sx if sx is not None else None,
        "Mass (kg/m)": section.mass_per_m,
    }
