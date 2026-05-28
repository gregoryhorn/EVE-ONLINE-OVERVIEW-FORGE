/* Dashboard screen */

function renderDashboard(doc, recentFiles) {
  const tabs = doc ? (doc.tabs || []) : [];
  const presets = doc ? (doc.presets || []) : [];
  const columns = doc ? (doc.columns?.columnOrder || []) : [];
  const appearance = doc ? doc.appearance : null;

  const noDoc = !doc;

  return `
<div class="section-header">Dashboard</div>

<div class="dashboard-grid">

  <!-- Overview Summary -->
  <div class="card">
    <div class="card-header">
      <div class="card-header-left">Overview Summary</div>
      ${!noDoc ? `<span style="font-size:10px;color:var(--text-muted);font-family:var(--font-mono)">${doc.meta?.sourceFormat || 'unknown'}</span>` : ''}
    </div>
    ${noDoc ? `
      <div class="empty-state">
        <div class="empty-state-icon">📂</div>
        <div class="empty-state-title">No Overview Loaded</div>
        <div class="empty-state-text">Import a YAML file or create a new overview to get started.</div>
      </div>
    ` : `
      <div class="overview-title-bar">
        <div>
          <div class="overview-filename">${window._appState.currentFileName || 'Untitled'}</div>
          <div class="overview-path">${window._appState.currentPath || ''}</div>
        </div>
      </div>
      <div class="stat-row">
        <div class="stat-box">
          <div class="stat-value">${tabs.length}</div>
          <div class="stat-label">Tabs</div>
        </div>
        <div class="stat-box">
          <div class="stat-value">${presets.length}</div>
          <div class="stat-label">Presets</div>
        </div>
        <div class="stat-box">
          <div class="stat-value">${columns.length}</div>
          <div class="stat-label">Columns</div>
        </div>
        <div class="stat-box">
          <div class="stat-value" style="color:var(--text-secondary)">${doc.meta?.clientTabCap || 8}</div>
          <div class="stat-label">Tab Cap</div>
        </div>
      </div>
    `}
  </div>

  <!-- Validation Status -->
  <div class="card">
    <div class="card-header">
      <div class="card-header-left">Validation Status</div>
      ${!noDoc ? `<button class="btn-secondary btn-sm" id="run-validate-btn">Run Check</button>` : ''}
    </div>
    <div id="validation-status-content">
      ${noDoc ? `
        <div class="empty-state">
          <div class="empty-state-icon">✓</div>
          <div class="empty-state-title">Nothing to validate</div>
          <div class="empty-state-text">Load an overview file first.</div>
        </div>
      ` : _validationPlaceholder()}
    </div>
  </div>

  <!-- Recent Files -->
  <div class="card">
    <div class="card-header">
      <div class="card-header-left">Recent Files</div>
    </div>
    ${recentFiles.length === 0 ? `
      <div class="empty-state" style="padding:20px">
        <div class="empty-state-title">No recent files</div>
        <div class="empty-state-text">Files you open will appear here.</div>
      </div>
    ` : `
      <ul class="file-list">
        ${recentFiles.map(f => `
          <li class="file-item" data-path="${f.path}" title="${f.path}">
            <div>
              <div class="file-item-name">${f.name}</div>
              <div class="file-item-meta">${f.tabCount} tabs · ${f.presetCount} presets</div>
            </div>
            <div class="file-item-time">${_relTime(f.openedAt)}</div>
          </li>
        `).join('')}
      </ul>
    `}
    <button class="open-file-btn" id="dashboard-open-btn">
      <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H8a3 3 0 00-3 3v1.5a1.5 1.5 0 01-3 0V6z" clip-rule="evenodd"/><path d="M6 12a2 2 0 012-2h8a2 2 0 012 2v2a2 2 0 01-2 2H2h2a2 2 0 002-2v-2z"/></svg>
      Open File Browser
    </button>
  </div>

  <!-- Template Shortcuts -->
  <div class="card">
    <div class="card-header">
      <div class="card-header-left">New Overview</div>
    </div>
    <div style="margin-bottom:10px;font-size:12px;color:var(--text-secondary)">Start from the maintained standard overview, a focused starter, or a blank overview.</div>
    <div class="template-grid">
      <button class="template-btn" data-template="standard">
        <span class="template-icon">▦</span>Standard
      </button>
      <button class="template-btn" data-template="blank">
        <span class="template-icon">⬜</span>Blank
      </button>
      <button class="template-btn" data-template="pvp">
        <span class="template-icon">⚔️</span>PVP
      </button>
      <button class="template-btn" data-template="mining">
        <span class="template-icon">⛏️</span>Mining
      </button>
    </div>
  </div>

</div>
  `;
}

function _validationPlaceholder() {
  const sections = ['Tabs', 'Presets', 'Appearance', 'Columns', 'States'];
  return sections.map(s => `
    <div class="validation-row">
      <div class="validation-row-left">
        <div class="val-dot val-dot--none"></div>
        <div class="validation-row-name">${s}</div>
      </div>
      <span class="val-badge val-badge--none">Not checked</span>
    </div>
  `).join('');
}

function _relTime(iso) {
  if (!iso) return '';
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function bindDashboard() {
  // Recent file clicks
  document.querySelectorAll('.file-item[data-path]').forEach(el => {
    el.addEventListener('click', () => window._loadFile(el.dataset.path));
  });

  // Template buttons
  document.querySelectorAll('.template-btn[data-template]').forEach(btn => {
    btn.addEventListener('click', () => window._newFromTemplate(btn.dataset.template));
  });

  // Open file button
  const openBtn = document.getElementById('dashboard-open-btn');
  if (openBtn) openBtn.addEventListener('click', () => window._openImportModal());

  // Run validate
  const valBtn = document.getElementById('run-validate-btn');
  if (valBtn) valBtn.addEventListener('click', () => window._runValidation());
}

function applyValidationResults(results) {
  const el = document.getElementById('validation-status-content');
  if (!el) return;

  const groups = validationGroups(results);
  el.innerHTML = ['Tabs', 'Presets', 'Appearance', 'Columns', 'States'].map(name => {
    const matches = groups[name] || [];
    const errors = matches.filter(r => r.severity === 'error').length;
    const warns = matches.filter(r => r.severity === 'warning').length;
    let dotClass = 'val-dot--ok';
    let badgeClass = 'val-badge--ok';
    let badgeText = 'OK';
    if (errors > 0) { dotClass = 'val-dot--error'; badgeClass = 'val-badge--error'; badgeText = `${errors} error${errors > 1 ? 's' : ''}`; }
    else if (warns > 0) { dotClass = 'val-dot--warn'; badgeClass = 'val-badge--warn'; badgeText = `${warns} warning${warns > 1 ? 's' : ''}`; }
    return `
      <div class="validation-row">
        <div class="validation-row-left">
          <div class="val-dot ${dotClass}"></div>
          <div class="validation-row-name">${name}</div>
        </div>
        <span class="val-badge ${badgeClass}">${badgeText}</span>
      </div>
    `;
  }).join('');
}
