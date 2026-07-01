/**
 * SolarForge Setup — HTML canvas UI backed by Python layout API.
 */

import { drawTipAlleyW, drawTipGap, drawTipReach, drawTipSpine, refreshTooltips } from './tooltips.js';

const STORAGE_KEY = 'solarforge.setup.v1';

const PANEL_KEYS = 'ABCDEFGH'.split('');
const DEFAULT_COLORS = ['#E74C3C', '#9B59B6', '#F39C12', '#1ABC9C', '#E91E63'];

const DEFAULT_STATE = {
  panelKey: 'A',
  catalog: [],
  customPanels: [],
  maxAreaX: 12,
  maxAreaY: 8,
  gap: 1,
  reach: 2,
  alleyW: 1,
  spineEdge: 'bottom',
  locked: false,
  lockedCount: 0,
};

const state = loadState();
let layoutData = null;
let viewTransform = null;
let fetchTimer = null;
let countRefreshTimer = null;

const canvas = document.getElementById('solarCanvas');
const ctx = canvas.getContext('2d');
const wrap = document.querySelector('.canvas-wrap');
const dimW = document.getElementById('dim-w');
const dimH = document.getElementById('dim-h');
const toastEl = document.getElementById('toast');

const PANEL_STROKE = {};

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return { ...DEFAULT_STATE, ...JSON.parse(raw) };
  } catch (_) {
    /* ignore */
  }
  return { ...DEFAULT_STATE };
}

function saveState() {
  const { customPanels, panelKey, maxAreaX, maxAreaY, gap, reach, alleyW, spineEdge, locked, lockedCount } = state;
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({ customPanels, panelKey, maxAreaX, maxAreaY, gap, reach, alleyW, spineEdge, locked, lockedCount }),
  );
}

function showToast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.add('show');
  setTimeout(() => toastEl.classList.remove('show'), 2400);
}

function lighten(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgb(${Math.min(255, r + 60)},${Math.min(255, g + 60)},${Math.min(255, b + 60)})`;
}

function mergeCustomPanels() {
  const custom = state.customPanels || [];
  custom.forEach((p) => {
    if (!state.catalog.some((c) => c.key === p.key)) {
      state.catalog.push({ ...p });
    }
  });
}

function selectedPanel() {
  mergeCustomPanels();
  return state.catalog.find((p) => p.key === state.panelKey) ?? null;
}

function panelPayload(panel) {
  return {
    key: panel.key,
    name: panel.name,
    length: panel.length,
    width: panel.width,
    weight: panel.weight,
    watt_peak: panel.watt_peak ?? 0,
    color: panel.color,
    tilt_angle: panel.tilt_angle ?? 10,
  };
}

function buildRequestBody() {
  const panel = selectedPanel();
  if (!panel) {
    throw new Error(`Panel type "${state.panelKey}" is not available`);
  }
  return {
    panel_key: panel.key,
    panel: panelPayload(panel),
    max_area_x: state.maxAreaX,
    max_area_y: state.maxAreaY,
    mid_clamp_in: state.gap,
    alley_width: state.alleyW,
    alley_reach: state.reach,
    spine_edge: state.spineEdge,
    use_fit: !state.locked,
    panels_locked: state.locked,
    target_panels: state.locked ? state.lockedCount : 0,
    num_pairs_manual: 3,
    num_rows_manual: 2,
  };
}

async function fetchLayout() {
  const res = await fetch('/api/layout', {
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

async function loadCatalog() {
  const res = await fetch('/api/catalog');
  if (!res.ok) throw new Error('Failed to load panel catalog');
  const defaults = await res.json();
  const custom = state.customPanels || [];
  const keys = new Set(defaults.map((p) => p.key));
  state.catalog = [...defaults, ...custom.filter((p) => !keys.has(p.key))];
  if (!state.catalog.some((p) => p.key === state.panelKey)) {
    state.panelKey = state.catalog[0]?.key || 'A';
  }
}

function renderPanelTypeRow() {
  const row = document.getElementById('panel-type-row');
  row.innerHTML = '';
  state.catalog.forEach((panel) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = `panel-type-btn${panel.key === state.panelKey ? ' active' : ''}`;
    btn.id = `btn-${panel.key}`;
    btn.textContent = panel.key;
    btn.title = panel.name;
    btn.style.background = `${panel.color}33`;
    btn.style.borderColor = panel.color;
    btn.style.color = panel.color;
    btn.addEventListener('click', () => selectPanel(panel.key));
    row.appendChild(btn);
  });

  const addBtn = document.createElement('button');
  addBtn.type = 'button';
  addBtn.className = 'panel-type-btn add-btn';
  addBtn.title = 'Add panel type';
  addBtn.textContent = '+';
  addBtn.addEventListener('click', openModal);
  row.appendChild(addBtn);
}

function updateSelectedPanelCard(panel) {
  document.getElementById('panel-name').textContent = panel.name;
  document.getElementById('panel-name').style.color = panel.color;
  document.getElementById('p-length').textContent = `${panel.length.toFixed(1)} m`;
  document.getElementById('p-width').textContent = `${panel.width.toFixed(1)} m`;
  document.getElementById('p-weight').textContent = `${panel.weight.toFixed(0)} kg`;
  document.getElementById('p-wp').textContent = `${panel.watt_peak.toFixed(0)} Wp`;
  const icon = document.getElementById('panel-icon');
  icon.style.background = `${panel.color}33`;
  icon.style.borderColor = `${panel.color}88`;
  icon.style.color = panel.color;
  PANEL_STROKE[panel.key] = lighten(panel.color);
}

function selectPanel(key) {
  state.panelKey = key;
  mergeCustomPanels();
  saveState();
  renderPanelTypeRow();
  scheduleRefresh();
}

/** Map layout coords (origin bottom-left, y up) to canvas pixels. */
function makeViewTransform(axisX, axisY, canvasW, canvasH) {
  const margin = 28;
  const innerW = canvasW - margin * 2;
  const innerH = canvasH - margin * 2;
  const dataAspect = axisX / axisY;
  const plotAspect = innerW / innerH;
  let usedW;
  let usedH;
  let padX;
  let padY;
  if (dataAspect > plotAspect) {
    usedW = innerW;
    usedH = innerW / dataAspect;
    padX = 0;
    padY = (innerH - usedH) / 2;
  } else {
    usedH = innerH;
    usedW = innerH * dataAspect;
    padX = (innerW - usedW) / 2;
    padY = 0;
  }
  const scale = usedW / axisX;
  const originX = margin + padX;
  const originY = margin + padY;

  function toCanvasRaw(rect) {
    const { x, y, w, h } = rect;
    return {
      x: originX + x * scale,
      y: originY + (axisY - y - h) * scale,
      w: w * scale,
      h: h * scale,
    };
  }

  function toCanvas(rect) {
    let { x, y, w, h } = rect;
    if (state.spineEdge === 'top') {
      y = axisY - y - h;
    }
    return toCanvasRaw({ x, y, w, h });
  }

  return { scale, originX, originY, usedW, usedH, axisX, axisY, toCanvas, toCanvasRaw };
}

function drawDashedRect(px, color = 'rgba(122, 132, 153, 0.55)') {
  ctx.save();
  ctx.strokeStyle = color;
  ctx.lineWidth = 1;
  ctx.setLineDash([5, 4]);
  ctx.strokeRect(px.x, px.y, px.w, px.h);
  ctx.restore();
}

function drawRoundRect(x, y, w, h, r, fill, stroke) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, r);
  if (fill) {
    ctx.fillStyle = fill;
    ctx.fill();
  }
  if (stroke) {
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 1;
    ctx.stroke();
  }
}

function alleyLabelFont(alley, px, scale) {
  const fromScale = Math.max(7, 8 * (scale / 12));
  const dim = Math.min(px.w, px.h);
  if (alley.kind === 'spine') {
    const size = Math.min(10, Math.max(7, Math.min(fromScale, px.h * 0.32)));
    return `700 ${size}px Rajdhani`;
  }
  const size = Math.min(9, Math.max(6, Math.min(fromScale, dim * 0.55)));
  return `700 ${size}px Rajdhani`;
}

function drawAlleyLabel(alley, px, scale) {
  if (!alley.label || px.w < 8 || px.h < 8) return;
  ctx.save();
  ctx.font = alleyLabelFont(alley, px, scale);
  ctx.fillStyle = 'rgba(245,163,35,0.9)';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  if (alley.kind === 'parallel' && px.h > px.w) {
    ctx.translate(px.x + px.w / 2, px.y + px.h / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText(alley.label, 0, 0);
  } else if (alley.kind === 'spine' && px.w < 90) {
    ctx.fillText('SPINE', px.x + px.w / 2, px.y + px.h / 2);
  } else {
    ctx.fillText(alley.label, px.x + px.w / 2, px.y + px.h / 2);
  }
  ctx.restore();
}

function drawLayout(data) {
  layoutData = data;
  resizeCanvas();
  const { axis, panel, stats } = data;
  viewTransform = makeViewTransform(axis.w, axis.h, canvas.width, canvas.height);

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const maxPx = viewTransform.toCanvasRaw(data.max_area);
  drawDashedRect(maxPx);

  const panelFill = panel.color;
  const panelStroke = PANEL_STROKE[panel.key] || lighten(panel.color);

  data.alleys.forEach((alley) => {
    const px = viewTransform.toCanvas(alley);
    drawRoundRect(px.x, px.y, px.w, px.h, 3, 'rgba(245,163,35,0.55)', '#F5A623');
    drawAlleyLabel(alley, px, viewTransform.scale);
  });

  data.panels.forEach((rect) => {
    const px = viewTransform.toCanvas(rect);
    drawRoundRect(px.x, px.y, px.w, px.h, 2, panelFill, panelStroke);
  });

  syncCountUI(stats);
  document.getElementById('area-val').textContent = `${stats.footprint_w.toFixed(1)} × ${stats.footprint_h.toFixed(1)} m`;
  document.getElementById('area-sub').textContent = `${stats.footprint_area.toFixed(1)} m²`;

  document.getElementById('proceed-btn').disabled = !stats.fits;
  positionDimBubbles(maxPx);

  let warning = wrap.querySelector('.layout-warning');
  if (!warning) {
    warning = document.createElement('div');
    warning.className = 'layout-warning';
    wrap.appendChild(warning);
  }
  if (!stats.fits && stats.message) {
    warning.textContent = stats.message;
    warning.classList.add('visible');
  } else {
    warning.classList.remove('visible');
  }
}

function positionDimBubbles(maxPx) {
  const wrapRect = wrap.getBoundingClientRect();
  const canvasRect = canvas.getBoundingClientRect();

  const topCenterX = canvasRect.left - wrapRect.left + maxPx.x + maxPx.w / 2;
  const topY = canvasRect.top - wrapRect.top + maxPx.y;

  dimW.style.left = `${topCenterX}px`;
  dimW.style.top = `${topY}px`;
  dimW.style.transform = 'translate(-50%, calc(-100% - 8px))';

  const rightX = canvasRect.left - wrapRect.left + maxPx.x + maxPx.w;
  const rightCenterY = canvasRect.top - wrapRect.top + maxPx.y + maxPx.h / 2;

  dimH.style.left = `${rightX}px`;
  dimH.style.top = `${rightCenterY}px`;
  dimH.style.transform = 'translate(8px, -50%)';
}

function updateHudReserve() {
  const hud = document.querySelector('.hud');
  if (!hud) return;
  const bottomGap = 20;
  const reserve = Math.ceil(hud.getBoundingClientRect().height + bottomGap + 24);
  document.documentElement.style.setProperty('--hud-reserve', `${reserve}px`);
}

function resizeCanvas() {
  const rect = wrap.getBoundingClientRect();
  const w = Math.max(320, Math.floor(rect.width));
  const h = Math.max(240, Math.floor(rect.height));
  if (canvas.width !== w || canvas.height !== h) {
    canvas.width = w;
    canvas.height = h;
  }
}

async function refreshLayout() {
  try {
    const data = await fetchLayout();
    updateSelectedPanelCard(data.panel);
    drawLayout(data);
  } catch (err) {
    showToast(String(err.message || err));
  }
}

function normalizeLockedCount(n) {
  let value = Math.max(2, Math.round(Number(n) || 2));
  if (value % 2 !== 0) value += 1;
  return value;
}

function commitLockedCount(raw, inputEl) {
  const parsed = String(raw ?? '').trim();
  state.lockedCount = normalizeLockedCount(parsed === '' ? state.lockedCount || 2 : parsed);
  if (inputEl) inputEl.value = String(state.lockedCount);
  saveState();
  scheduleRefresh();
}

function syncCountUI(stats) {
  const display = document.getElementById('panel-count');
  const input = document.getElementById('panel-count-input');
  const label = document.getElementById('count-label');
  const lockBtn = document.getElementById('lock-btn');

  lockBtn.classList.toggle('locked', state.locked);
  lockBtn.textContent = state.locked ? '🔒' : '🔓';
  lockBtn.title = state.locked ? 'Unlock panel count' : 'Lock panel count';

  if (state.locked) {
    display.hidden = true;
    input.hidden = false;
    if (!state.lockedCount && stats) {
      state.lockedCount = stats.panel_count;
    }
    if (document.activeElement !== input) {
      input.value = String(normalizeLockedCount(state.lockedCount));
    }
    label.textContent = 'panels locked';
  } else {
    display.hidden = false;
    input.hidden = true;
    if (stats) display.textContent = String(stats.panel_count);
    label.textContent = 'panels fit';
  }
}

function scheduleRefresh() {
  clearTimeout(fetchTimer);
  fetchTimer = setTimeout(refreshLayout, 120);
}

function syncHudDisplays() {
  document.getElementById('val-gap').textContent = String(state.gap);
  document.getElementById('val-reach').textContent = String(state.reach);
  document.getElementById('val-alleyW').textContent = state.alleyW.toFixed(1);
  document.getElementById('spine-btn').textContent = state.spineEdge.toUpperCase();
  document.getElementById('input-w').value = String(state.maxAreaX);
  document.getElementById('input-h').value = String(state.maxAreaY);
  syncCountUI(layoutData?.stats);
  refreshTooltips(state);
}

function adjust(field, delta) {
  if (field === 'gap') {
    state.gap = Math.max(0, Math.min(4, Math.round((state.gap + delta * 0.25) * 4) / 4));
  } else if (field === 'reach') {
    state.reach = Math.max(2, Math.min(4, state.reach + delta));
  } else if (field === 'alleyW') {
    state.alleyW = Math.max(0.1, Math.min(3, Math.round((state.alleyW + delta * 0.1) * 10) / 10));
  }
  saveState();
  syncHudDisplays();
  scheduleRefresh();
}

let modalColor = DEFAULT_COLORS[0];

function openModal() {
  document.getElementById('modal').classList.add('open');
}

function closeModal() {
  document.getElementById('modal').classList.remove('open');
}

function pickColor(el) {
  document.querySelectorAll('.color-swatch').forEach((s) => s.classList.remove('selected'));
  el.classList.add('selected');
  modalColor = el.dataset.color;
}

function addPanel() {
  const used = new Set(state.catalog.map((p) => p.key));
  const key = PANEL_KEYS.find((k) => !used.has(k));
  if (!key) {
    showToast('Maximum panel types reached');
    return;
  }

  const name = document.getElementById('modal-name').value.trim() || `Panel ${key}`;
  const length = parseFloat(document.getElementById('modal-len').value) || 2.0;
  const width = parseFloat(document.getElementById('modal-wid').value) || 1.0;
  const weight = parseFloat(document.getElementById('modal-kg').value) || 20;
  const watt_peak = parseFloat(document.getElementById('modal-wp').value) || 400;

  const panel = { key, name, length, width, weight, watt_peak, color: modalColor, tilt_angle: 10 };
  if (!state.customPanels) state.customPanels = [];
  state.customPanels.push(panel);
  mergeCustomPanels();
  state.panelKey = key;
  saveState();
  closeModal();
  renderPanelTypeRow();
  scheduleRefresh();
  showToast(`Added ${name}`);
}

function bindEvents() {
  document.querySelectorAll('[data-adj]').forEach((btn) => {
    btn.addEventListener('click', () => {
      adjust(btn.dataset.adj, Number(btn.dataset.delta));
    });
  });

  document.getElementById('spine-btn').addEventListener('click', () => {
    state.spineEdge = state.spineEdge === 'bottom' ? 'top' : 'bottom';
    saveState();
    syncHudDisplays();
    scheduleRefresh();
  });

  document.getElementById('lock-btn').addEventListener('click', () => {
    state.locked = !state.locked;
    if (state.locked) {
      const fitCount = layoutData?.stats?.panel_count ?? normalizeLockedCount(state.lockedCount);
      state.lockedCount = normalizeLockedCount(fitCount);
      saveState();
      syncCountUI(layoutData?.stats);
      scheduleRefresh();
      showToast('Panel count locked');
    } else {
      saveState();
      syncCountUI(layoutData?.stats);
      scheduleRefresh();
      showToast('Panel count unlocked');
    }
  });

  document.getElementById('panel-count-input').addEventListener('focus', (e) => {
    e.target.select();
  });

  document.getElementById('panel-count-input').addEventListener('input', (e) => {
    if (!state.locked) return;
    const raw = e.target.value.trim();
    if (raw === '') return;
    const n = parseInt(raw, 10);
    if (Number.isNaN(n)) return;
    state.lockedCount = n;
    clearTimeout(countRefreshTimer);
    countRefreshTimer = setTimeout(() => commitLockedCount(state.lockedCount, null), 450);
  });

  document.getElementById('panel-count-input').addEventListener('blur', (e) => {
    if (!state.locked) return;
    clearTimeout(countRefreshTimer);
    commitLockedCount(e.target.value, e.target);
  });

  document.getElementById('panel-count-input').addEventListener('keydown', (e) => {
    if (!state.locked) return;
    if (e.key === 'Enter') {
      e.preventDefault();
      clearTimeout(countRefreshTimer);
      commitLockedCount(e.target.value, e.target);
      e.target.blur();
    }
  });

  document.getElementById('input-w').addEventListener('input', (e) => {
    state.maxAreaX = Math.max(1, parseFloat(e.target.value) || state.maxAreaX);
    saveState();
    scheduleRefresh();
  });

  document.getElementById('input-h').addEventListener('input', (e) => {
    state.maxAreaY = Math.max(1, parseFloat(e.target.value) || state.maxAreaY);
    saveState();
    scheduleRefresh();
  });

  document.getElementById('proceed-btn').addEventListener('click', () => {
    if (!layoutData?.stats.fits) {
      showToast('Fix the layout before continuing');
      return;
    }
    if (!layoutData.snapshot) {
      showToast('Layout snapshot missing — refresh and try again');
      return;
    }
    const payload = {
      snapshot: layoutData.snapshot,
      panels_locked: state.locked,
      locked_panel_count: state.locked ? state.lockedCount : 0,
      footprint: {
        w: layoutData.stats.footprint_w,
        h: layoutData.stats.footprint_h,
      },
    };
    localStorage.setItem('solarforge.setup.snapshot.v1', JSON.stringify(payload));
    window.location.href = '/layout';
  });

  document.getElementById('modal-cancel').addEventListener('click', closeModal);
  document.getElementById('modal-add').addEventListener('click', addPanel);
  document.getElementById('modal').addEventListener('click', (e) => {
    if (e.target.id === 'modal') closeModal();
  });
  document.querySelectorAll('.color-swatch').forEach((swatch) => {
    swatch.addEventListener('click', () => pickColor(swatch));
  });

  window.addEventListener('resize', () => {
    updateHudReserve();
    if (layoutData) drawLayout(layoutData);
  });
}

async function init() {
  bindEvents();
  updateHudReserve();
  await loadCatalog();
  renderPanelTypeRow();
  syncHudDisplays();
  await refreshLayout();
}

init();
