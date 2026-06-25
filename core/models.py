"""Panel Calculator data models."""

from dataclasses import dataclass

from core.wind import WIND_EXPOSURE_CATEGORIES

INCH_TO_M = 0.0254
DEFAULT_MID_CLAMP_GAP_M = INCH_TO_M  # 1"

DEFAULT_WIND_SPEED_KMH = 120.0
DEFAULT_WIND_EXPOSURE = "B"


@dataclass
class PanelSpec:
    """Single solar panel geometry and weight."""

    length: float  # m, long edge along row
    width: float  # m, short edge across row depth
    weight: float  # kg
    tilt_angle: float  # degrees from horizontal

    def __post_init__(self) -> None:
        if self.length <= 0:
            raise ValueError("length must be positive")
        if self.width <= 0:
            raise ValueError("width must be positive")
        if self.weight <= 0:
            raise ValueError("weight must be positive")
        if not 0 <= self.tilt_angle <= 90:
            raise ValueError("tilt_angle must be between 0 and 90 degrees")


@dataclass
class LayoutConfig:
    """Layout constraints for panel pairs, alleys, and max footprint."""

    mid_clamp_gap: float = DEFAULT_MID_CLAMP_GAP_M  # m, gap between paired panels
    alley_width: float = 1.0  # m, service alley width
    alley_reach: int = 2  # panels reachable on each side of a parallel alley
    max_area_x: float = 50.0  # m, max layout width
    max_area_y: float = 50.0  # m, max layout depth

    def __post_init__(self) -> None:
        if self.mid_clamp_gap < 0:
            raise ValueError("mid_clamp_gap must be non-negative")
        if self.alley_width <= 0:
            raise ValueError("alley_width must be positive")
        if self.alley_reach < 2 or self.alley_reach > 4:
            raise ValueError("alley_reach must be between 2 and 4 panels")
        if self.max_area_x <= 0:
            raise ValueError("max_area_x must be positive")
        if self.max_area_y <= 0:
            raise ValueError("max_area_y must be positive")


@dataclass
class WindConfig:
    """Wind load inputs per CFE NTC-Viento 2020 (basic service wind speed)."""

    wind_speed_kmh: float = DEFAULT_WIND_SPEED_KMH
    exposure_category: str = DEFAULT_WIND_EXPOSURE

    def __post_init__(self) -> None:
        if self.wind_speed_kmh <= 0:
            raise ValueError("wind_speed_kmh must be positive")
        if self.exposure_category not in WIND_EXPOSURE_CATEGORIES:
            raise ValueError(
                f"exposure_category must be one of {WIND_EXPOSURE_CATEGORIES}"
            )
