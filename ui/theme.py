"""SolarForge game UI theme — dark/light visual shell for Streamlit."""

from __future__ import annotations

import streamlit as st

THEME_DARK = "dark"
THEME_LIGHT = "light"


def is_dark_theme() -> bool:
    """Return True when the dark color scheme is active."""
    return st.session_state.get("sf_color_theme", THEME_DARK) != THEME_LIGHT

GOOGLE_FONTS = (
    "https://fonts.googleapis.com/css2?"
    "family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap"
)

GAME_CSS = """
<style>
@import url('GOOGLE_FONTS_PLACEHOLDER');

/* =============================================================================
   THEME MAP — ui/theme.py
   Each block below names the UI surface it styles (Setup tab unless noted).
   =============================================================================
   1.  Design tokens (:root)
   2.  Global app shell (background, sidebar, Streamlit chrome)
   3.  Main top bar — stepper row + theme toggle (block-container)
   4.  Top stepper — Setup / Layout / Structure / Materials / Results
   5.  Setup stage layout — full-width canvas + hidden sidebar
   6.  Layout canvas — Plotly panel grid board (center column)
   7.  Canvas dimension pills — ↔ max width, ↕ max height
   8.  Bottom HUD tooltips — info (i) hover diagrams
   9.  Panel type selector — A / B / + colored squares
  10.  Panel count lock button — legacy fallback
  11.  Nav stepper buttons — clickable step fallback
  12.  Game content shell — Structure / Materials / Results tabs
  13.  Setup left rail — outer card container (224px column)
  14.  Auto-fit to max area — checkbox + pairs/rows inputs
  15.  Left-rail shared — section wrappers + section labels
  16.  Total panels — count box + lock overlay
  17.  Selected panel — stats card (length, width, weight, Wp)
  18.  Footprint — panels + alleys dimensions
  19.  Bottom HUD bar — fixed control strip
  20.  HUD Gap / Alley reach / Alley W — stepper controls
  21.  HUD Spine edge — TOP/BOTTOM toggle
  22.  HUD NEXT — proceed button
  23.  Game shell metrics — stMetric styling (non-Setup tabs)
   24.  Left-rail expanders — compact panels
   ============================================================================= */

/* ── 1. Design tokens ── */
:root {
  --bg: #0D1117;
  --surface: #161B27;
  --surface2: #1E2640;
  --border: rgba(255,255,255,0.07);
  --border2: rgba(255,255,255,0.13);
  --amber: #F5A623;
  --amber-dim: rgba(245,163,35,0.15);
  --amber-glow: rgba(245,163,35,0.35);
  --sky: #5BB8F5;
  --green: #3ECF8E;
  --text: #E8EAF0;
  --text-dim: #7A8499;
  --radius: 10px;
  --radius-lg: 16px;
  --font-game: 'Rajdhani', sans-serif;
  --font-body: 'Inter', sans-serif;
  --shadow-lg: 0 4px 32px rgba(0,0,0,0.5);
  --shadow-md: 0 4px 28px rgba(0,0,0,0.45);
  --shadow-sm: 0 4px 16px rgba(0,0,0,0.35);
  --shadow-hud: 0 8px 48px rgba(0,0,0,0.6);
  --canvas-bg: #0A0E18;
  --canvas-grid: rgba(255,255,255,0.02);
  --canvas-glow: rgba(91,184,245,0.04);
  --hud-hover: rgba(30,38,64,0.55);
}

/* ── 2. Global app shell — page background, sidebar, Streamlit chrome ── */
.stApp {
  background: var(--bg) !important;
  font-family: var(--font-body);
}

.block-container {
  padding-top: 1rem !important;
  max-width: 100% !important;
}

header[data-testid="stHeader"] {
  background: transparent !important;
}

#MainMenu, footer, [data-testid="stToolbar"] {
  visibility: hidden;
}

[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
  font-family: var(--font-game) !important;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-size: 0.85rem !important;
  color: var(--text-dim) !important;
}

/* ── 3. Main top bar — stepper centered, theme toggle right (block-container) ── */
.sf-main-root { display: none !important; }
div[data-testid="stVerticalBlock"]:has(.sf-main-root) > div[data-testid="stHorizontalBlock"] {
  align-items: center !important;
  margin-bottom: 0.35rem !important;
}
div[data-testid="stVerticalBlock"]:has(.sf-main-root) > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child {
  display: flex !important;
  justify-content: flex-end !important;
  align-items: center !important;
}
div[data-testid="stVerticalBlock"]:has(.sf-main-root) > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child button {
  white-space: nowrap !important;
}

/* ── 4. Top stepper — Setup / Layout / Structure / Materials / Results ── */
.sf-stepper-wrap {
  display: flex;
  justify-content: center;
  margin: 0.5rem 0 1rem;
}
.sf-stepper {
  display: inline-flex;
  align-items: center;
  background: var(--surface);
  border: 1px solid var(--border2);
  border-top: none;
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  padding: 0.35rem 0.75rem 0.6rem;
  box-shadow: var(--shadow-lg), 0 0 0 1px rgba(245,163,35,0.12);
  gap: 0;
}
.sf-step {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.85rem;
  font-family: var(--font-game);
  font-weight: 600;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-dim);
}
.sf-step.active {
  color: var(--amber) !important;
}
.sf-step.done {
  color: var(--green) !important;
}
.sf-step.locked { opacity: 0.45; }
.sf-step-icon {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  border: 1.5px solid currentColor;
  flex-shrink: 0;
}
.sf-step.active .sf-step-icon {
  background: var(--amber) !important;
  border-color: var(--amber) !important;
  color: #000 !important;
  box-shadow: 0 0 12px var(--amber-glow), 0 0 24px rgba(245,163,35,0.25) !important;
}
.sf-step.done .sf-step-icon {
  background: var(--green) !important;
  border-color: var(--green) !important;
  color: #000 !important;
  box-shadow: 0 0 8px rgba(62,207,142,0.35) !important;
}
.sf-step-connector {
  width: 24px;
  height: 2px;
  background: var(--border2);
  flex-shrink: 0;
  position: relative;
}
.sf-step-connector-done {
  background: var(--green);
}

/* ── 5. Setup stage layout — full-width main area, compact stepper, room for HUD ── */
.stApp:has(.sf-layout-view) [data-testid="stSidebar"] {
  display: none !important;
}
.stApp:has(.sf-layout-view) [data-testid="stMain"] {
  margin-left: 0 !important;
}
.stApp:has(.sf-layout-view) .block-container {
  padding: 0.35rem 0.65rem 0 !important;
  max-width: 100% !important;
}
.stApp:has(.sf-layout-view) .sf-stepper-wrap {
  margin: 0 0 0.45rem !important;
  display: flex !important;
  justify-content: center !important;
}
.stApp:has(.sf-layout-view) .sf-stepper {
  padding: 0.3rem 0.65rem 0.5rem !important;
  border-top: none !important;
  box-shadow: var(--shadow-lg), 0 0 0 1px rgba(245,163,35,0.15) !important;
}
.stApp:has(.sf-layout-view) .sf-step.active {
  color: var(--amber) !important;
}
.stApp:has(.sf-layout-view) .sf-step.active .sf-step-icon {
  background: var(--amber) !important;
  border-color: var(--amber) !important;
  color: #000 !important;
  box-shadow: 0 0 12px var(--amber-glow), 0 0 22px rgba(245,163,35,0.3) !important;
}
.stApp:has(.sf-layout-view) .sf-step.done {
  color: var(--green) !important;
}
.stApp:has(.sf-layout-view) .sf-step.done .sf-step-icon {
  background: var(--green) !important;
  border-color: var(--green) !important;
  color: #000 !important;
}
.stApp:has(.sf-layout-view) .block-container {
  padding-bottom: 6.5rem !important;
}
.stApp:has(.sf-layout-view) div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
  gap: 0.35rem !important;
}

/* ── 6. Layout canvas — Plotly panel grid board (center column) ── */
div[data-testid="stColumn"]:has(.sf-canvas-col-root) {
  position: relative !important;
  min-width: 0 !important;
  overflow: visible !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) [data-testid="stPlotlyChart"] {
  background: var(--canvas-bg) !important;
  background-image:
    radial-gradient(circle at 50% 50%, var(--canvas-glow) 0%, transparent 70%),
    linear-gradient(var(--canvas-grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--canvas-grid) 1px, transparent 1px);
  background-size: 100% 100%, 40px 40px, 40px 40px;
  border: 1px solid var(--border2);
  border-radius: var(--radius-lg);
  padding: 2.25rem 3.25rem 0.5rem 0.5rem;
  box-shadow: inset 0 0 80px var(--canvas-glow), var(--shadow-md);
  overflow: visible !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) [data-testid="stPlotlyChart"] .main-svg {
  background: transparent !important;
}

/* ── 7. Canvas dimension pills — aligned to max-area dotted box on the plot ── */
.sf-dim-overlay-root { display: none !important; }
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:has(.sf-canvas-col-root) {
  height: 0 !important;
  min-height: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
  overflow: visible !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] {
  position: relative !important;
  overflow: visible !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:has(.sf-dim-overlay-root) {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: var(--sf-canvas-plot-h, 572px) !important;
  z-index: 8 !important;
  pointer-events: none !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: visible !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:has(.sf-dim-overlay-root)
  + div[data-testid="stElementContainer"] {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: var(--sf-canvas-plot-h, 572px) !important;
  z-index: 9 !important;
  pointer-events: none !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: visible !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:has([data-testid="stPlotlyChart"]) {
  position: relative !important;
  z-index: 1 !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h) {
  position: static !important;
  display: block !important;
  width: 100% !important;
  height: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h) > div[data-testid="stColumn"] {
  position: absolute !important;
  width: auto !important;
  flex: none !important;
  pointer-events: none !important;
  padding: 0 !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h) > div[data-testid="stColumn"]:has(.sf-dim-w) {
  left: var(--dim-w-left, 50%) !important;
  top: var(--dim-w-top, 12%) !important;
  transform: translate(-50%, calc(-100% - 6px)) !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h) > div[data-testid="stColumn"]:has(.sf-dim-h) {
  left: var(--dim-h-left, 82%) !important;
  top: var(--dim-h-top, 50%) !important;
  transform: translate(6px, -50%) !important;
}
/* Dimension pill chrome — arrow, value input, unit label inside each bubble */
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-w) div[data-testid="stHorizontalBlock"],
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-h) div[data-testid="stHorizontalBlock"] {
  display: inline-flex !important;
  align-items: center !important;
  gap: 0.25rem !important;
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 20px !important;
  padding: 0.2rem 0.7rem !important;
  box-shadow: var(--shadow-sm) !important;
  pointer-events: all !important;
  width: auto !important;
  margin: 0 !important;
  white-space: nowrap !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-w) div[data-testid="stHorizontalBlock"]:hover,
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-h) div[data-testid="stHorizontalBlock"]:hover {
  border-color: var(--amber) !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-w) div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-h) div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
  width: auto !important;
  flex: 0 0 auto !important;
  min-width: 0 !important;
  padding: 0 !important;
}
.sf-dim-arrow {
  font-family: var(--font-game);
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-dim);
  line-height: 1;
}
.sf-dim-unit {
  font-family: var(--font-game);
  font-size: 0.7rem;
  color: var(--text-dim);
  line-height: 1;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-w) [data-testid="stNumberInput"],
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-h) [data-testid="stNumberInput"] {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  margin: 0 !important;
  min-height: 0 !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-w) [data-testid="stNumberInput"] input,
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-h) [data-testid="stNumberInput"] input {
  font-family: var(--font-game) !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  width: 2.6rem !important;
  min-width: 2.6rem !important;
  text-align: center !important;
  background: transparent !important;
  color: var(--text) !important;
  border: none !important;
  padding: 0 !important;
  margin: 0 !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-w) [data-testid="stNumberInputStepDown"],
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-w) [data-testid="stNumberInputStepUp"],
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-h) [data-testid="stNumberInputStepDown"],
div[data-testid="stColumn"]:has(.sf-canvas-col-root) > div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]:has(.sf-dim-h) [data-testid="stNumberInputStepUp"] {
  display: none !important;
}

/* ── 8. Bottom HUD tooltips — info (i) hover diagrams for Gap / Alley reach / etc. ── */
.sf-hud-cell,
.sf-hud-var {
  position: relative;
}
.sf-hud-cell .sf-hud-tooltip,
.sf-hud-var .sf-hud-tooltip {
  position: absolute;
  bottom: calc(100% + 10px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--surface2);
  border: 1px solid var(--border2);
  border-radius: 12px;
  padding: 8px;
  width: 140px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  z-index: 100;
}
.sf-hud-cell:hover .sf-hud-tooltip,
.sf-hud-var:hover .sf-hud-tooltip {
  opacity: 1;
}
.sf-hud-tooltip-label {
  font-size: 10px;
  color: var(--text-dim);
  text-align: center;
  margin-top: 6px;
  line-height: 1.4;
}
.info-dot {
  display: inline-flex;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid var(--text-dim);
  align-items: center;
  justify-content: center;
  font-size: 8px;
  color: var(--text-dim);
}
.sf-hud-label.amber .info-dot,
.info-dot.amber {
  border-color: var(--amber);
  color: var(--amber);
}
.sf-hud-var {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  width: 100%;
  text-align: center;
}
.sf-hud-var-accent .sf-hud-label,
.sf-hud-var-accent .sf-hud-val-display {
  color: var(--amber);
}

/* ── 9. Panel type selector — A / B / + colored squares (Setup left rail) ── */
.sf-panel-type-row-marker {
  display: none !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-panel-type-row-marker):not(:has(.sf-left-rail-root)) {
  width: 100% !important;
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  justify-content: center !important;
  align-items: center !important;
  gap: 8px !important;
  padding: 0.35rem 1rem 0.9rem !important;
  margin: 0 !important;
  border-bottom: 1px solid var(--border) !important;
  min-height: 40px !important;
  overflow: visible !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-panel-type-row-marker):not(:has(.sf-left-rail-root)) > div[data-testid="stColumn"] {
  flex: 0 0 32px !important;
  width: 32px !important;
  min-width: 32px !important;
  max-width: 32px !important;
  height: 32px !important;
  min-height: 32px !important;
  max-height: 32px !important;
  padding: 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  align-self: center !important;
  overflow: visible !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-panel-type-row-marker):not(:has(.sf-left-rail-root)) > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {
  width: 100% !important;
  height: 100% !important;
  min-height: 0 !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  align-items: center !important;
  gap: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-panel-type-row-marker):not(:has(.sf-left-rail-root)) [data-testid="stElementContainer"]:has(.sf-panel-type-row-marker) {
  display: none !important;
  height: 0 !important;
  min-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-panel-type-row-marker):not(:has(.sf-left-rail-root)) [data-testid="stElementContainer"]:has([data-testid="stButton"]) {
  width: 32px !important;
  height: 32px !important;
  min-height: 32px !important;
  margin: 0 !important;
  padding: 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  flex: 0 0 32px !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-panel-type-row-marker):not(:has(.sf-left-rail-root)) [data-testid="stButton"] {
  width: 32px !important;
  height: 32px !important;
  min-height: 32px !important;
  margin: 0 !important;
  padding: 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-panel-type-row-marker):not(:has(.sf-left-rail-root)) button {
  width: 32px !important;
  height: 32px !important;
  min-width: 32px !important;
  min-height: 32px !important;
  max-width: 32px !important;
  max-height: 32px !important;
  padding: 0 !important;
  border-radius: 8px !important;
  font-family: var(--font-game) !important;
  font-weight: 700 !important;
  font-size: 14px !important;
  line-height: 1 !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-sizing: border-box !important;
  transition: all 0.2s ease !important;
}

/* ── 10. Panel count lock button — legacy marker fallback ── */
.sf-lock-marker ~ div button {
  border-radius: 6px !important;
  border: 1.5px solid var(--border2) !important;
  background: var(--surface2) !important;
}

/* ── 11. Nav stepper buttons — clickable step fallback (sf-nav-btn-marker) ── */
div[data-testid="stHorizontalBlock"]:has(.sf-nav-btn-marker) {
  gap: 0.15rem !important;
  justify-content: center !important;
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  padding: 0.35rem 0.75rem 0.6rem !important;
  box-shadow: 0 4px 32px rgba(0,0,0,0.5);
  max-width: 720px;
  margin: 0 auto 1rem auto !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-nav-btn-marker) [data-testid="stColumn"] {
  flex: 1 1 0 !important;
  min-width: 0 !important;
  text-align: center;
}
div[data-testid="stHorizontalBlock"]:has(.sf-nav-btn-marker) button {
  font-size: 0.6rem !important;
  padding: 0.15rem 0.35rem !important;
  min-height: 1.4rem !important;
  margin-top: 0.15rem;
}

/* ── 12. Game content shell — Structure / Materials / Results tab panels ── */
.sf-shell {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
}
.sf-shell-title {
  font-family: var(--font-game);
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--amber);
  margin: 0 0 0.25rem 0;
}
.sf-shell-caption {
  font-size: 0.78rem;
  color: var(--text-dim);
  margin-bottom: 0.75rem;
}

/* ── 13. Setup left rail — outer card container (224px column + canvas flex) ── */
.stApp:has(.sf-layout-view) div[data-testid="stHorizontalBlock"]:has(.sf-left-rail-root) {
  gap: 0.65rem !important;
  align-items: flex-start !important;
}
/* Left rail card — Panel type, Selected panel, Total panels, Footprint, Auto-fit */
.stApp:has(.sf-layout-view) div[data-testid="stHorizontalBlock"]:has(.sf-left-rail-root) > div[data-testid="stColumn"]:first-child {
  flex: 0 0 224px !important;
  min-width: 224px !important;
  max-width: 224px !important;
  width: 224px !important;
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 16px !important;
  box-shadow: var(--shadow-md) !important;
  overflow: hidden !important;
  padding: 0 !important;
}
/* Layout canvas column — grows to fill remaining viewport width */
.stApp:has(.sf-layout-view) div[data-testid="stHorizontalBlock"]:has(.sf-left-rail-root) > div[data-testid="stColumn"]:last-child {
  flex: 1 1 0% !important;
  width: auto !important;
  min-width: 0 !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) [data-testid="stPlotlyChart"],
div[data-testid="stColumn"]:has(.sf-canvas-col-root) .js-plotly-plot,
div[data-testid="stColumn"]:has(.sf-canvas-col-root) .plot-container {
  width: 100% !important;
}
div[data-testid="stColumn"]:has(.sf-left-rail-root) > div[data-testid="stVerticalBlock"] {
  gap: 0 !important;
  padding: 0 !important;
}
div[data-testid="stColumn"]:has(.sf-left-rail-root) [data-testid="stElementContainer"] {
  margin: 0 !important;
}
/* Hidden DOM anchor — marks left-rail column for :has() selectors */
.sf-left-rail-root {
  display: none !important;
}
/* ── 14. Auto-fit to max area — checkbox + pairs/rows number inputs ── */
div[data-testid="stColumn"]:has(.sf-left-rail-root) .sf-autofit-section [data-testid="stCheckbox"] {
  padding: 0 !important;
  border-top: none !important;
}
div[data-testid="stColumn"]:has(.sf-left-rail-root) .sf-autofit-section [data-testid="stCheckbox"] label span {
  font-size: 0.7rem !important;
  color: var(--text-dim) !important;
  letter-spacing: 0.04em;
}
div[data-testid="stColumn"]:has(.sf-left-rail-root) .sf-autofit-section [data-testid="stNumberInput"] {
  margin-top: 0.35rem;
}
div[data-testid="stColumn"]:has(.sf-left-rail-root) .sf-autofit-section [data-testid="stNumberInput"] label {
  font-size: 0.65rem !important;
  color: var(--text-dim) !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
div[data-testid="stColumn"]:has(.sf-left-rail-root) .sf-autofit-section [data-testid="stNumberInput"] input {
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-family: var(--font-game) !important;
}

/* ── 15. Left-rail shared — section wrappers, labels, standalone section headers ── */
.sf-left-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.sf-panel-section {
  padding: 1rem;
  border-bottom: 1px solid var(--border);
  margin: 0;
}
.sf-panel-section:last-child { border-bottom: none; }
.sf-section-label {
  font-family: var(--font-game);
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 0.62rem;
}
/* Standalone section header — e.g. "Panel type" above Streamlit widget rows */
.sf-section-head {
  font-family: var(--font-game);
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-dim);
  padding: 0.9rem 1rem 0.55rem !important;
}

/* ── 16. Total panels — count box ("24 panels fit") + lock button overlay ── */
.sf-total-panels-section {
  padding-top: 1.15rem !important;
}
.sf-count-box {
  background: var(--surface2);
  border-radius: var(--radius);
  border: 1px solid var(--border2);
  padding: 0.55rem 2.85rem 0.55rem 0.75rem;
  min-height: 3.25rem;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  position: relative;
}
.sf-count-lock-marker {
  display: none !important;
}
div[data-testid="stColumn"]:has(.sf-left-rail-root) [data-testid="stElementContainer"]:has(.sf-count-lock-marker) {
  display: none !important;
  height: 0 !important;
  min-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}
/* Lock button — Streamlit widget pulled into the count box via negative margin */
div[data-testid="stColumn"]:has(.sf-left-rail-root)
  [data-testid="stElementContainer"]:has(.sf-total-panels-section)
  + [data-testid="stElementContainer"]:has(.sf-count-lock-marker)
  + [data-testid="stElementContainer"] {
  margin: -2.65rem 1.75rem 0 auto !important;
  width: 30px !important;
  min-height: 0 !important;
  padding: 0 !important;
  position: relative !important;
  z-index: 2 !important;
}
div[data-testid="stColumn"]:has(.sf-left-rail-root)
  [data-testid="stElementContainer"]:has(.sf-total-panels-section)
  + [data-testid="stElementContainer"]:has(.sf-count-lock-marker)
  + [data-testid="stElementContainer"]
  button {
  width: 30px !important;
  height: 30px !important;
  min-width: 30px !important;
  min-height: 30px !important;
  padding: 0 !important;
  border-radius: 6px !important;
  border: 1.5px solid var(--border2) !important;
  background: var(--surface) !important;
  font-size: 0.85rem !important;
  line-height: 1 !important;
}
div[data-testid="stColumn"]:has(.sf-left-rail-root)
  [data-testid="stElementContainer"]:has(.sf-total-panels-section)
  + [data-testid="stElementContainer"]:has(.sf-count-lock-marker)
  + [data-testid="stElementContainer"]
  button:hover {
  border-color: var(--amber) !important;
  background: var(--amber-dim) !important;
}
.sf-count-body {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  gap: 0.12rem;
  line-height: 1;
  margin: 0;
  padding: 0;
}
.sf-count-num {
  font-family: var(--font-game);
  font-size: 1.625rem;
  font-weight: 700;
  color: var(--amber);
  line-height: 1;
}
.sf-count-label {
  font-size: 0.625rem;
  color: var(--text-dim);
  line-height: 1.3;
  margin-top: 0.1rem;
}
/* ── 17. Selected panel — stats card (length, width, weight, watt-peak) ── */
.sf-panel-card {
  background: var(--surface2);
  border-radius: var(--radius);
  padding: 0.75rem;
  border: 1px solid var(--border2);
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}
.sf-panel-card-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
  margin: 0 auto 0.15rem;
  line-height: 1;
}
.sf-panel-name {
  font-family: var(--font-game);
  font-weight: 700;
  font-size: 0.94rem;
  text-align: center;
  margin-bottom: 0.15rem;
}
.sf-panel-stats {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.sf-stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.7rem;
  padding: 0.05rem 0;
}
.sf-stat-key { color: var(--text-dim); font-size: 0.68rem; }
.sf-stat-val {
  font-family: var(--font-game);
  font-weight: 600;
  font-size: 0.75rem;
  color: var(--text);
}
/* ── 18. Footprint — "Panels + alleys" dimensions and area ── */
.sf-area-box {
  background: var(--surface2);
  border-radius: var(--radius);
  padding: 0.62rem 0.75rem;
  border: 1px solid var(--border2);
  text-align: center;
}
.sf-area-label {
  font-size: 0.625rem;
  color: var(--text-dim);
  margin-bottom: 0.25rem;
}
.sf-area-val {
  font-family: var(--font-game);
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text);
}
.sf-area-sub {
  font-size: 0.625rem;
  color: var(--text-dim);
  margin-top: 0.12rem;
}
/* Auto-fit section wrapper — pairs/rows inputs when auto-fit is unchecked */
.sf-autofit-section {
  padding: 0.85rem 1rem 1rem !important;
}

/* ── 19. Bottom HUD bar — fixed strip: Gap, Alley reach, Alley W, Spine, NEXT ── */
.stApp:has(.sf-layout-view) div[data-testid="stHorizontalBlock"]:has(.sf-hud-bar-marker) {
  position: fixed !important;
  bottom: 1.1rem !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
  z-index: 50 !important;
  display: flex !important;
  align-items: stretch !important;
  gap: 0 !important;
  width: max-content !important;
  min-width: 560px !important;
  max-width: calc(100vw - 2rem) !important;
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 20px !important;
  padding: 0.55rem 0.65rem !important;
  box-shadow: var(--shadow-hud), 0 0 0 1px rgba(245,163,35,0.18), 0 0 28px rgba(245,163,35,0.08) !important;
  flex-wrap: nowrap !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-hud-bar-marker) > div[data-testid="stColumn"] {
  flex: 1 1 0 !important;
  width: auto !important;
  min-width: 108px !important;
  padding: 0.15rem 0.55rem !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 0 !important;
  border-radius: 12px !important;
  transition: background 0.2s ease !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-hud-bar-marker) > div[data-testid="stColumn"]:has(.sf-hud-var-accent):hover {
  background: rgba(245, 163, 35, 0.08) !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-hud-bar-marker) > div[data-testid="stColumn"]:not(:has(.sf-hud-var-accent)):hover {
  background: var(--hud-hover) !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-hud-bar-marker) > div[data-testid="stColumn"]:last-child {
  flex: 0 0 auto !important;
  min-width: 0 !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-hud-bar-marker) > div[data-testid="stColumn"]:not(:last-child) {
  border-right: 1px solid var(--border);
  margin-right: 0.15rem !important;
  padding-right: 0.65rem !important;
}
/* Each HUD variable column — label stacked above − value unit + row */
div[data-testid="stColumn"]:has(.sf-hud-var-anchor) > div[data-testid="stVerticalBlock"] {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 0.35rem !important;
  width: 100% !important;
}
.sf-hud-bar-marker,
.sf-hud-var-anchor,
.sf-hud-controls-marker {
  display: none !important;
}
div[data-testid="stElementContainer"]:has(.sf-hud-controls-marker) {
  display: none !important;
  height: 0 !important;
  min-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}
/* ── 20. HUD Gap / Alley reach / Alley W — label, −/+ steppers, value, unit ── */
/* Control row: −  value  unit  +  (matches UI_upgrade .hud-controls) */
div[data-testid="stVerticalBlock"]:has(.sf-hud-controls-marker) {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 100% !important;
}
div[data-testid="stVerticalBlock"]:has(.sf-hud-controls-marker) > div[data-testid="stHorizontalBlock"] {
  display: inline-flex !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 0.35rem !important;
  width: fit-content !important;
  max-width: 100% !important;
  margin: 0 auto !important;
  padding: 0 !important;
  min-height: 28px !important;
}
div[data-testid="stVerticalBlock"]:has(.sf-hud-controls-marker) > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
  width: auto !important;
  flex: 0 0 auto !important;
  min-width: 0 !important;
  padding: 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  align-self: center !important;
  min-height: 24px !important;
}
div[data-testid="stVerticalBlock"]:has(.sf-hud-controls-marker) > div[data-testid="stHorizontalBlock"] [data-testid="stElementContainer"] {
  margin: 0 !important;
  padding: 0 !important;
  min-height: 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}
div[data-testid="stVerticalBlock"]:has(.sf-hud-controls-marker) > div[data-testid="stHorizontalBlock"] [data-testid="stMarkdownContainer"] p {
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1 !important;
}
div[data-testid="stVerticalBlock"]:has(.sf-hud-controls-marker) > div[data-testid="stHorizontalBlock"] [data-testid="stButton"],
div[data-testid="stVerticalBlock"]:has(.sf-hud-controls-marker) > div[data-testid="stHorizontalBlock"] [data-testid="stElementContainer"]:has(button) {
  margin: 0 !important;
  padding: 0 !important;
  min-height: 0 !important;
  height: auto !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}
div[data-testid="stVerticalBlock"]:has(.sf-hud-controls-marker) > div[data-testid="stHorizontalBlock"] button {
  min-width: 24px !important;
  width: 24px !important;
  height: 24px !important;
  min-height: 24px !important;
  max-height: 24px !important;
  padding: 0 !important;
  margin: 0 !important;
  border-radius: 6px !important;
  border: 1px solid var(--border2) !important;
  background: var(--surface2) !important;
  color: var(--text-dim) !important;
  font-size: 0.95rem !important;
  font-weight: 300 !important;
  line-height: 1 !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  vertical-align: middle !important;
}
div[data-testid="stVerticalBlock"]:has(.sf-hud-controls-marker) > div[data-testid="stHorizontalBlock"] button:hover {
  border-color: var(--amber) !important;
  color: var(--amber) !important;
  background: var(--amber-dim) !important;
}
/* HUD variable cell — label row + value display */
.sf-hud-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  width: 100%;
}
.sf-hud-label {
  font-size: 0.56rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin: 0 0 0.35rem 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  white-space: nowrap;
}
.sf-hud-label.amber { color: var(--amber) !important; }
.sf-hud-val-display {
  font-family: var(--font-game);
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--text);
  text-align: center;
  line-height: 1;
  min-width: 2.25rem;
  min-height: 24px;
  padding: 0;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}
.sf-hud-val-display.amber { color: var(--amber) !important; }
.sf-hud-unit {
  font-size: 0.625rem;
  color: var(--text-dim);
  text-align: center;
  line-height: 1;
  white-space: nowrap;
  min-height: 24px;
  display: inline-flex !important;
  align-items: center !important;
  align-self: center !important;
  margin: 0 !important;
  padding: 0 !important;
}
/* ── 21. HUD Spine edge — TOP / BOTTOM toggle button ── */
div[data-testid="stColumn"]:has(.sf-hud-spine-marker) button {
  min-width: 4.5rem !important;
  width: auto !important;
  height: 30px !important;
  padding: 0 0.6rem !important;
  border-radius: 6px !important;
  border: 1px solid var(--border2) !important;
  background: var(--surface2) !important;
  font-family: var(--font-game) !important;
  font-size: 0.7rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.06em !important;
  color: var(--text) !important;
}
div[data-testid="stColumn"]:has(.sf-hud-spine-marker) button:hover {
  border-color: var(--amber) !important;
  color: var(--amber) !important;
  background: var(--amber-dim) !important;
}
/* ── 22. HUD NEXT — amber proceed button (→ NEXT) ── */
div[data-testid="stColumn"]:has(.sf-hud-proceed-marker) button {
  background: var(--amber) !important;
  color: #000 !important;
  border: none !important;
  border-radius: 14px !important;
  font-family: var(--font-game) !important;
  font-weight: 700 !important;
  letter-spacing: 0.1em !important;
  min-width: 72px !important;
  min-height: 3rem !important;
  padding: 0.35rem 0.85rem !important;
  white-space: pre-line !important;
  line-height: 1.1 !important;
  box-shadow: 0 0 20px var(--amber-glow), 0 0 32px rgba(245,163,35,0.25) !important;
  animation: sf-pulse 2.5s ease-in-out infinite;
}
div[data-testid="stColumn"]:has(.sf-hud-proceed-marker) button:hover {
  background: #ffb740 !important;
  transform: scale(1.03);
}
/* NEXT button pulse glow */
@keyframes sf-pulse {
  0%, 100% { box-shadow: 0 0 18px var(--amber-glow); }
  50% { box-shadow: 0 0 32px rgba(245,163,35,0.6); }
}

/* ── 23. Game shell metrics — stMetric cards on Structure / Materials / Results ── */
.sf-shell [data-testid="stMetric"] {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.5rem;
}
.sf-shell [data-testid="stMetricLabel"] {
  font-family: var(--font-game) !important;
  font-size: 0.62rem !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  color: var(--text-dim) !important;
}
.sf-shell [data-testid="stMetricValue"] {
  font-family: var(--font-game) !important;
  color: var(--text) !important;
}

/* ── 24. Left-rail expanders — compact collapsible panels ── */
.sf-left-panel [data-testid="stExpander"] {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}
</style>
""".replace("GOOGLE_FONTS_PLACEHOLDER", GOOGLE_FONTS)

LIGHT_THEME_CSS = """
<style>
:root {
  --bg: #EEF1F7;
  --surface: #FFFFFF;
  --surface2: #F4F6FB;
  --border: rgba(15,23,42,0.08);
  --border2: rgba(15,23,42,0.14);
  --amber: #C47D08;
  --amber-dim: rgba(196,125,8,0.12);
  --amber-glow: rgba(196,125,8,0.28);
  --text: #1A1F2E;
  --text-dim: #5C677A;
  --shadow-lg: 0 4px 24px rgba(15,23,42,0.1);
  --shadow-md: 0 4px 20px rgba(15,23,42,0.08);
  --shadow-sm: 0 2px 12px rgba(15,23,42,0.08);
  --shadow-hud: 0 8px 32px rgba(15,23,42,0.12);
  --canvas-bg: #F8FAFD;
  --canvas-grid: rgba(15,23,42,0.05);
  --canvas-glow: rgba(91,184,245,0.08);
  --hud-hover: rgba(15,23,42,0.05);
}

/* Streamlit config uses base=dark — override native widgets in light mode */
.stApp [data-testid="stNumberInput"] input {
  color: #1A1F2E !important;
  -webkit-text-fill-color: #1A1F2E !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h) [data-testid="stNumberInput"] input {
  background: transparent !important;
  color: #1A1F2E !important;
  -webkit-text-fill-color: #1A1F2E !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h) .sf-dim-arrow,
div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h) .sf-dim-unit {
  color: #5C677A !important;
}
div[data-testid="stVerticalBlock"]:has(.sf-hud-controls-marker) button,
.stApp [data-testid="stBaseButton-secondary"] button,
.stApp button[kind="secondary"] {
  background-color: #FFFFFF !important;
  background: #FFFFFF !important;
  color: #5C677A !important;
  border: 1px solid rgba(15,23,42,0.14) !important;
}
div[data-testid="stVerticalBlock"]:has(.sf-hud-controls-marker) button:hover,
.stApp [data-testid="stBaseButton-secondary"] button:hover,
.stApp button[kind="secondary"]:hover {
  color: #C47D08 !important;
  border-color: #C47D08 !important;
  background-color: rgba(196,125,8,0.12) !important;
}
div[data-testid="stVerticalBlock"]:has(.sf-main-root) > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child button {
  background-color: #FFFFFF !important;
  color: #1A1F2E !important;
  border: 1px solid rgba(15,23,42,0.14) !important;
}
</style>
"""


def inject_game_theme() -> None:
    """Inject global SolarForge CSS (see GAME_CSS theme map for section index)."""
    st.markdown(GAME_CSS, unsafe_allow_html=True)
    if not is_dark_theme():
        st.markdown(LIGHT_THEME_CSS, unsafe_allow_html=True)


def render_theme_toggle() -> None:
    """Theme switch in the main top bar — same pattern as HUD +/- buttons."""
    is_light = st.session_state.get("sf_color_theme", THEME_DARK) == THEME_LIGHT
    label = "Dark" if is_light else "Light"
    icon = "🌙" if is_light else "☀"
    if st.button(
        f"{icon} {label}",
        key="sf_theme_toggle",
        help="Toggle light/dark theme",
        type="secondary",
    ):
        st.session_state.sf_color_theme = THEME_DARK if is_light else THEME_LIGHT
        st.rerun()
