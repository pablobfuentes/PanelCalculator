/** HUD tooltip mini-canvas previews. */

const ALLEY_COLOR = 'rgba(245,163,35,0.65)';

export function drawTipGap(canvasEl, gapIn) {
  const x = canvasEl.getContext('2d');
  canvasEl.width = 120;
  canvasEl.height = 80;
  x.fillStyle = '#1E2640';
  x.fillRect(0, 0, 120, 80);
  x.fillStyle = '#3B7DD8';
  x.fillRect(10, 15, 40, 50);
  x.fillStyle = '#3B7DD8';
  x.fillRect(70, 15, 40, 50);
  const gapPx = Math.max(2, gapIn * 6);
  x.fillStyle = 'rgba(255,193,7,0.8)';
  x.fillRect(50, 15, gapPx, 50);
  x.strokeStyle = '#F5A623';
  x.lineWidth = 1.5;
  x.beginPath();
  x.moveTo(50, 8);
  x.lineTo(50 + gapPx, 8);
  x.stroke();
  x.fillStyle = '#F5A623';
  x.font = '9px Inter';
  x.textAlign = 'center';
  x.fillText(`${gapIn}"`, 50 + gapPx / 2, 7);
}

export function drawTipReach(canvasEl, reach) {
  const x = canvasEl.getContext('2d');
  canvasEl.width = 120;
  canvasEl.height = 80;
  x.fillStyle = '#1E2640';
  x.fillRect(0, 0, 120, 80);
  const pw = 10;
  const aw = 8;
  const totalPanels = reach * 2;
  const totalW = totalPanels * pw + aw;
  const startX = (120 - totalW) / 2;
  x.fillStyle = 'rgba(91,184,245,0.12)';
  x.fillRect(startX, 10, totalW, 60);
  for (let i = 0; i < totalPanels; i += 1) {
    const px = startX + i * pw + (i >= reach ? aw : 0);
    x.fillStyle = i < reach ? 'rgba(59,125,216,0.9)' : 'rgba(59,125,216,0.5)';
    x.fillRect(px + 1, 15, pw - 2, 50);
  }
  x.fillStyle = ALLEY_COLOR;
  x.fillRect(startX + reach * pw, 15, aw, 50);
  x.strokeStyle = '#5BB8F5';
  x.lineWidth = 1;
  x.beginPath();
  x.moveTo(startX, 8);
  x.lineTo(startX + reach * pw, 8);
  x.stroke();
  x.fillStyle = '#5BB8F5';
  x.font = '8px Inter';
  x.textAlign = 'center';
  x.fillText(`≤${reach}`, startX + (reach * pw) / 2, 7);
}

export function drawTipAlleyW(canvasEl, alleyW) {
  const x = canvasEl.getContext('2d');
  canvasEl.width = 120;
  canvasEl.height = 80;
  x.fillStyle = '#1E2640';
  x.fillRect(0, 0, 120, 80);
  x.fillStyle = '#3B7DD8';
  x.fillRect(10, 15, 35, 50);
  x.fillStyle = '#3B7DD8';
  x.fillRect(75, 15, 35, 50);
  const aw = Math.max(6, alleyW * 20);
  x.fillStyle = ALLEY_COLOR;
  x.fillRect(45, 15, aw, 50);
  x.strokeStyle = '#F5A623';
  x.lineWidth = 1;
  x.beginPath();
  x.moveTo(45, 8);
  x.lineTo(45 + aw, 8);
  x.stroke();
  x.fillStyle = '#F5A623';
  x.font = '9px Inter';
  x.textAlign = 'center';
  x.fillText(`${alleyW}m`, 45 + aw / 2, 7);
}

export function drawTipSpine(canvasEl, spineEdge) {
  const x = canvasEl.getContext('2d');
  canvasEl.width = 120;
  canvasEl.height = 80;
  x.fillStyle = '#1E2640';
  x.fillRect(0, 0, 120, 80);
  x.fillStyle = '#3B7DD8';
  x.fillRect(15, 20, 90, 45);
  const sy = spineEdge === 'top' ? 18 : 62;
  x.fillStyle = ALLEY_COLOR;
  x.fillRect(15, sy, 90, 10);
  x.fillStyle = '#F5A623';
  x.font = '8px Rajdhani';
  x.textAlign = 'center';
  x.fillText('SPINE', 60, sy + 7);
}

export function refreshTooltips(state) {
  drawTipGap(document.getElementById('tip-gap'), state.gap);
  drawTipReach(document.getElementById('tip-reach'), state.reach);
  drawTipAlleyW(document.getElementById('tip-alleyW'), state.alleyW);
  drawTipSpine(document.getElementById('tip-spine'), state.spineEdge);
}
