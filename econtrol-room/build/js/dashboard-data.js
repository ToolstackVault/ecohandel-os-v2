/**
 * dashboard-data.js — Live data fetcher for the Econtrol Room Dashboard
 * Calls /api/v1/dashboard and renders KPIs, GSC, Ads, WeFact, Queue, Agents
 */
async function loadDashboard() {
  const data = await apiFetch('/dashboard');
  const meta = data.meta || {};
  const gsc = data.gsc || {};
  const ga4 = data.ga4 || {};
  const wefact = data.wefact || {};
  const ads = data.ads || {};
  const health = data.health || {};
  const queue = data.queue || {};
  const agents = data.agents || [];

  // ── Hero KPIs ────────────────────────────────────────────────────────────
  const todayTraffic = ga4.windows?.today?.sessions || ga4.kpis?.find(k => k.label.includes('Today'))?.value || '—';
  const yesterdayTraffic = ga4.windows?.yesterday?.sessions || '—';
  const gscClicks7d = gsc.kpis?.find(k => k.label.includes('7d') || k.label.includes('7 D'))?.value || '—';
  const gscClicks28d = gsc.kpis?.find(k => k.label.includes('28d') || k.label.includes('28 D'))?.value || '—';
  const traffic7d = ga4.windows?.last_7_days?.sessions || ga4.windows?.last_7_days?.users || '—';
  const traffic28d = ga4.windows?.last_28_days?.sessions || ga4.windows?.last_28_days?.users || '—';
  const wefact28d = wefact.windows?.last_28_days?.invoice_total_fmt || '€0,00';
  const wefact7d = wefact.windows?.last_7_days?.invoice_total_fmt || '€0,00';
  const wefactInvoices28d = wefact.windows?.last_28_days?.invoice_count || 0;
  const wefactFollowups = wefact.finance_intelligence?.quote_followup_count_fmt || '0';
  const wefactOverdue = wefact.finance_intelligence?.overdue_amount_fmt || '€0,00';
  const adsSpend7d = ads.windows?.last_7_days?.cost_eur || '€0,00';
  const adsRoas7d = ads.kpis?.find(k => k.label.includes('ROAS') && k.label.includes('7d'))?.value || ads.windows?.last_7_days?.roas || '—';
  const convValue28d = ads.windows?.last_28_days?.conversion_value_fmt || ads.kpis?.find(k => k.label.includes('Conv. value') && k.label.includes('28d'))?.value || '€0';

  // Queue KPIs
  const queueTotal = queue.total || 0;
  const queueTop5 = queue.top5 || 0;
  const queueDone = queue.done || 0;

  // Hero stat cards
  patch('kpi-traffic-today', `<span class="sv">${escHtml(String(todayTraffic))}</span><span class="sn">gisteren ${yesterdayTraffic}</span>`);
  patch('kpi-gsc-clicks', `<span class="sv">${escHtml(String(gscClicks7d))}</span><span class="sn">28d ${gscClicks28d} · CTR ${gsc.kpis?.find(k=>k.label.includes('CTR'))?.value || '—'}</span>`);
  patch('kpi-traffic-7d', `<span class="sv">${escHtml(String(traffic7d))}</span><span class="sn">28d ${traffic28d}</span>`);
  patch('kpi-wefact', `<span class="sv">${escHtml(wefact28d)}</span><span class="sn">7d ${wefact7d} · ${wefactInvoices28d} facturen · follow-up ${wefactFollowups} · open achterstallig ${wefactOverdue}</span>`);

  // ── Ops status ──────────────────────────────────────────────────────────
  const sources = health.sources || [];
  const okSources = sources.filter(s => s.status === 'success' || s.status === 'live').length;
  const partialSources = sources.filter(s => s.status === 'partial').length;
  const opsStatus = partialSources === 0 && okSources > 0 ? 'badge-ok' : partialSources > 0 ? 'badge-warn' : 'badge-off';
  const opsLabel = partialSources === 0 ? 'ok' : `${okSources} live, ${partialSources} partial`;
  patch('ops-status-badge', `<span class="badge ${opsStatus}">${opsLabel}</span>`);

  // ── Traffic snapshot table ───────────────────────────────────────────────
  const periods = [
    { label: 'Vandaag', sessions: ga4.windows?.today?.sessions, users: ga4.windows?.today?.users, clicks: gsc.windows?.today?.clicks, impr: gsc.windows?.today?.impressions, ctr: gsc.windows?.today?.ctr },
    { label: 'Gisteren', sessions: ga4.windows?.yesterday?.sessions, users: ga4.windows?.yesterday?.users, clicks: gsc.windows?.yesterday?.clicks, impr: gsc.windows?.yesterday?.impressions, ctr: gsc.windows?.yesterday?.ctr },
    { label: 'Laatste 7 dgn', sessions: ga4.windows?.last_7_days?.sessions, users: ga4.windows?.last_7_days?.users, clicks: gsc.windows?.last_7_days?.clicks, impr: gsc.windows?.last_7_days?.impressions, ctr: gsc.windows?.last_7_days?.ctr },
    { label: 'Laatste 28 dgn', sessions: ga4.windows?.last_28_days?.sessions, users: ga4.windows?.last_28_days?.users, clicks: gsc.windows?.last_28_days?.clicks, impr: gsc.windows?.last_28_days?.impressions, ctr: gsc.windows?.last_28_days?.ctr },
  ];

  const trafficRows = periods.map(p => `
    <tr>
      <td><strong>${escHtml(p.label)}</strong></td>
      <td>${p.sessions ?? '—'}</td>
      <td>${p.users ?? '—'}</td>
      <td>${p.clicks ?? '—'}</td>
      <td>${p.impr ?? '—'}</td>
      <td>${p.ctr ?? '—'}</td>
      <td class="muted">—</td>
    </tr>`).join('');

  patch('traffic-tbody', trafficRows);

  // ── Google Ads panel ─────────────────────────────────────────────────────
  const adsRows = [
    { label: 'Vandaag', cost: ads.windows?.today?.cost_eur, clicks: ads.windows?.today?.clicks, impr: ads.windows?.today?.impressions, ctr: ads.windows?.today?.ctr, conv: ads.windows?.today?.conversions, value: ads.windows?.today?.value_eur },
    { label: 'Gisteren', cost: ads.windows?.yesterday?.cost_eur, clicks: ads.windows?.yesterday?.clicks, impr: ads.windows?.yesterday?.impressions, ctr: ads.windows?.yesterday?.ctr, conv: ads.windows?.yesterday?.conversions, value: ads.windows?.yesterday?.value_eur },
    { label: 'Laatste 7 dgn', cost: adsSpend7d, clicks: ads.windows?.last_7_days?.clicks, impr: ads.windows?.last_7_days?.impressions, ctr: ads.windows?.last_7_days?.ctr, conv: ads.windows?.last_7_days?.conversions, value: ads.windows?.last_7_days?.value_eur },
    { label: 'Laatste 28 dgn', cost: ads.windows?.last_28_days?.cost_eur, clicks: ads.windows?.last_28_days?.clicks, impr: ads.windows?.last_28_days?.impressions, ctr: ads.windows?.last_28_days?.ctr, conv: ads.windows?.last_28_days?.conversions, value: convValue28d },
  ].map(p => `
    <tr>
      <td><strong>${escHtml(p.label)}</strong></td>
      <td>${escHtml(p.cost ?? '—')}</td>
      <td>${escHtml(p.clicks ?? '—')}</td>
      <td>${escHtml(p.impr ?? '—')}</td>
      <td>${escHtml(p.ctr ?? '—')}</td>
      <td>${escHtml(p.conv ?? '—')}</td>
      <td>${escHtml(p.value ?? '—')}</td>
    </tr>`).join('');

  patch('ads-tbody', adsRows);

  // Ads ROAS KPI
  patch('kpi-ads-roas', `<span class="sv">${escHtml(String(adsRoas7d))}</span><span class="sn">28d ${ads.kpis?.find(k=>k.label.includes('ROAS') && k.label.includes('28d'))?.value || '—'}</span>`);
  patch('kpi-ads-conv', `<span class="sv">${escHtml(String(convValue28d))}</span><span class="sn">7d ${ads.windows?.last_7_days?.value_eur || '€0'}</span>`);

  // ── WeFact panel ─────────────────────────────────────────────────────────
  const wfRows = [
    { label: 'Vandaag', count: wefact.windows?.today?.invoice_count, total: wefact.windows?.today?.invoice_total_fmt, quotes: wefact.windows?.today?.quote_count, quote_total: wefact.windows?.today?.quote_total_fmt },
    { label: 'Gisteren', count: wefact.windows?.yesterday?.invoice_count, total: wefact.windows?.yesterday?.invoice_total_fmt, quotes: wefact.windows?.yesterday?.quote_count, quote_total: wefact.windows?.yesterday?.quote_total_fmt },
    { label: 'Laatste 7 dgn', count: wefact.windows?.last_7_days?.invoice_count, total: wefact.windows?.last_7_days?.invoice_total_fmt, quotes: wefact.windows?.last_7_days?.quote_count, quote_total: wefact.windows?.last_7_days?.quote_total_fmt },
    { label: 'Laatste 28 dgn', count: wefact.windows?.last_28_days?.invoice_count, total: wefact.windows?.last_28_days?.invoice_total_fmt, quotes: wefact.windows?.last_28_days?.quote_count, quote_total: wefact.windows?.last_28_days?.quote_total_fmt },
  ].map(p => `
    <tr>
      <td><strong>${escHtml(p.label)}</strong></td>
      <td>${escHtml(String(p.count ?? 0))}</td>
      <td>${escHtml(p.total ?? '€0,00')}</td>
      <td>${escHtml(String(p.quotes ?? 0))}</td>
      <td>${escHtml(p.quote_total ?? '€0,00')}</td>
    </tr>`).join('');

  patch('wefact-tbody', wfRows);

  // ── Queue panel ───────────────────────────────────────────────────────────
  patch('kpi-queue-total', `<span class="sv">${queueTotal}</span><span class="sn">top5 ${queueTop5} · klaar ${queueDone}</span>`);
  patch('kpi-queue-top5', `<span class="sv">${queueTop5}</span><span class="sn">van ${queueTotal} items</span>`);

  // Queue lane breakdown
  const laneRows = Object.entries({
    top_5_now: '🔴 Top 5 Nu',
    next_up: '🟡 Next Up',
    watchlist: '🔵 Watchlist',
    refresh_first: '🔵 Refresh Eerst',
    unqueued: '⚪ Unqueued',
    done: '✅ Klaar',
  }).map(([lane, label]) => {
    const count = queue[lane] || 0;
    return `<tr><td>${label}</td><td><strong>${count}</strong></td></tr>`;
  }).join('');

  patch('queue-tbody', laneRows);

  // ── Agent runs ─────────────────────────────────────────────────────────────
  const agentRows = agents.slice(0, 10).map(r => `
    <tr>
      <td>${escHtml(r.agent_name)}</td>
      <td><span class="pill ${r.status === 'running' ? 'pill-c' : r.status === 'done' ? 'pill-g' : 'pill-s'}">${escHtml(r.status)}</span></td>
      <td>${fmtRelative(r.started_at)}</td>
      <td>${escHtml(String(r.items_processed || '—'))}</td>
      <td>${escHtml(String(r.output_summary || '—'))}</td>
    </tr>`).join('');

  patch('agent-tbody', agentRows);

  // ── Last updated ──────────────────────────────────────────────────────────
  renderLastUpdated(meta.generated_at);
  hideLoading('dashboard-main');
}

async function initDashboard() {
  initPage('/');
  startAutoRefresh(loadDashboard);
}
