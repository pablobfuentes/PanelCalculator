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
  columnHeight: 2.5,
  columnOverrides: '',
  obstacles: '',
  countsSeeded: false,
};

const state = loadLayoutState();
let accepted = null;
let layoutData = null;
let selectedElementId = null;
let selectedCheckId = null;
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
  document.getElementById('col-height').value = state.columnHeight;
  document.getElementById('col-overrides').value = state.columnOverrides;
  document.getElementById('obstacles').value = state.obstacles;
}

function readFormToState() {
  state.columnCountX = Math.max(2, parseInt(document.getElementById('col-count-x').value, 10) || 2);
  state.columnCountY = Math.max(2, parseInt(document.getElementById('col-count-y').value, 10) || 2);
  state.columnHeight = Math.max(0.1, parseFloat(document.getElementById('col-height').value) || 2.5);
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
    column_height_m: state.columnHeight,
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
  const spanNote = rules.default_column_spacing_m
    ? `max span ${rules.max_recommended_beam_span_m} m (2×${rules.default_column_spacing_m} m − 1), `
    : `max span ${rules.max_recommended_beam_span_m} m, `;
  el.textContent =
    `L/${rules.deflection_limit_denominator} deflection, ` +
    spanNote +
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

function formatCalcValue(value, unit) {
  const n = Number(value);
  if (Number.isNaN(n)) return String(value);
  if (unit === '—') return String(n);
  if (Math.abs(n) >= 1e6) return `${n.toExponential(2)} ${unit}`;
  if (Math.abs(n) >= 100) return `${n.toFixed(1)} ${unit}`;
  if (Math.abs(n) >= 1) return `${n.toFixed(3)} ${unit}`;
  return `${n.toFixed(5)} ${unit}`;
}

function clearCalcDetail() {
  selectedCheckId = null;
  document.getElementById('right-rails')?.classList.remove('calc-open');
  const rail = document.getElementById('calc-rail');
  if (rail) rail.hidden = true;
  document.querySelectorAll('.check-row.selected').forEach((row) => row.classList.remove('selected'));
}

function renderCalcDetail(check) {
  if (!check?.detail) return;

  selectedCheckId = check.check_id;
  document.querySelectorAll('.check-row.selected').forEach((row) => row.classList.remove('selected'));
  const activeRow = document.querySelector(`.check-row[data-check-id="${check.check_id}"]`);
  activeRow?.classList.add('selected');

  const rails = document.getElementById('right-rails');
  const rail = document.getElementById('calc-rail');
  rails.classList.add('calc-open');
  rail.hidden = false;

  document.getElementById('calc-title').textContent = check.label;
  const verdictEl = document.getElementById('calc-verdict');
  verdictEl.textContent = check.detail.verdict;
  verdictEl.className = `calc-verdict ${check.passed ? 'pass' : 'fail'}`;

  document.getElementById('calc-vars').innerHTML = check.detail.variables
    .map(
      (variable) =>
        `<div class="calc-var-row">` +
        `<span class="calc-var-name">${variable.name}<code>${variable.symbol}</code></span>` +
        `<span class="calc-var-val">${formatCalcValue(variable.value, variable.unit)}</span>` +
        `</div>`,
    )
    .join('');

  document.getElementById('calc-steps').innerHTML = check.detail.steps
    .map((step) => {
      const resultClass =
        step.result === 'PASS' ? 'pass' : step.result === 'FAIL' ? 'fail' : '';
      return (
        `<div class="calc-step">` +
        `<div class="calc-step-label">${step.label}</div>` +
        `<div class="calc-step-formula">${step.formula}</div>` +
        `<div class="calc-step-expr">${step.expression}</div>` +
        `<div class="calc-step-result ${resultClass}">${step.result}</div>` +
        `</div>`
      );
    })
    .join('');
}

function clearElementReport() {
  selectedElementId = null;
  clearCalcDetail();
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
  const elementChanged = selectedElementId !== element.element_id;
  const keepCheckId = elementChanged ? null : selectedCheckId;
  if (elementChanged) clearCalcDetail();

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
    positionText =
      `Plan (${element.x.toFixed(2)}, ${element.y.toFixed(2)}) m · ` +
      `Height ${state.columnHeight.toFixed(1)} m`;
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
      .map((check) => {
        const detailClass = check.detail ? ' has-detail' : '';
        const selectedClass = check.check_id === keepCheckId ? ' selected' : '';
        const attrs = check.detail
          ? ` data-check-id="${check.check_id}" role="button" tabindex="0"`
          : '';
        return (
          `<div class="check-row ${check.passed ? 'pass' : 'fail'}${detailClass}${selectedClass}"${attrs}>` +
          `<span class="check-label">${check.label}</span>` +
          `<span class="check-value">${check.value} / ${check.limit} ${check.unit}</span>` +
          `<span class="check-icon ${check.passed ? 'pass' : 'fail'}">${check.passed ? '✓' : '✗'}</span>` +
          `</div>`
        );
      })
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

  if (keepCheckId) {
    const check = element.checks.find((item) => item.check_id === keepCheckId);
    if (check?.detail) renderCalcDetail(check);
  }
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

function escapeHtml(text) {
  const el = document.createElement('div');
  el.textContent = text;
  return el.innerHTML;
}

function collectLayoutWarnings(metrics, elements) {
  const warnings = [];
  if (metrics.parse_error) {
    warnings.push(`Input error: ${metrics.parse_error}`);
  }
  if (!metrics.parse_error && !metrics.partition_ok) {
    const delta = Math.abs(metrics.tributary_area_m2 - metrics.panel_area_m2);
    warnings.push(`Tributary areas do not cover the full panel area (Δ ${delta.toFixed(4)} m²).`);
  }
  for (const element of elements) {
    if (element.overall_pass) continue;
    const failedChecks = element.checks.filter((check) => !check.passed).map((check) => check.label);
    if (failedChecks.length > 0) {
      warnings.push(`${element.name}: ${failedChecks.join('; ')}`);
    } else {
      warnings.push(`${element.name}: preliminary ${element.preliminary_status}`);
    }
  }
  return warnings;
}

function hasLayoutWarnings(metrics, elements) {
  return collectLayoutWarnings(metrics, elements).length > 0;
}

function proceedToStructure() {
  if (layoutData) saveHandoff(layoutData);
  window.location.href = '/structure';
}

function openLayoutWarningModal(warnings) {
  const modal = document.getElementById('layout-warning-modal');
  document.getElementById('layout-warning-list').innerHTML = warnings
    .map((warning) => `<li>${escapeHtml(warning)}</li>`)
    .join('');
  modal.hidden = false;
  requestAnimationFrame(() => modal.classList.add('open'));
  document.getElementById('layout-warning-ok').focus();
}

function closeLayoutWarningModal() {
  const modal = document.getElementById('layout-warning-modal');
  modal.classList.remove('open');
  modal.hidden = true;
}

function updateNextButton(metrics, elements) {
  const btn = document.getElementById('next-btn');
  if (!btn) return;
  btn.disabled = !layoutData;
  btn.classList.toggle('has-warnings', Boolean(metrics && elements && hasLayoutWarnings(metrics, elements)));
}

function handleNextClick() {
  if (!layoutData) return;
  const { metrics, elements } = layoutData;
  const warnings = collectLayoutWarnings(metrics, elements);
  if (warnings.length === 0) {
    proceedToStructure();
    return;
  }
  openLayoutWarningModal(warnings);
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

  updateNextButton(data.metrics, data.elements);

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
  ['col-count-x', 'col-count-y', 'col-height', 'col-overrides', 'obstacles'].forEach((id) => {
    const el = document.getElementById(id);
    el.addEventListener('input', scheduleRefresh);
    el.addEventListener('change', scheduleRefresh);
  });

  document.getElementById('report-close').addEventListener('click', clearElementReport);
  document.getElementById('calc-close').addEventListener('click', clearCalcDetail);

  document.getElementById('report-checks').addEventListener('click', (event) => {
    const row = event.target.closest('.check-row.has-detail');
    if (!row) return;
    const element = findElement(selectedElementId);
    const check = element?.checks?.find((item) => item.check_id === row.dataset.checkId);
    if (check?.detail) renderCalcDetail(check);
  });

  document.getElementById('report-checks').addEventListener('keydown', (event) => {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    const row = event.target.closest('.check-row.has-detail');
    if (!row) return;
    event.preventDefault();
    const element = findElement(selectedElementId);
    const check = element?.checks?.find((item) => item.check_id === row.dataset.checkId);
    if (check?.detail) renderCalcDetail(check);
  });

  document.getElementById('next-btn').addEventListener('click', handleNextClick);

  document.getElementById('layout-warning-ok').addEventListener('click', () => {
    closeLayoutWarningModal();
    proceedToStructure();
  });

  document.getElementById('layout-warning-modal').addEventListener('click', (event) => {
    if (event.target.id === 'layout-warning-modal') closeLayoutWarningModal();
  });

  document.addEventListener('keydown', (event) => {
    const modal = document.getElementById('layout-warning-modal');
    if (!modal?.classList.contains('open')) return;
    if (event.key === 'Escape') closeLayoutWarningModal();
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
