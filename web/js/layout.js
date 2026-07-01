/**
 * SolarForge Layout — column/beam grid, preliminary rules, element report.
 */

const SNAPSHOT_KEY = 'solarforge.setup.snapshot.v1';
const SETUP_KEY = 'solarforge.setup.v1';
const LAYOUT_KEY = 'solarforge.layout.v1';
const HANDOFF_KEY = 'solarforge.layout.handoff.v1';
const LEGACY_LAYOUT_KEY = 'solarforge.structure.v1';
const DEFAULT_SPACING_M = 3.5;

const DEFAULT_STATE = {
  columnCountX: 2,
  columnCountY: 2,
  columnOverrides: '',
  obstacles: '',
  countsSeeded: false,
};

const state = loadLayoutState();
let accepted = null;
let layoutData = null;
let selectedElementId = null;
let fetchTimer = null;
const toastEl = document.getElementById('toast');

function loadLayoutState() {
  try {
    let raw = localStorage.getItem(LAYOUT_KEY);
    if (!raw) raw = localStorage.getItem(LEGACY_LAYOUT_KEY);
    if (raw) return { ...DEFAULT_STATE, ...JSON.parse(raw) };
  } catch (_) {
    /* ignore */
  }
  return { ...DEFAULT_STATE };
}

function saveLayoutState() {
  localStorage.setItem(LAYOUT_KEY, JSON.stringify(state));
}

function showToast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.add('show');
  setTimeout(() => toastEl.classList.remove('show'), 2400);
}

function loadAcceptedLayout() {
  try {
    const raw = localStorage.getItem(SNAPSHOT_KEY);
    if (raw) return JSON.parse(raw);
  } catch (_) {
    /* ignore */
  }
  return null;
}

function showEmptyState() {
  document.getElementById('empty-state').classList.add('is-visible');
  document.getElementById('plotly-chart').style.visibility = 'hidden';
}

function hideEmptyState() {
  document.getElementById('empty-state').classList.remove('is-visible');
  document.getElementById('plotly-chart').style.visibility = 'visible';
}

function saveAcceptedLayout(payload) {
  localStorage.setItem(SNAPSHOT_KEY, JSON.stringify(payload));
  accepted = payload;
}

async function recoverLayoutSnapshot() {
  try {
    const raw = localStorage.getItem(SETUP_KEY);
    if (!raw) return null;
    const setup = { ...JSON.parse(raw) };
    const catRes = await fetch('/api/catalog');
    if (!catRes.ok) return null;
    const defaults = await catRes.json();
    const custom = setup.customPanels || [];
    const keys = new Set(defaults.map((p) => p.key));
    const catalog = [...defaults, ...custom.filter((p) => !keys.has(p.key))];
    const panel = catalog.find((p) => p.key === setup.panelKey);
    if (!panel) return null;

    const body = {
      panel_key: panel.key,
      panel: {
        key: panel.key,
        name: panel.name,
        length: panel.length,
        width: panel.width,
        weight: panel.weight,
        watt_peak: panel.watt_peak ?? 0,
        color: panel.color,
        tilt_angle: panel.tilt_angle ?? 10,
      },
      max_area_x: setup.maxAreaX ?? 12,
      max_area_y: setup.maxAreaY ?? 8,
      mid_clamp_in: setup.gap ?? 1,
      alley_width: setup.alleyW ?? 1,
      alley_reach: setup.reach ?? 2,
      spine_edge: setup.spineEdge ?? 'bottom',
      use_fit: !setup.locked,
      panels_locked: Boolean(setup.locked),
      target_panels: setup.locked ? setup.lockedCount : 0,
      num_pairs_manual: 3,
      num_rows_manual: 2,
    };

    const res = await fetch('/api/layout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) return null;
    const layout = await res.json();
    if (!layout.snapshot) return null;

    const payload = {
      snapshot: layout.snapshot,
      panels_locked: Boolean(setup.locked),
      locked_panel_count: setup.locked ? setup.lockedCount : 0,
      footprint: { w: layout.stats.footprint_w, h: layout.stats.footprint_h },
    };
    saveAcceptedLayout(payload);
    return payload;
  } catch (_) {
    return null;
  }
}

function defaultColumnCount(extent) {
  if (extent <= 0) return 2;
  return Math.max(2, Math.round(extent / DEFAULT_SPACING_M) + 1);
}

function seedColumnCounts(fieldW, fieldH) {
  if (state.countsSeeded) return;
  state.columnCountX = defaultColumnCount(fieldW);
  state.columnCountY = defaultColumnCount(fieldH);
  state.countsSeeded = true;
  saveLayoutState();
}

function syncFormFromState() {
  document.getElementById('col-count-x').value = state.columnCountX;
  document.getElementById('col-count-y').value = state.columnCountY;
  document.getElementById('col-overrides').value = state.columnOverrides;
  document.getElementById('obstacles').value = state.obstacles;
}

function readFormToState() {
  state.columnCountX = Math.max(2, parseInt(document.getElementById('col-count-x').value, 10) || 2);
  state.columnCountY = Math.max(2, parseInt(document.getElementById('col-count-y').value, 10) || 2);
  state.columnOverrides = document.getElementById('col-overrides').value;
  state.obstacles = document.getElementById('obstacles').value;
  saveLayoutState();
}

function buildRequestBody() {
  if (!accepted?.snapshot) throw new Error('No accepted layout');
  return {
    snapshot: accepted.snapshot,
    column_count_x: state.columnCountX,
    column_count_y: state.columnCountY,
    column_overrides: state.columnOverrides,
    obstacle_zones: state.obstacles,
    panels_locked: Boolean(accepted.panels_locked),
    locked_panel_count: accepted.locked_panel_count || 0,
  };
}

async function fetchLayoutCheck() {
  const res = await fetch('/api/layout-check', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(buildRequestBody()),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

function scheduleRefresh() {
  clearTimeout(fetchTimer);
  fetchTimer = setTimeout(() => refreshLayout().catch((e) => showToast(e.message)), 350);
}

function renderRulesCaption(rules) {
  if (!rules) return;
  const el = document.getElementById('rules-caption');
  el.textContent =
    `L/${rules.deflection_limit_denominator} deflection, ` +
    `max span ${rules.max_recommended_beam_span_m} m, ` +
    `LL ${rules.live_load_kn_m2} kN/m², ` +
    `1.2D+1.6L screening. No sections chosen.`;
}

function renderSummary(summary, metrics) {
  document.getElementById('sum-panels').textContent = String(summary.panel_count);
  const colLabel =
    summary.column_count !== summary.active_column_count
      ? `${summary.active_column_count} (${summary.column_count})`
      : String(summary.active_column_count);
  document.getElementById('sum-columns').textContent = colLabel;
  document.getElementById('sum-beams').textContent = String(summary.beam_count);
  document.getElementById('sum-beam-len').textContent = `${summary.beam_length_m.toFixed(1)} m`;
  document.getElementById('sum-dl').textContent = `${summary.total_dead_kn.toFixed(2)} kN`;
  document.getElementById('sum-ll').textContent = `${summary.total_live_kn.toFixed(2)} kN`;
  document.getElementById('sum-passing').textContent =
    `${metrics.elements_passing}/${metrics.element_count}`;

  document.getElementById('spacing-x').textContent = `${metrics.spacing_x.toFixed(2)} m spacing`;
  document.getElementById('spacing-y').textContent = `${metrics.spacing_y.toFixed(2)} m spacing`;
  document.getElementById('m-columns').textContent = String(metrics.column_count);
  document.getElementById('m-active').textContent = String(metrics.active_count);
  document.getElementById('m-panel-area').textContent = `${metrics.panel_area_m2.toFixed(2)} m²`;
  document.getElementById('m-dl').textContent = `${metrics.total_dead_kn.toFixed(2)} kN`;
  document.getElementById('m-ll').textContent = `${metrics.total_live_kn.toFixed(2)} kN`;
  document.getElementById('m-elements').textContent =
    `${metrics.elements_passing}/${metrics.element_count}`;

  const partEl = document.getElementById('m-partition');
  if (metrics.parse_error) {
    partEl.textContent = 'ERR';
    partEl.className = 'hud-metric-val fail';
  } else {
    partEl.textContent = metrics.partition_ok ? 'PASS' : 'FAIL';
    partEl.className = `hud-metric-val ${metrics.partition_ok ? 'ok' : 'fail'}`;
  }

  const banner = document.getElementById('partition-banner');
  const msg = document.getElementById('partition-msg');
  if (metrics.parse_error) {
    banner.hidden = false;
    banner.className = 'panel-section partition-banner fail';
    msg.textContent = metrics.parse_error;
  } else if (metrics.partition_ok) {
    banner.hidden = false;
    banner.className = 'panel-section partition-banner ok';
    msg.textContent = 'Active tributary zones cover the full panel area.';
  } else {
    banner.hidden = false;
    banner.className = 'panel-section partition-banner fail';
    const delta = Math.abs(metrics.tributary_area_m2 - metrics.panel_area_m2);
    msg.textContent = `Tributary areas do not match panel area (Δ ${delta.toFixed(4)} m²).`;
  }
}

function clearElementReport() {
  selectedElementId = null;
  document.getElementById('report-empty').hidden = false;
  document.getElementById('report-content').hidden = true;
  document.getElementById('report-close').hidden = true;
  clearPlotlySelection();
}

function renderElementReport(element) {
  if (!element) {
    clearElementReport();
    return;
  }
  selectedElementId = element.element_id;
  document.getElementById('report-empty').hidden = true;
  document.getElementById('report-content').hidden = false;
  document.getElementById('report-close').hidden = false;

  document.getElementById('report-name').textContent = element.name;
  document.getElementById('report-type').textContent = element.element_type;

  let positionText;
  if (element.element_type === 'beam' && element.x2 != null && element.y2 != null) {
    positionText =
      `From (${element.x.toFixed(2)}, ${element.y.toFixed(2)}) m → ` +
      `(${element.x2.toFixed(2)}, ${element.y2.toFixed(2)}) m · Span ${element.span_m.toFixed(2)} m`;
  } else {
    positionText = `Plan position (${element.x.toFixed(2)}, ${element.y.toFixed(2)}) m`;
  }
  document.getElementById('report-position').textContent = positionText;

  const loadsHtml =
    `DL: ${element.dead_load_kn.toFixed(3)} kN<br>` +
    `LL: ${element.live_load_kn.toFixed(3)} kN<br>` +
    `Factored (1.2D+1.6L): ${element.factored_load_kn.toFixed(3)} kN`;
  document.getElementById('report-loads').innerHTML = loadsHtml;

  const checksEl = document.getElementById('report-checks');
  if (element.checks.length === 0) {
    checksEl.innerHTML =
      '<div class="check-row pass"><span class="check-label">Axial / gravity screening</span>' +
      '<span class="check-value">—</span><span class="check-icon pass">✓</span></div>';
  } else {
    checksEl.innerHTML = element.checks
      .map(
        (check) =>
          `<div class="check-row ${check.passed ? 'pass' : 'fail'}">` +
          `<span class="check-label">${check.label}</span>` +
          `<span class="check-value">${check.value} / ${check.limit} ${check.unit}</span>` +
          `<span class="check-icon ${check.passed ? 'pass' : 'fail'}">${check.passed ? '✓' : '✗'}</span>` +
          `</div>`,
      )
      .join('');
  }

  if (element.element_type === 'beam') {
    checksEl.innerHTML +=
      '<div class="check-row pass"><span class="check-label">Max torsion</span>' +
      '<span class="check-value">N/A at layout stage</span><span class="check-icon pass">—</span></div>';
  }

  const overall = document.getElementById('report-overall');
  overall.className = `report-overall ${element.overall_pass ? 'pass' : 'fail'}`;
  overall.textContent = element.overall_pass
    ? `✓ Preliminary ${element.preliminary_status}`
    : `✗ Preliminary ${element.preliminary_status}`;
}

function findElement(elementId) {
  return layoutData?.elements?.find((element) => element.element_id === elementId) ?? null;
}

let plotlyClickBound = false;

function clearPlotlySelection() {
  const host = document.getElementById('plotly-chart');
  if (!host?.data?.length) return;
  const indices = host.data.map((_, i) => i);
  Plotly.restyle(host, { selectedpoints: indices.map(() => null) }, indices);
}

function handlePlotlyClick(event) {
  const point = event.points?.[0];
  if (!point) return;
  const raw = point.customdata;
  const elementId = Array.isArray(raw) ? raw[0] : raw;
  if (elementId) renderElementReport(findElement(elementId));
  clearPlotlySelection();
}

function renderPlotly(figure) {
  const host = document.getElementById('plotly-chart');
  const fitHeight = Math.max(host.clientHeight, 520);
  const fitWidth = Math.max(host.clientWidth, 400);
  const layout = {
    ...figure.layout,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    autosize: true,
    height: fitHeight,
    width: fitWidth,
    margin: figure.layout?.margin || { l: 24, r: 24, t: 24, b: 24 },
    clickmode: 'event',
  };
  Plotly.react(host, figure.data, layout, {
    responsive: true,
    displayModeBar: false,
    scrollZoom: true,
  }).then(() => {
    if (!plotlyClickBound) {
      host.on('plotly_click', handlePlotlyClick);
      plotlyClickBound = true;
    }
    Plotly.Plots.resize(host);
  });
}

function saveHandoff(data) {
  localStorage.setItem(
    HANDOFF_KEY,
    JSON.stringify({
      snapshot: accepted?.snapshot,
      panels_locked: accepted?.panels_locked,
      locked_panel_count: accepted?.locked_panel_count || 0,
      layout_state: { ...state },
      metrics: data.metrics,
      elements: data.elements,
      saved_at: Date.now(),
    }),
  );
}

function canProceed(metrics, elements) {
  if (!metrics.partition_ok || metrics.parse_error) return false;
  return elements.every((element) => element.overall_pass);
}

async function refreshLayout(reseedAttempt = false) {
  readFormToState();
  const data = await fetchLayoutCheck();

  if (!state.countsSeeded && !reseedAttempt) {
    seedColumnCounts(data.metrics.field_width, data.metrics.field_height);
    document.getElementById('col-count-x').value = state.columnCountX;
    document.getElementById('col-count-y').value = state.columnCountY;
    saveLayoutState();
    return refreshLayout(true);
  }

  layoutData = data;
  hideEmptyState();
  renderPlotly(data.figure);
  renderRulesCaption(data.rules);
  renderSummary(data.summary, data.metrics);
  saveHandoff(data);

  if (selectedElementId) {
    const element = findElement(selectedElementId);
    if (element) renderElementReport(element);
    else clearElementReport();
  }

  document.getElementById('next-btn').disabled = !canProceed(data.metrics, data.elements);

  requestAnimationFrame(() => {
    const host = document.getElementById('plotly-chart');
    if (!host?.data) return;
    Plotly.relayout(host, {
      height: Math.max(host.clientHeight, 520),
      width: Math.max(host.clientWidth, 400),
    });
    Plotly.Plots.resize(host);
  });
}

function bindEvents() {
  ['col-count-x', 'col-count-y', 'col-overrides', 'obstacles'].forEach((id) => {
    const el = document.getElementById(id);
    el.addEventListener('input', scheduleRefresh);
    el.addEventListener('change', scheduleRefresh);
  });

  document.getElementById('report-close').addEventListener('click', clearElementReport);

  document.getElementById('next-btn').addEventListener('click', () => {
    if (layoutData) saveHandoff(layoutData);
    showToast('Structure step coming soon');
  });

  window.addEventListener('resize', () => {
    const host = document.getElementById('plotly-chart');
    if (!host?.data) return;
    Plotly.relayout(host, {
      height: Math.max(host.clientHeight, 520),
      width: Math.max(host.clientWidth, 400),
    });
    Plotly.Plots.resize(host);
  });
}

function updateHudReserve() {
  const hud = document.querySelector('.layout-hud');
  if (!hud) return;
  const h = Math.ceil(hud.getBoundingClientRect().height);
  document.documentElement.style.setProperty('--hud-reserve', `${Math.max(96, h + 16)}px`);
}

async function init() {
  bindEvents();
  syncFormFromState();
  updateHudReserve();

  accepted = loadAcceptedLayout();
  if (!accepted?.snapshot) accepted = await recoverLayoutSnapshot();
  if (!accepted?.snapshot) {
    showEmptyState();
    showToast('Accept a layout in Setup first');
    return;
  }

  hideEmptyState();
  if (accepted.footprint) {
    seedColumnCounts(accepted.footprint.w, accepted.footprint.h);
    syncFormFromState();
  }

  try {
    await refreshLayout();
    clearElementReport();
    showToast('Layout step active — preliminary checks ready');
  } catch (e) {
    showToast(e.message);
  }

  requestAnimationFrame(updateHudReserve);
}

init();
