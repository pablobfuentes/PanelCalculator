"""Panel type catalog for the web API (no Streamlit dependency)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from core.models import PanelSpec

DEFAULT_COLORS = {
    "A": "#3B7DD8",
    "B": "#3ECF8E",
    "C": "#E74C3C",
    "D": "#9B59B6",
    "E": "#F39C12",
    "F": "#1ABC9C",
}


@dataclass
class PanelTypeDefinition:
    key: str
    name: str
    length: float
    width: float
    weight: float
    watt_peak: float
    color: str
    tilt_angle: float = 10.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PanelTypeDefinition:
        return cls(
            key=str(data["key"]),
            name=str(data["name"]),
            length=float(data["length"]),
            width=float(data["width"]),
            weight=float(data["weight"]),
            watt_peak=float(data.get("watt_peak", 0.0)),
            color=str(data["color"]),
            tilt_angle=float(data.get("tilt_angle", 10.0)),
        )

    def to_panel_spec(self) -> PanelSpec:
        return PanelSpec(
            length=self.length,
            width=self.width,
            weight=self.weight,
            tilt_angle=self.tilt_angle,
        )


def default_catalog() -> list[PanelTypeDefinition]:
    return [
        PanelTypeDefinition(
            key="A",
            name="Panel A",
            length=2.3,
            width=1.2,
            weight=25.0,
            watt_peak=540.0,
            color=DEFAULT_COLORS["A"],
        ),
        PanelTypeDefinition(
            key="B",
            name="Panel B",
            length=2.0,
            width=1.0,
            weight=20.0,
            watt_peak=450.0,
            color=DEFAULT_COLORS["B"],
        ),
    ]


def catalog_by_key() -> dict[str, PanelTypeDefinition]:
    return {panel.key: panel for panel in default_catalog()}
