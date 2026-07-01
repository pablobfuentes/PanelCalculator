# Layout Section — Modification Plan

**Status:** Implemented (2026-06-29)  
**Tracking:** Checkboxes below reflect completion state.

## Scope

Step 2 **Layout** validates proposed column/beam geometry against rules of thumb (DL/LL, span limits, preliminary capacity placeholders). No steel sections, no PyNite, no code checks — those belong in **Structure** (step 3) and **Results** (step 4).

| Step | Name | Purpose |
|------|------|---------|
| 1 | Setup | Panel grid, alleys, max area |
| 2 | **Layout** | Column/beam positions + preliminary checks |
| 3 | **Structure** | Element definition (sections, materials) |
| 4 | Results | Full FEA + code checks + export |

---

## Phase 0 — Product definition

- [x] **0.1** Document stepper rename (this file)
- [x] **0.2** Scope note: Layout = geometry vs rules; no `SteelSection` / PyNite
- [x] **0.3** Logical elements: **Column** (post), **Beam** (horizontal bay between columns)
- [x] **0.4** Preliminary rules in `LayoutRules` (`core/layout_checks.py`)
- [x] **0.5** Governing loads: unfactored DL/LL for display; factored `1.2D + 1.6L` for pass/fail

---

## Phase 1 — Rename & navigation

- [x] **1.1** Routes/files: `web/layout.html`, `web/js/layout.js`, `web/css/layout-extras.css`, `/layout`
- [x] **1.2** Stepper: Setup → **Layout** → **Structure** → Results
- [x] **1.3** localStorage: `solarforge.layout.v1` (+ migrate from `solarforge.structure.v1`)
- [x] **1.4** API: `POST /api/layout-check`; alias `/api/structure` retained
- [x] **1.5** Tests: `tests/test_api_layout_check.py`
- [x] **1.6** `/structure` redirects to `/layout`; Setup **NEXT** → `/layout`

---

## Phase 2 — Strip full analysis from Layout

- [x] **2.1** Remove bottom detail-stack (FEA / code-check tables)
- [x] **2.2** Remove PyNite FEA + `evaluate_code_checks` from layout API
- [x] **2.3** Replace Live BOM steel tonnage with layout quantities (panels, columns, beams, DL/LL)
- [x] **2.4** Remove wind / column height from Layout inputs
- [x] **2.5** Keep tributary partition PASS/FAIL in HUD

---

## Phase 3 — Backend: layout element model + quick checks

- [x] **3.1** `derive_layout_elements()` — columns + beams from tributary grid
- [x] **3.2** DL/LL per column and beam (tributary-based)
- [x] **3.3** `preliminary_check()` — rule-of-thumb pass/fail per element
- [x] **3.4** `LayoutRules` dataclass — configurable placeholders
- [x] **3.5** API response: metrics, elements[], summary, figure JSON, rules
- [x] **3.6** `api/layout_check_service.py` (no Streamlit, no PyNite)

---

## Phase 4 — Visualization

- [x] **4.1** Draw beams as lines between columns (color by preliminary status)
- [x] **4.2** Unified hover: name, position, preliminary status, “Click for full report”
- [x] **4.3** `customdata` on traces for click → element report
- [x] **4.4** Legend chips: Panels, Alleys, Tributary, Columns, Beams
- [ ] **4.5** Optional: migrate to canvas (deferred)

---

## Phase 5 — Frontend interaction

- [x] **5.1** Default right panel: layout summary
- [x] **5.2** Click element → Element Report (checks with ✓/✗)
- [x] **5.3** Close / back to summary
- [x] **5.4** Plotly click handler + selected state
- [x] **5.5** HUD: columns, active, areas, DL, LL, partition, elements passing
- [x] **5.6** NEXT enabled when partition PASS and all elements preliminary PASS

---

## Phase 6 — Left panel (Layout controls)

- [x] **6.1** Keep: column grid X/Y, overrides, obstacles
- [x] **6.2** Remove: wind speed / exposure
- [x] **6.3** Remove: column height
- [x] **6.4** Rules-of-thumb read-only caption
- [x] **6.5** Partition banner retained

---

## Phase 7 — Handoff to Structure step

- [x] **7.1** Layout **NEXT** saves `solarforge.layout.handoff.v1`
- [ ] **7.2** Structure step consumes handoff (future — step 3 not built)
- [x] **7.3** Preliminary vs code-check distinction documented here and in `core/layout_checks.py`

---

## Phase 8 — Testing & acceptance

- [x] **8.1** Unit tests: `tests/test_layout_checks.py`
- [x] **8.2** API tests: `tests/test_api_layout_check.py`
- [ ] **8.3** Manual UI smoke (Setup → Layout → hover → click → report)
- [x] **8.4** API has no FEA / code-check fields in layout-check response

---

## File map

| Before | After |
|--------|-------|
| `web/structure.html` | `web/layout.html` (`/structure` → redirect) |
| `web/js/structure.js` | `web/js/layout.js` |
| `api/structure_service.py` | `api/layout_check_service.py` (legacy service unused by main) |
| `POST /api/structure` | `POST /api/layout-check` (+ alias) |
| FEA + code tables | Element report on click |
| Step 2 “Structure” | Step 2 **Layout** |
| Step 3 “Materials” | Step 3 **Structure** (placeholder) |

## Key modules

- `core/layout_checks.py` — element derivation + preliminary rules
- `api/layout_check_service.py` — layout-check API
- `core/visualization.py` — beams + status-colored columns (`layout_elements` param)
- `web/layout.html` + `web/js/layout.js` — UI
