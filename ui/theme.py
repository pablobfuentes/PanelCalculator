"""SolarForge game UI theme — dark visual shell for Streamlit."""

from __future__ import annotations

import streamlit as st

GOOGLE_FONTS = (
    "https://fonts.googleapis.com/css2?"
    "family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap"
)

GAME_CSS = """
<style>
@import url('GOOGLE_FONTS_PLACEHOLDER');

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
}

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

/* ── App header ── */
.sf-header {
  text-align: center;
  margin-bottom: 0.25rem;
}
.sf-title {
  font-family: var(--font-game);
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text);
  margin: 0;
}
.sf-title span { color: var(--amber); }
.sf-tagline {
  font-size: 0.75rem;
  color: var(--text-dim);
  margin-top: 0.15rem;
}

/* ── Stepper ── */
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
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  padding: 0.35rem 0.75rem 0.6rem;
  box-shadow: 0 4px 32px rgba(0,0,0,0.5);
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
.sf-step.active { color: var(--amber); }
.sf-step.done { color: var(--green); }
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
  background: var(--amber);
  border-color: var(--amber);
  color: #000;
  box-shadow: 0 0 12px var(--amber-glow);
}
.sf-step.done .sf-step-icon {
  background: var(--green);
  border-color: var(--green);
  color: #000;
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

/* ── Setup / Layout stage (match HTML.JPG) ── */
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
.stApp:has(.sf-layout-view) .sf-header {
  display: none !important;
}
.stApp:has(.sf-layout-view) .sf-stepper-wrap {
  margin: 0 0 0.45rem !important;
}
.stApp:has(.sf-layout-view) .sf-stepper {
  padding: 0.3rem 0.65rem 0.5rem !important;
}
.stApp:has(.sf-layout-view) .block-container {
  padding-bottom: 6.5rem !important;
}
.stApp:has(.sf-layout-view) div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
  gap: 0.35rem !important;
}

/* ── Canvas board + floating dimension pills ── */
div[data-testid="stColumn"]:has(.sf-canvas-col-root) {
  position: relative !important;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) [data-testid="stPlotlyChart"] {
  background: #0A0E18 !important;
  background-image:
    radial-gradient(circle at 50% 50%, rgba(91,184,245,0.04) 0%, transparent 70%),
    linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 100% 100%, 40px 40px, 40px 40px;
  border: 1px solid var(--border2);
  border-radius: var(--radius-lg);
  padding: 0.5rem;
  box-shadow: inset 0 0 80px rgba(91,184,245,0.04), 0 8px 40px rgba(0,0,0,0.4);
  overflow: hidden;
}
div[data-testid="stColumn"]:has(.sf-canvas-col-root) [data-testid="stPlotlyChart"] .main-svg {
  background: transparent !important;
}

/* The dim overlay row (inner hblock carrying both slot markers, never the main layout row) */
div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h):not(:has(.sf-left-rail-root)) {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 8 !important;
  pointer-events: none !important;
  display: block !important;
  margin: 0 !important;
  padding: 0 !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h):not(:has(.sf-left-rail-root)) > div[data-testid="stColumn"] {
  position: absolute !important;
  width: auto !important;
  flex: none !important;
  pointer-events: none !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h):not(:has(.sf-left-rail-root)) > div[data-testid="stColumn"]:has(.sf-dim-w) {
  top: 0.7rem;
  left: 50%;
  transform: translateX(-50%);
}
div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h):not(:has(.sf-left-rail-root)) > div[data-testid="stColumn"]:has(.sf-dim-h) {
  top: 50%;
  right: 0.9rem;
  transform: translateY(-50%);
}
/* inner pill = the arrow/value/unit hblock */
div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h):not(:has(.sf-left-rail-root)) div[data-testid="stHorizontalBlock"] {
  display: inline-flex !important;
  align-items: center !important;
  gap: 0.25rem !important;
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 20px !important;
  padding: 0.2rem 0.7rem !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.35) !important;
  pointer-events: all !important;
  width: auto !important;
  margin: 0 !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h):not(:has(.sf-left-rail-root)) div[data-testid="stHorizontalBlock"]:hover {
  border-color: var(--amber) !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h):not(:has(.sf-left-rail-root)) div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
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
div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h):not(:has(.sf-left-rail-root)) [data-testid="stNumberInput"] {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  margin: 0 !important;
  min-height: 0 !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h):not(:has(.sf-left-rail-root)) [data-testid="stNumberInput"] input {
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
div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h):not(:has(.sf-left-rail-root)) [data-testid="stNumberInputStepDown"],
div[data-testid="stHorizontalBlock"]:has(.sf-dim-w):has(.sf-dim-h):not(:has(.sf-left-rail-root)) [data-testid="stNumberInputStepUp"] {
  display: none !important;
}

/* HUD tooltips */
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
.sf-hud-label.amber .info-dot {
  border-color: var(--amber);
  color: var(--amber);
}

/* Panel type squares */
div[data-testid="stHorizontalBlock"]:has(.sf-panel-type-row-marker):not(:has(.sf-left-rail-root)) {
  width: 100% !important;
  display: flex !important;
  flex-wrap: nowrap !important;
  gap: 6px !important;
  align-items: center !important;
  padding: 0 1rem 0.9rem !important;
  margin: 0 !important;
  border-bottom: 1px solid rgba(255,255,255,0.07) !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-panel-type-row-marker):not(:has(.sf-left-rail-root)) > div[data-testid="stColumn"] {
  flex: 0 0 32px !important;
  width: 32px !important;
  min-width: 32px !important;
  max-width: 32px !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-panel-type-row-marker):not(:has(.sf-left-rail-root)) > div[data-testid="stColumn"]:last-child {
  margin-left: auto !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-panel-type-row-marker):not(:has(.sf-left-rail-root)) button {
  width: 32px !important;
  height: 32px !important;
  min-width: 32px !important;
  min-height: 32px !important;
  padding: 0 !important;
  border-radius: 8px !important;
  font-family: var(--font-game) !important;
  font-weight: 700 !important;
  font-size: 14px !important;
  line-height: 1 !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.2s ease !important;
}

/* Lock button styling — legacy marker fallback */
.sf-lock-marker ~ div button {
  border-radius: 6px !important;
  border: 1.5px solid var(--border2) !important;
  background: var(--surface2) !important;
}

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

/* ── Game content shell ── */
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

/* ── Left rail (setup) — the first column is the card ── */
.stApp:has(.sf-layout-view) div[data-testid="stHorizontalBlock"]:has(.sf-left-rail-root) {
  gap: 0.65rem !important;
  align-items: flex-start !important;
}
.stApp:has(.sf-layout-view) div[data-testid="stHorizontalBlock"]:has(.sf-left-rail-root) > div[data-testid="stColumn"]:first-child {
  flex: 0 0 224px !important;
  min-width: 224px !important;
  max-width: 224px !important;
  width: 224px !important;
  background: #161B27 !important;
  border: 1px solid rgba(255, 255, 255, 0.13) !important;
  border-radius: 16px !important;
  box-shadow: 0 4px 28px rgba(0, 0, 0, 0.45) !important;
  overflow: hidden !important;
  padding: 0 !important;
}
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
.sf-left-rail-root {
  display: none !important;
}
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

.sf-left-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.sf-panel-section {
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
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
/* Standalone section header (label that precedes Streamlit widgets) */
.sf-section-head {
  font-family: var(--font-game);
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-dim);
  padding: 0.9rem 1rem 0.55rem !important;
}
/* Card sections that sit between widgets need their own side padding */
div[data-testid="stColumn"]:has(.sf-left-rail-root) div[data-testid="stHorizontalBlock"]:has(.sf-count-lock-marker) {
  margin: 0 1rem 0.9rem !important;
}
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
div[data-testid="stHorizontalBlock"]:has(.sf-count-lock-marker):not(:has(.sf-left-rail-root)) {
  display: flex !important;
  align-items: center !important;
  gap: 0.5rem !important;
  background: var(--surface2) !important;
  border-radius: var(--radius) !important;
  border: 1px solid var(--border2) !important;
  padding: 0.5rem 0.7rem !important;
  margin: 0 !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-count-lock-marker):not(:has(.sf-left-rail-root)) > div[data-testid="stColumn"]:first-child {
  flex: 1 1 auto !important;
  width: auto !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-count-lock-marker):not(:has(.sf-left-rail-root)) > div[data-testid="stColumn"]:last-child {
  flex: 0 0 30px !important;
  width: 30px !important;
  min-width: 30px !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-count-lock-marker):not(:has(.sf-left-rail-root)) button {
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
div[data-testid="stHorizontalBlock"]:has(.sf-count-lock-marker):not(:has(.sf-left-rail-root)) button:hover {
  border-color: var(--amber) !important;
  background: var(--amber-dim) !important;
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
.sf-autofit-section {
  padding: 0.85rem 1rem 1rem !important;
}

/* ── Bottom HUD (fixed bar built from a Streamlit column row) ── */
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
  max-width: calc(100vw - 2rem) !important;
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 20px !important;
  padding: 0.5rem 0.4rem !important;
  box-shadow: 0 8px 48px rgba(0,0,0,0.6), 0 0 0 1px rgba(245,163,35,0.08) !important;
  flex-wrap: nowrap !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-hud-bar-marker) > div[data-testid="stColumn"] {
  flex: 0 0 auto !important;
  width: auto !important;
  min-width: 0 !important;
  padding: 0 0.6rem !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: flex-start !important;
  gap: 0.3rem !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-hud-bar-marker) > div[data-testid="stColumn"]:not(:last-child) {
  border-right: 1px solid var(--border);
}
/* inner control row: − value unit + */
div[data-testid="stHorizontalBlock"]:has(.sf-hud-bar-marker) div[data-testid="stHorizontalBlock"] {
  display: flex !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 0.3rem !important;
  width: auto !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-hud-bar-marker) div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
  width: auto !important;
  flex: 0 0 auto !important;
  min-width: 0 !important;
  padding: 0 !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-hud-bar-marker) div[data-testid="stHorizontalBlock"] button {
  min-width: 24px !important;
  width: 24px !important;
  height: 24px !important;
  padding: 0 !important;
  border-radius: 6px !important;
  border: 1px solid var(--border2) !important;
  background: var(--surface2) !important;
  color: var(--text-dim) !important;
  font-size: 0.95rem !important;
  font-weight: 300 !important;
  line-height: 1 !important;
}
div[data-testid="stHorizontalBlock"]:has(.sf-hud-bar-marker) div[data-testid="stHorizontalBlock"] button:hover {
  border-color: var(--amber) !important;
  color: var(--amber) !important;
  background: var(--amber-dim) !important;
}
.sf-hud-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}
.sf-hud-label {
  font-size: 0.56rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 0.2rem;
  display: flex;
  align-items: center;
  gap: 0.2rem;
  white-space: nowrap;
}
.sf-hud-label.amber { color: var(--amber); }
.sf-hud-val-display {
  font-family: var(--font-game);
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--text);
  text-align: center;
  line-height: 1;
  min-width: 1.6rem;
  padding: 0;
}
.sf-hud-val-display.amber { color: var(--amber); }
.sf-hud-unit {
  font-size: 0.6rem;
  color: var(--text-dim);
  text-align: center;
  align-self: flex-end;
  margin-bottom: 0.15rem;
  line-height: 1;
  white-space: nowrap;
}
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
  box-shadow: 0 0 20px var(--amber-glow) !important;
  animation: sf-pulse 2.5s ease-in-out infinite;
}
div[data-testid="stColumn"]:has(.sf-hud-proceed-marker) button:hover {
  background: #ffb740 !important;
  transform: scale(1.03);
}
@keyframes sf-pulse {
  0%, 100% { box-shadow: 0 0 18px var(--amber-glow); }
  50% { box-shadow: 0 0 32px rgba(245,163,35,0.6); }
}

/* Metrics & dataframes in game shell */
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

/* Compact expanders */
.sf-left-panel [data-testid="stExpander"] {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}
</style>
""".replace("GOOGLE_FONTS_PLACEHOLDER", GOOGLE_FONTS)


def inject_game_theme() -> None:
    """Inject global SolarForge CSS every run."""
    st.markdown(GAME_CSS, unsafe_allow_html=True)
