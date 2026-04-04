/**
 * EcoHandel Econtrol Room — Shared API Client
 * All pages use this to call the Flask backend with Basic Auth.
 * Auto-refreshes every 5 minutes and shows "last updated" timestamp.
 */
const API_BASE = '/api/v1';
const AUTH_USER = 'milan';
const AUTH_PASS = 'ecohandel2026';
const REFRESH_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes
const LOG_PREFIX = '[EcontrolRoom]';

let _lastUpdated = null;
let _refreshTimer = null;
let _onRefresh = null;

/** Build Basic Auth header */
function apiAuthHeader() {
  const creds = btoa(`${AUTH_USER}:${AUTH_PASS}`);
  return `Basic ${creds}`;
}

/** Fetch JSON from API with auth, returns {ok, data} or throws */
async function apiFetch(path) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { Authorization: apiAuthHeader() }
  });
  const json = await res.json();
  if (!json.ok) {
    throw new Error(json.error?.message || `API error on ${path}`);
  }
  return json.data;
}

/** Format an ISO timestamp to NL locale string */
function fmtTime(isoStr) {
  if (!isoStr) return '—';
  const d = new Date(isoStr);
  return d.toLocaleString('nl-NL', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}

/** Format a relative time string */
function fmtRelative(isoStr) {
  if (!isoStr) return '—';
  const d = new Date(isoStr);
  const diffMs = Date.now() - d.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return 'zojuist';
  if (diffMin < 60) return `${diffMin}m geleden`;
  const diffH = Math.floor(diffMin / 60);
  if (diffH < 24) return `${diffH}u geleden`;
  const diffD = Math.floor(diffH / 24);
  return `${diffD}d geleden`;
}

/** Show a toast notification */
function showToast(msg, type = 'info') {
  const colors = { info: 'rgba(34,211,238,.15)', ok: 'rgba(34,197,94,.15)', warn: 'rgba(245,158,11,.15)', err: 'rgba(239,68,68,.15)' };
  const border = { info: 'rgba(34,211,238,.4)', ok: 'rgba(34,197,94,.4)', warn: 'rgba(245,158,11,.4)', err: 'rgba(239,68,68,.4)' };
  const existing = document.getElementById('toast');
  if (existing) existing.remove();
  const el = document.createElement('div');
  el.id = 'toast';
  el.textContent = msg;
  el.style.cssText = `position:fixed;top:${document.querySelector('.topbar')?.getBoundingClientRect().bottom + 8 || 80}px;right:16px;z-index=9999;padding:10px 16px;border-radius:12px;background:${colors[type] || colors.info};border:1px solid ${border[type] || border.info};color:var(--text);font-size:13px;font-weight:600;backdrop-filter:blur(10px);box-shadow:0 8px 24px rgba(0,0,0,.3);transition:opacity .4s;max-width:320px`;
  document.body.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 400); }, 3000);
}

/** Render "last updated" badge */
function renderLastUpdated(isoStr) {
  _lastUpdated = isoStr;
  const el = document.getElementById('last-updated');
  if (el) el.textContent = `Verversd: ${fmtTime(isoStr)} (${fmtRelative(isoStr)})`;
}

/** Patch innerHTML of an element by ID, or silently skip if not found */
function patch(id, html) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = html;
}

/** Loading overlay */
function showLoading(id) {
  const el = document.getElementById(id);
  if (el) el.style.opacity = '0.4';
}
function hideLoading(id) {
  const el = document.getElementById(id);
  if (el) el.style.opacity = '1';
}

/** Start auto-refresh loop */
function startAutoRefresh(fetchFn) {
  _onRefresh = fetchFn;
  // Initial load
  fetchFn();
  // Every 5 minutes
  _refreshTimer = setInterval(fetchFn, REFRESH_INTERVAL_MS);
}

/** Manual refresh (reload button) */
function manualRefresh() {
  if (_onRefresh) {
    showToast('Verversen…', 'info');
    _onRefresh();
  }
}

/** Init the page: set nav active state + last updated el + refresh button */
function initPage(pageKey) {
  // Nav active
  document.querySelectorAll('.dnav a').forEach(a => {
    a.classList.remove('on');
    if (a.getAttribute('href') === pageKey) a.classList.add('on');
  });
  // Refresh button
  const rb = document.getElementById('refresh-btn');
  if (rb) rb.addEventListener('click', manualRefresh);
}

/** Escape HTML to prevent XSS */
function escHtml(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/** Priority badge class */
function pClass(p) {
  if (p === 'P1') return 'pill-r';
  if (p === 'P2') return 'pill-w';
  if (p === 'P3') return 'pill-c';
  return 'pill-s';
}

/** Lane badge class */
function laneClass(lane) {
  if (lane === 'top_5_now') return 'pill-r';
  if (lane === 'next_up') return 'pill-w';
  if (lane === 'watchlist') return 'pill-c';
  if (lane === 'refresh_first') return 'pill-c';
  return 'pill-s';
}

/** Status pill */
function statusPill(status) {
  const cls = status === 'done' ? 'pill-g' : status === 'in_progress' ? 'pill-c' : status === 'blocked' ? 'pill-r' : 'pill-s';
  return `<span class="pill ${cls}">${escHtml(status)}</span>`;
}
