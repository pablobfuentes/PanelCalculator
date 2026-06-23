"""Panel Calculator data models."""

from dataclasses import dataclass

INCH_TO_M = 0.0254
DEFAULT_MID_CLAMP_GAP_M = INCH_TO_M  # 1"


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
