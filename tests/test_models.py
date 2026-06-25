"""Tests for core data models."""

import pytest

from core.models import (
    DEFAULT_MID_CLAMP_GAP_M,
    INCH_TO_M,
    LayoutConfig,
    PanelSpec,
    WindConfig,
    WIND_EXPOSURE_CATEGORIES,
)


def test_panel_spec_valid():
    panel = PanelSpec(length=2.0, width=1.0, weight=25.0, tilt_angle=15.0)
    assert panel.length == 2.0
    assert panel.width == 1.0
    assert panel.weight == 25.0
    assert panel.tilt_angle == 15.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"length": 0, "width": 1.0, "weight": 25.0, "tilt_angle": 15.0},
        {"length": 2.0, "width": -1.0, "weight": 25.0, "tilt_angle": 15.0},
        {"length": 2.0, "width": 1.0, "weight": 0, "tilt_angle": 15.0},
        {"length": 2.0, "width": 1.0, "weight": 25.0, "tilt_angle": 91.0},
    ],
)
def test_panel_spec_rejects_invalid_values(kwargs):
    with pytest.raises(ValueError):
        PanelSpec(**kwargs)


def test_layout_config_defaults():
    config = LayoutConfig()
    assert config.mid_clamp_gap == DEFAULT_MID_CLAMP_GAP_M
    assert config.mid_clamp_gap == INCH_TO_M
    assert config.alley_width == 1.0
    assert config.alley_reach == 2
    assert config.max_area_x == 50.0
    assert config.max_area_y == 50.0


def test_layout_config_custom():
    config = LayoutConfig(
        mid_clamp_gap=0.05,
        alley_width=1.2,
        alley_reach=3,
        max_area_x=30.0,
        max_area_y=40.0,
    )
    assert config.mid_clamp_gap == 0.05
    assert config.alley_reach == 3
    assert config.max_area_x == 30.0


def test_layout_config_rejects_invalid_max_area():
    with pytest.raises(ValueError):
        LayoutConfig(max_area_x=0)


def test_layout_config_rejects_invalid_alley_reach():
    with pytest.raises(ValueError):
        LayoutConfig(alley_reach=1)


def test_wind_config_defaults():
    wind = WindConfig()
    assert wind.wind_speed_kmh == 120.0
    assert wind.exposure_category == "B"


def test_wind_config_custom():
    wind = WindConfig(wind_speed_kmh=150.0, exposure_category="D")
    assert wind.wind_speed_kmh == 150.0
    assert wind.exposure_category == "D"


@pytest.mark.parametrize("category", ["A", "B", "C", "D"])
def test_wind_config_accepts_exposure_categories(category: str):
    wind = WindConfig(exposure_category=category)
    assert wind.exposure_category == category


def test_wind_config_rejects_invalid_exposure():
    with pytest.raises(ValueError):
        WindConfig(exposure_category="E")


def test_wind_config_rejects_non_positive_speed():
    with pytest.raises(ValueError):
        WindConfig(wind_speed_kmh=0.0)
