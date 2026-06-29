"""SVG mini-diagrams for HUD hover tooltips."""

from __future__ import annotations


def _svg_wrap(body: str, *, width: int = 120, height: int = 80) -> str:
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg">{body}</svg>'
    )


def gap_tooltip_svg(gap_in: float) -> str:
    gap_px = max(3, min(20, gap_in * 6))
    x0 = 50 - gap_px / 2
    return _svg_wrap(
        f'<rect fill="#1E2640" width="120" height="80"/>'
        f'<rect fill="#3B7DD8" x="10" y="15" width="40" height="50"/>'
        f'<rect fill="#3B7DD8" x="70" y="15" width="40" height="50"/>'
        f'<rect fill="rgba(255,193,7,0.85)" x="{x0:.1f}" y="15" width="{gap_px:.1f}" height="50"/>'
        f'<line stroke="#F5A623" x1="{x0:.1f}" y1="8" x2="{x0 + gap_px:.1f}" y2="8"/>'
        f'<text fill="#F5A623" font-size="9" text-anchor="middle" x="60" y="7">{gap_in:g}"</text>'
    )


def reach_tooltip_svg(reach: int) -> str:
    pw, aw = 10, 8
    total = reach * 2
    total_w = total * pw + aw
    start = (120 - total_w) / 2
    panels = ""
    for i in range(total):
        px = start + i * pw + (aw if i >= reach else 0)
        opacity = "0.9" if i < reach else "0.45"
        panels += f'<rect fill="rgba(59,125,216,{opacity})" x="{px + 1:.0f}" y="15" width="{pw - 2}" height="50"/>'
    alley_x = start + reach * pw
    return _svg_wrap(
        f'<rect fill="#1E2640" width="120" height="80"/>'
        f'<rect fill="rgba(91,184,245,0.12)" x="{start:.0f}" y="10" width="{total_w:.0f}" height="60"/>'
        f"{panels}"
        f'<rect fill="rgba(245,163,35,0.65)" x="{alley_x:.0f}" y="15" width="{aw}" height="50"/>'
        f'<line stroke="#5BB8F5" x1="{start:.0f}" y1="8" x2="{alley_x:.0f}" y2="8"/>'
        f'<text fill="#5BB8F5" font-size="8" text-anchor="middle" x="{(start + alley_x) / 2:.0f}" y="7">≤{reach}</text>'
    )


def alley_width_tooltip_svg(alley_w: float) -> str:
    aw = max(6, min(30, alley_w * 20))
    return _svg_wrap(
        f'<rect fill="#1E2640" width="120" height="80"/>'
        f'<rect fill="#3B7DD8" x="10" y="15" width="35" height="50"/>'
        f'<rect fill="#3B7DD8" x="75" y="15" width="35" height="50"/>'
        f'<rect fill="rgba(245,163,35,0.65)" x="45" y="15" width="{aw:.0f}" height="50"/>'
        f'<line stroke="#F5A623" x1="45" y1="8" x2="{45 + aw:.0f}" y2="8"/>'
        f'<text fill="#F5A623" font-size="9" text-anchor="middle" x="{45 + aw / 2:.0f}" y="7">{alley_w:g}m</text>'
    )


def spine_tooltip_svg(spine_edge: str) -> str:
    sy = 10 if spine_edge == "top" else 68
    return _svg_wrap(
        f'<rect fill="#1E2640" width="120" height="80"/>'
        f'<rect fill="#3B7DD8" x="10" y="20" width="30" height="35"/>'
        f'<rect fill="#3B7DD8" x="45" y="20" width="30" height="35"/>'
        f'<rect fill="#3B7DD8" x="80" y="20" width="30" height="35"/>'
        f'<rect fill="rgba(245,163,35,0.65)" x="10" y="{sy}" width="100" height="8"/>'
        f'<text fill="#F5A623" font-size="7" text-anchor="middle" x="60" y="{sy + 6}">SPINE</text>'
    )


def hud_tooltip_block(label: str, svg: str, description: str, *, accent: bool = False) -> str:
    accent_cls = " amber" if accent else ""
    return f"""
    <div class="sf-hud-var">
      <div class="sf-hud-label{accent_cls}">{label}</div>
      <div class="sf-hud-tooltip">
        {svg}
        <div class="sf-hud-tooltip-label">{description}</div>
      </div>
    </div>
    """
