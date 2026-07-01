/**
 * SolarForge Structure — tributary canvas, BOM, FEA (Plotly + API).
 */

const SNAPSHOT_KEY = 'solarforge.setup.snapshot.v1';
const SETUP_KEY = 'solarforge.setup.v1';
const STRUCTURE_KEY = 'solarforge.structure.v1';
const DEFAULT_SPACING_M = 3.5;

const EXPOSURE_HINTS = {
  A: 'Dense urban centers; buildings mostly > 15 m.',
  B: 'Urban, suburban, or wooded terrain.',
  C: 'Open country with scattered obstructions.',
  D: 'Flat unobstructed coastal exposure.',
};

const DEFAULT_STATE = {
  columnCountX: 2,
  columnCountY: 2,
  columnHeight: 2.5,
  windSpeed: 120,
  windExposure: 'B',
  columnOverrides: '',
  obstacles: '',
  countsSeeded: false,
};

const state = loadStructureState();
let accepted = null;
let fetchTimer = null;
const toastEl = document.getElementById('toast');

function loadStructureState() {
  try {
    const raw = localStorage.getItem(STRUCTURE_KEY);
    if (raw) return { ...DEFAULT_STATE, ...JSON.parse(raw) };
  } catch (_) {
    /* ignore */
  }
  return { ...DEFAULT_STATE };
}

function saveStructureState() {
  localStorage.setItem(STRUCTURE_KEY, JSON.stringify(state));
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
      footprint: {
        w: layout.stats.footprint_w,
        h: layout.stats.footprint_h,
      },
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
  saveStructureState();
}

function syncFormFromState() {
  document.getElementById('wind-speed').value = state.windSpeed;
  document.getElementById('wind-exposure').value = state.windExposure;
  document.getElementById('col-height').value = state.columnHeight;
  document.getElementById('col-count-x').value = state.columnCountX;
  document.getElementById('col-count-y').value = state.columnCountY;
  document.getElementById('col-overrides').value = state.columnOverrides;
  document.getElementById('obstacles').value = state.obstacles;
  document.getElementById('exposure-hint').textContent =
    EXPOSURE_HINTS[state.windExposure] || '';
}

function readFormToState() {
  state.windSpeed = Math.max(1, parseFloat(document.getElementById('wind-speed').value) || 120);
  state.windExposure = document.getElementById('wind-exposure').value;
  state.columnHeight = Math.max(0.1, parseFloat(document.getElementById('col-height').value) || 2.5);
  state.columnCountX = Math.max(2, parseInt(document.getElementById('col-count-x').value, 10) || 2);
  state.columnCountY = Math.max(2, parseInt(document.getElementById('col-count-y').value, 10) || 2);
  state.columnOverrides = document.getElementById('col-overrides').value;
  state.obstacles = document.getElementById('obstacles').value;
  saveStructureState();
}

function buildRequestBody() {
  if (!accepted?.snapshot) throw new Error('No accepted layout');
  return {
    snapshot: accepted.snapshot,
    column_count_x: state.columnCountX,
    column_count_y: state.columnCountY,
    column_height_m: state.columnHeight,
    wind_speed_kmh: state.windSpeed,
    wind_exposure: state.windExposure,
    column_overrides: state.columnOverrides,
    obstacle_zones: state.obstacles,
    panels_locked: Boolean(accepted.panels_locked),
    locked_panel_count: accepted.locked_panel_count || 0,
  };
}

async function fetchStructure() {
  const res = await fetch('/api/structure', {
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
  fetchTimer = setTimeout(() => refreshStructure().catch((e) => showToast(e.message)), 350);
}

function renderPlotly(figure) {
  const host = document.getElementById('plotly-chart');
  const layout = {
    ...figure.layout,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    autosize: true,
    margin: figure.layout?.margin || { l: 24, r: 24, t: 24, b: 24 },
  };
  Plotly.react(host, figure.data, layout, {
    responsive: true,
    displayModeBar: false,
    scrollZoom: true,
  });
}

function renderBom(bom) {
  document.getElementById('bom-panels').textContent = String(bom.panel_count);
  const colLabel =
    bom.column_count !== bom.active_column_count
      ? `${bom.active_column_count} (${bom.column_count} total)`
      : String(bom.active_column_count);
  document.getElementById('bom-columns').textContent = colLabel;
  document.getElementById('bom-ptr').textContent = `${bom.ptr_total_length_m.toFixed(1)} m`;
  document.getElementById('bom-chords').textContent = `${bom.truss_chord_length_m.toFixed(1)} m`;
  document.getElementById('bom-plates').textContent = String(bom.base_plate_count);
  document.getElementById('bom-steel').textContent = `${bom.steel_tonnage.toFixed(2)} t`;
}

function renderMetrics(m) {
  document.getElementById('spacing-x').textContent = `${m.spacing_x.toFixed(2)} m spacing`;
  document.getElementById('spacing-y').textContent = `${m.spacing_y.toFixed(2)} m spacing`;
  document.getElementById('m-columns').textContent = String(m.column_count);
  document.getElementById('m-active').textContent = String(m.active_count);
  document.getElementById('m-panel-area').textContent = `${m.panel_area_m2.toFixed(2)} m²`;
  document.getElementById('m-trib-area').textContent = `${m.tributary_area_m2.toFixed(2)} m²`;
  document.getElementById('m-load').textContent = `${m.estimated_load_kn.toFixed(2)} kN`;

  const partEl = document.getElementById('m-partition');
  if (m.parse_error) {
    partEl.textContent = 'ERR';
    partEl.className = 'hud-metric-val fail';
  } else {
    partEl.textContent = m.partition_ok ? 'PASS' : 'FAIL';
    partEl.className = `hud-metric-val ${m.partition_ok ? 'ok' : 'fail'}`;
  }

  const banner = document.getElementById('partition-banner');
  const msg = document.getElementById('partition-msg');
  if (m.parse_error) {
    banner.hidden = false;
    banner.className = 'panel-section partition-banner fail';
    msg.textContent = m.parse_error;
  } else if (m.partition_ok) {
    banner.hidden = false;
    banner.className = 'panel-section partition-banner ok';
    msg.textContent = 'Active tributary zones cover the full panel area.';
  } else {
    banner.hidden = false;
    banner.className = 'panel-section partition-banner fail';
    const delta = Math.abs(m.tributary_area_m2 - m.panel_area_m2);
    msg.textContent = `Tributary areas do not match panel area (Δ ${delta.toFixed(4)} m²).`;
  }
}

function renderTable(containerId, columns, rows, statusKey) {
  const wrap = document.getElementById(containerId);
  if (!rows.length) {
    wrap.innerHTML = '<p class="table-placeholder">No data.</p>';
    return;
  }
  const thead = columns.map((c) => `<th>${c.label}</th>`).join('');
  const tbody = rows
    .map((row) => {
      const status = statusKey ? row[statusKey] : null;
      const cls = status ? ` class="status-${String(status).toLowerCase()}"` : '';
      const cells = columns.map((c) => `<td>${row[c.key] ?? ''}</td>`).join('');
      return `<tr${cls}>${cells}</tr>`;
    })
    .join('');
  wrap.innerHTML = `<table class="data-table"><thead><tr>${thead}</tr></thead><tbody>${tbody}</tbody></table>`;
}

function renderColumnsTable(columns) {
  renderTable(
    'columns-table-wrap',
    [
      { key: 'Column', label: 'Column' },
      { key: 'X (m)', label: 'X (m)' },
      { key: 'Y (m)', label: 'Y (m)' },
      { key: 'Custom', label: 'Custom' },
      { key: 'Excluded', label: 'Excluded' },
      { key: 'Area (m²)', label: 'Area (m²)' },
      { key: 'Est. load (kN)', label: 'Est. load (kN)' },
    ],
    columns.map((c) => ({
      Column: c.column_id,
      'X (m)': c.x.toFixed(3),
      'Y (m)': c.y.toFixed(3),
      Custom: c.is_custom ? 'Yes' : '',
      Excluded: c.excluded ? 'Yes' : '',
      'Area (m²)': c.tributary_area_m2.toFixed(3),
      'Est. load (kN)': c.estimated_load_kn.toFixed(3),
    })),
  );
}

function renderFeaTable(fea) {
  const wrap = document.getElementById('fea-table-wrap');
  if (!fea) {
    wrap.innerHTML = '<p class="table-placeholder">Fix tributary partition to run FEA.</p>';
    return;
  }
  if (!fea.solved) {
    wrap.innerHTML = `<p class="table-placeholder">${fea.error || 'FEA solver failed.'}</p>`;
    return;
  }
  renderTable(
    'fea-table-wrap',
    [
      { key: 'Element', label: 'Element' },
      { key: 'Type', label: 'Type' },
      { key: 'Combo', label: 'Combo' },
      { key: 'M max (kN·m)', label: 'M max (kN·m)' },
      { key: 'P max (kN)', label: 'P max (kN)' },
      { key: 'δ max (m)', label: 'δ max (m)' },
    ],
    fea.rows,
  );
}

function renderCodeChecks(checks) {
  const summary = document.getElementById('code-summary');
  const wrap = document.getElementById('checks-table-wrap');
  if (!checks || !checks.rows.length) {
    summary.hidden = true;
    wrap.innerHTML = '<p class="table-placeholder">Code checks appear after a successful FEA solve.</p>';
    return;
  }
  summary.hidden = false;
  document.getElementById('code-pass').textContent = `PASS ${checks.pass_count}`;
  document.getElementById('code-warn').textContent = `WARN ${checks.warn_count}`;
  document.getElementById('code-fail').textContent = `FAIL ${checks.fail_count}`;
  renderTable(
    'checks-table-wrap',
    [
      { key: 'Element', label: 'Element' },
      { key: 'Type', label: 'Type' },
      { key: 'Combo', label: 'Combo' },
      { key: 'Utilization', label: 'Utilization' },
      { key: 'Governs', label: 'Governs' },
      { key: 'Status', label: 'Status' },
    ],
    checks.rows,
    'Status',
  );
}

async function refreshStructure(reseedAttempt = false) {
  readFormToState();
  const data = await fetchStructure();

  if (!state.countsSeeded && !reseedAttempt) {
    seedColumnCounts(data.metrics.field_width, data.metrics.field_height);
    document.getElementById('col-count-x').value = state.columnCountX;
    document.getElementById('col-count-y').value = state.columnCountY;
    saveStructureState();
    return refreshStructure(true);
  }

  hideEmptyState();
  renderPlotly(data.figure);
  renderBom(data.bom);
  renderMetrics(data.metrics);
  renderColumnsTable(data.columns);
  renderFeaTable(data.fea);
  renderCodeChecks(data.code_checks);

  document.getElementById('next-btn').disabled = !data.metrics.partition_ok;
}

function bindEvents() {
  const inputs = [
    'wind-speed',
    'wind-exposure',
    'col-height',
    'col-count-x',
    'col-count-y',
    'col-overrides',
    'obstacles',
  ];
  inputs.forEach((id) => {
    const el = document.getElementById(id);
    el.addEventListener('input', scheduleRefresh);
    el.addEventListener('change', scheduleRefresh);
  });

  document.getElementById('wind-exposure').addEventListener('change', (e) => {
    document.getElementById('exposure-hint').textContent = EXPOSURE_HINTS[e.target.value] || '';
  });

  document.getElementById('next-btn').addEventListener('click', () => {
    showToast('Materials step coming soon');
  });

  window.addEventListener('resize', () => {
    const host = document.getElementById('plotly-chart');
    if (host?.data) Plotly.Plots.resize(host);
  });
}

function updateHudReserve() {
  const hud = document.querySelector('.structure-hud');
  if (!hud) return;
  const h = Math.ceil(hud.getBoundingClientRect().height);
  document.documentElement.style.setProperty('--hud-reserve', `${Math.max(96, h + 16)}px`);
}

async function init() {
  bindEvents();
  syncFormFromState();
  updateHudReserve();

  accepted = loadAcceptedLayout();
  if (!accepted?.snapshot) {
    accepted = await recoverLayoutSnapshot();
  }
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
    await refreshStructure();
    showToast('Layout accepted — Structure is now active');
  } catch (e) {
    showToast(e.message);
  }

  requestAnimationFrame(updateHudReserve);
}

init();
