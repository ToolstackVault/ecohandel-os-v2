/**
 * workflows-data.js — Live data fetcher for the Workflows page
 */
async function loadWorkflows() {
  const [wfData, histData] = await Promise.all([
    apiFetch('/workflows'),
    apiFetch('/workflows/history?limit=50'),
  ]);

  const workflows = wfData.workflows || [];
  const runs = histData.runs || [];

  // Group runs by workflow
  const runsByWf = {};
  for (const r of runs) {
    const wid = r.workflow_id;
    if (!runsByWf[wid]) runsByWf[wid] = [];
    runsByWf[wid].push(r);
  }

  // Update hero
  const enabled = workflows.filter(w => w.enabled).length;
  const lastRun = runs[0];
  patch('workflow-count', String(workflows.length));
  patch('workflows-enabled', String(enabled));
  patch('last-run-time', lastRun ? fmtRelative(lastRun.started_at) : 'nog nooit');

  // Build workflows table
  const rows = workflows.map(wf => {
    const wfRuns = runsByWf[wf.id] || [];
    const lastRunItem = wfRuns[0];
    const depList = (() => { try { return JSON.parse(wf.dependencies || '[]'); } catch { return []; } })();

    return `
    <tr>
      <td>
        <strong>${escHtml(wf.name || '')}</strong><br>
        <span class="muted" style="font-size:11px">${escHtml(wf.id)} · ${escHtml(wf.driver_type)}</span>
      </td>
      <td style="font-size:12px;max-width:220px">
        <span class="muted">${escHtml((wf.description || '').slice(0, 100))}</span>
      </td>
      <td>
        <span class="pill ${wf.enabled ? 'pill-g' : 'pill-s'}">${wf.enabled ? 'Aan' : 'Uit'}</span>
      </td>
      <td>
        ${depList.length > 0
          ? depList.map(d => `<span class="pill pill-s" style="margin:2px">${escHtml(String(d).slice(0,20))}</span>`).join('')
          : '<span class="muted">—</span>'}
      </td>
      <td>
        ${wf.last_run
          ? `<span style="font-size:12px">${fmtRelative(wf.last_run)}</span><br><span class="muted" style="font-size:11px">${fmtTime(wf.last_run)}</span>`
          : '<span class="muted">Nog nooit</span>'}
      </td>
      <td><span class="pill pill-s">${wf.total_runs || 0}</span></td>
      <td>
        ${wf.enabled
          ? `<button class="pill pill-c" style="cursor:pointer" onclick="triggerWorkflow('${wf.id}')" title="Workflow nu triggeren">▶ Run</button>`
          : '<span class="pill pill-s">Disabled</span>'}
      </td>
    </tr>`;
  }).join('');

  patch('workflows-tbody', rows);

  // Build recent runs table
  const runRows = runs.slice(0, 20).map(r => `
    <tr>
      <td><span class="pill pill-s">${escHtml(r.workflow_id)}</span></td>
      <td>${escHtml(r.workflow_name || '')}</td>
      <td>
        <span class="pill ${r.status === 'running' ? 'pill-c' : r.status === 'done' ? 'pill-g' : r.status === 'failed' ? 'pill-r' : 'pill-s'}">
          ${escHtml(r.status)}
        </span>
      </td>
      <td>${escHtml(r.triggered_by || '—')}</td>
      <td>${fmtRelative(r.started_at)}</td>
      <td>${r.completed_at ? fmtRelative(r.completed_at) : '—'}</td>
    </tr>`).join('');

  patch('runs-tbody', runRows || '<tr><td colspan="6" class="muted">Nog geen runs</td></tr>');

  renderLastUpdated();
  hideLoading('workflows-main');
}

async function triggerWorkflow(workflowId) {
  showToast(`Trigger ${workflowId}…`, 'info');
  try {
    const res = await fetch(`${API_BASE}/workflows/${workflowId}/run`, {
      method: 'POST',
      headers: { Authorization: apiAuthHeader() }
    });
    const json = await res.json();
    if (json.ok) {
      showToast(`${workflowId} gestart!`, 'ok');
      setTimeout(loadWorkflows, 1500);
    } else {
      showToast(`Fout: ${json.error?.message}`, 'err');
    }
  } catch (e) {
    showToast(`Netwerkfout: ${e.message}`, 'err');
  }
}

async function initWorkflows() {
  initPage('/workflows.html');
  startAutoRefresh(loadWorkflows);
}
