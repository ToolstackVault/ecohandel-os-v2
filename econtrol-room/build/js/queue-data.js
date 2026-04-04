/**
 * queue-data.js — Live data fetcher for the Smart Content Queue page
 */
async function loadQueue() {
  const data = await apiFetch('/queue');
  const meta = data.meta || {};
  const items = data.items || [];
  const summary = data.summary || {};
  const top5 = data.top_5_now || [];
  const refresh = data.refresh_first || [];

  // Update hero stats
  patch('total-items', String(summary.total || 0));
  patch('refresh-time', fmtTime(meta.generated_at));
  renderLastUpdated(meta.generated_at);

  // Group by lane
  const lanes = {};
  for (const item of items) {
    const lane = item.lane || 'unqueued';
    if (!lanes[lane]) lanes[lane] = [];
    lanes[lane].push(item);
  }

  const LANE_ORDER = ['top_5_now', 'next_up', 'refresh_first', 'watchlist', 'unqueued', 'killed_noise', 'done'];
  const LANE_LABELS = {
    top_5_now: '🔴 Top 5 Nu',
    next_up: '🟡 Next Up',
    refresh_first: '🔵 Refresh Eerst',
    watchlist: '🔵 Watchlist',
    unqueued: '⚪ Unqueued',
    killed_noise: '💀 Gefilterd',
    done: '✅ Klaar',
  };
  const LANE_CLASS = {
    top_5_now: 'sc-r',
    next_up: 'sc-w',
    refresh_first: 'sc-c',
    watchlist: 'sc-c',
    unqueued: 'sc-g',
    killed_noise: 'sc-r',
    done: 'sc-g',
  };

  let html = '';

  for (const laneName of LANE_ORDER) {
    const laneItems = lanes[laneName] || [];
    if (laneItems.length === 0) continue;

    const colClass = LANE_CLASS[laneName] || 'sc-c';
    const label = LANE_LABELS[laneName] || laneName;

    html += `
    <div class="p s12" style="margin-bottom:14px">
      <div class="ph">
        <div>
          <div class="ey">${label}</div>
          <h2>${laneItems.length} item${laneItems.length !== 1 ? 's' : ''}</h2>
        </div>
      </div>
      <div class="tw">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Titel</th>
              <th>Score</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Why Now</th>
              <th>Next Step</th>
              <th>Owner</th>
            </tr>
          </thead>
          <tbody>
            ${laneItems.map(item => `
            <tr>
              <td><span class="pill pill-s">${escHtml(item.id || '')}</span></td>
              <td><strong>${escHtml(item.title || '')}</strong><br><span class="muted" style="font-size:11px">${escHtml(item.primary_cluster || '')}</span></td>
              <td><span class="pill ${item.total_score >= 80 ? 'pill-r' : item.total_score >= 65 ? 'pill-w' : 'pill-c'}">${item.total_score || 0}</span></td>
              <td><span class="pill ${pClass(item.priority_label)}">${escHtml(item.priority_label || '—')}</span></td>
              <td>${statusPill(item.status)}</td>
              <td style="max-width:200px;font-size:12px;color:var(--muted)">${escHtml((item.why_now || '').slice(0, 100))}${item.why_now?.length > 100 ? '…' : ''}</td>
              <td><span class="pill pill-s">${escHtml(item.recommended_next_step || '—')}</span></td>
              <td>${escHtml(item.owner || '—')}</td>
            </tr>`).join('')}
          </tbody>
        </table>
      </div>
    </div>`;
  }

  if (html === '') {
    html = `<div class="p s12"><p class="muted">Nog geen items in de queue. Score queue draaien om items te scoreren.</p></div>`;
  }

  patch('queue-container', html);
  hideLoading('queue-main');
}

async function initQueue() {
  initPage('/smart-content-queue.html');
  startAutoRefresh(loadQueue);
}
