"""In-memory panel type catalog (A, B, C, …) for the Layout builder."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import streamlit as st

from core.models import PanelSpec
from ui.session_store import get_persist, init_session_defaults

PANEL_KEYS = tuple("ABCDEFGH")
PERSIST_CATALOG = "persist_panel_catalog"
PERSIST_SELECTED = "persist_selected_panel_key"

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


def _default_catalog() -> list[PanelTypeDefinition]:
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
            tilt_angle=10.0,
        ),
    ]


def init_panel_catalog() -> None:
    init_session_defaults()
    if PERSIST_CATALOG not in st.session_state:
        st.session_state[PERSIST_CATALOG] = [
            panel.to_dict() for panel in _default_catalog()
        ]
    if PERSIST_SELECTED not in st.session_state:
        st.session_state[PERSIST_SELECTED] = "A"


def get_panel_catalog() -> list[PanelTypeDefinition]:
    init_panel_catalog()
    return [PanelTypeDefinition.from_dict(item) for item in st.session_state[PERSIST_CATALOG]]


def set_panel_catalog(catalog: list[PanelTypeDefinition]) -> None:
    init_panel_catalog()
    st.session_state[PERSIST_CATALOG] = [panel.to_dict() for panel in catalog]


def get_selected_panel_key() -> str:
    init_panel_catalog()
    return str(st.session_state[PERSIST_SELECTED])


def set_selected_panel_key(key: str) -> None:
    init_panel_catalog()
    st.session_state[PERSIST_SELECTED] = key


def get_selected_panel_type() -> PanelTypeDefinition:
    catalog = get_panel_catalog()
    selected = get_selected_panel_key()
    for panel in catalog:
        if panel.key == selected:
            return panel
    return catalog[0]


def selected_panel_spec() -> PanelSpec:
    return get_selected_panel_type().to_panel_spec()


def sync_selected_to_legacy_persist() -> None:
    """Keep persist_length/width/weight/tilt aligned with selected panel type."""
    panel = get_selected_panel_type()
    st.session_state.persist_length = panel.length
    st.session_state.persist_width = panel.width
    st.session_state.persist_weight = panel.weight
    st.session_state.persist_tilt = panel.tilt_angle


def update_selected_panel(**kwargs: object) -> None:
    catalog = get_panel_catalog()
    selected = get_selected_panel_key()
    updated: list[PanelTypeDefinition] = []
    for panel in catalog:
        if panel.key == selected:
            data = panel.to_dict()
            data.update(kwargs)
            updated.append(PanelTypeDefinition.from_dict(data))
        else:
            updated.append(panel)
    set_panel_catalog(updated)
    sync_selected_to_legacy_persist()


def next_panel_key() -> str | None:
    used = {panel.key for panel in get_panel_catalog()}
    for key in PANEL_KEYS:
        if key not in used:
            return key
    return None


def add_panel_type(
    *,
    name: str,
    length: float,
    width: float,
    weight: float,
    watt_peak: float,
    color: str,
    tilt_angle: float = 10.0,
) -> PanelTypeDefinition:
    key = next_panel_key()
    if key is None:
        raise ValueError("Maximum panel types reached.")
    panel = PanelTypeDefinition(
        key=key,
        name=name.strip() or f"Panel {key}",
        length=length,
        width=width,
        weight=weight,
        watt_peak=watt_peak,
        color=color,
        tilt_angle=tilt_angle,
    )
    catalog = get_panel_catalog()
    catalog.append(panel)
    set_panel_catalog(catalog)
    set_selected_panel_key(key)
    sync_selected_to_legacy_persist()
    return panel
