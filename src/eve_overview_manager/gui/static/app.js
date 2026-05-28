/* ============================================================
   Overview Forge â€” Main Application
   ============================================================ */

// â”€â”€ App State â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
window._appState = {
  currentDoc: null,
  currentPath: null,
  currentFileName: null,
  currentScreen: 'dashboard',
  validationResults: [],
  activePreviewTabSlot: null,
  previewMode: 'overview',
  previewPresetId: null,
  previewShowTabs: true,
  previewRequestSeq: 0,
};

// â”€â”€ API helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
async function api(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res = await fetch('/api' + path, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

// â”€â”€ Toast â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
let _toastTimer;
function toast(msg, type = '') {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast' + (type ? ' toast--' + type : '');
  el.style.display = 'block';
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => { el.style.display = 'none'; }, 3000);
}

// â”€â”€ Navigation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function navigate(screen) {
  window._appState.currentScreen = screen;
  document.querySelectorAll('.nav-item').forEach(el => {
    const isAdvancedChild = (screen === 'types' || screen === 'brackets') && el.dataset.screen === 'advanced';
    el.classList.toggle('active', el.dataset.screen === screen || isAdvancedChild);
  });
  renderScreen(screen);
}

function renderScreen(screen) {
  const center = document.getElementById('center-panel');
  const right = document.getElementById('right-panel');
  const workspace = document.querySelector('.workspace');
  const doc = window._appState.currentDoc;
  const fullWidthScreen = screen === 'profiles';

  workspace?.classList.toggle('workspace--full', fullWidthScreen);

  window._appState.previewPresetId = null;
  window._appState.previewShowTabs = screen !== 'presets';
  if (fullWidthScreen) {
    right.innerHTML = '';
  } else {
    right.innerHTML = renderLivePreview(doc);
    refreshLivePreview();
  }

  switch (screen) {
    case 'dashboard':
      api('GET', '/recent-files').then(data => {
        center.innerHTML = renderDashboard(doc, data.recentFiles || []);
        bindDashboard();
        if (window._appState.validationResults.length > 0) {
          applyValidationResults(window._appState.validationResults);
        }
      }).catch(() => {
        center.innerHTML = renderDashboard(doc, []);
        bindDashboard();
      });
      break;
    case 'tabs':
      center.innerHTML = renderTabsScreen();
      bindTabsScreen();
      break;
    case 'presets':
      center.innerHTML = renderPresetsScreen();
      bindPresetsScreen();
      break;
    case 'types':
      center.innerHTML = renderTypesScreen();
      bindTypesScreen();
      break;
    case 'appearance':
      center.innerHTML = renderAppearanceScreen();
      bindAppearanceScreen();
      break;
    case 'columns':
      center.innerHTML = renderColumnsScreen();
      bindColumnsScreen();
      break;
    case 'brackets':
      center.innerHTML = renderBracketsScreen();
      bindBracketsScreen();
      break;
    case 'importexport':
      center.innerHTML = renderImportExportScreen();
      bindImportExportScreen();
      if (window._appState.validationResults.length > 0 && window.renderImportExportValidationPanel) {
        window.renderImportExportValidationPanel(window._appState.validationResults);
      }
      break;
    case 'profiles':
      center.innerHTML = renderProfilesScreen();
      bindProfilesScreen();
      break;
    case 'advanced':
      center.innerHTML = renderAdvancedScreen();
      bindAdvancedScreen();
      break;
    default:
      center.innerHTML = renderPlaceholder(screen);
  }
  if (!fullWidthScreen) bindLivePreview();
}

function bindLivePreview() {
  document.querySelectorAll('.preview-tab[data-preview-slot]').forEach(tab => {
    tab.addEventListener('click', () => {
      window._appState.activePreviewTabSlot = Number(tab.dataset.previewSlot);
      refreshLivePreview();
    });
  });
  document.querySelectorAll('.preview-mode-btn[data-preview-mode]').forEach(btn => {
    btn.addEventListener('click', () => {
      window._appState.previewMode = btn.dataset.previewMode;
      refreshLivePreview();
    });
  });
}

function renderPlaceholder(screen) {
  const labels = {
    tabs: 'Tabs',
    presets: 'Presets',
    types: 'Types & States',
    appearance: 'Appearance',
    columns: 'Columns',
    brackets: 'Brackets',
    profiles: 'Profiles',
    importexport: 'Import / Export',
  };
  const name = labels[screen] || screen;
  const hints = {
    tabs: 'Manage your 8-tab overview layout â€” names, colors, and preset bindings.',
    presets: 'Create and edit named presets defining which ship types and states appear.',
    types: 'Browse EVE entity categories and understand state hierarchy and filters.',
    appearance: 'Control row colors, background priorities, blink settings, and standings display.',
    columns: 'Choose which columns appear in your overview and in what order.',
    brackets: 'Configure ship bracket labels and what information displays in space.',
    profiles: 'Scan local EVE profiles and safely clone settings between characters and accounts.',
    importexport: 'Import YAML from EVE, export back to YAML, JSON, or CSV audit format.',
    advanced: 'Reference and low-frequency tools that are not part of the normal tab editing workflow.',
  };
  return `
    <div class="placeholder-screen">
      <div class="coming-soon-badge">Coming in next phase</div>
      <h2>${name}</h2>
      <p>${hints[screen] || ''}</p>
    </div>
  `;
}

function renderAdvancedScreen() {
  return `
    <div class="section-header">Advanced</div>
    <div class="advanced-grid">
      <button class="advanced-card" type="button" data-advanced-screen="types">
        <div class="advanced-card-title">Types &amp; States</div>
        <div class="advanced-card-text">Reference catalog for entity groups and overview states. Use Presets for normal visibility edits.</div>
      </button>
      <button class="advanced-card" type="button" data-advanced-screen="brackets">
        <div class="advanced-card-title">Brackets</div>
        <div class="advanced-card-text">Inspect bracket-related settings. Bracket preset assignment is handled from Tabs.</div>
      </button>
    </div>
  `;
}

function bindAdvancedScreen() {
  document.querySelectorAll('[data-advanced-screen]').forEach(btn => {
    btn.addEventListener('click', () => navigate(btn.dataset.advancedScreen));
  });
}

function renderLivePreview(doc) {
  return `
    <div class="preview-header">
      <div class="preview-title">
        <div class="preview-live-dot"></div>
        Live Preview
      </div>
      <div class="preview-controls">
        <button class="preview-mode-btn preview-mode-btn--active" type="button" data-preview-mode="overview">Overview</button>
      </div>
    </div>

    <div id="preview-tab-strip" style="padding:8px 14px;border-bottom:1px solid var(--border);background:#0a0d14;flex-shrink:0;overflow-x:auto;white-space:nowrap;${window._appState.previewShowTabs ? '' : 'display:none;'}">
      <span style="font-size:10px;color:var(--text-muted)">${doc ? 'Loading preview...' : 'No overview loaded'}</span>
    </div>

    <div class="preview-table-wrap">
      <table class="preview-table">
        <thead id="preview-head"></thead>
        <tbody id="preview-body">
          <tr><td style="padding:16px;color:var(--text-muted)">Loading sample entities...</td></tr>
        </tbody>
      </table>
    </div>

    <div class="preview-footer">
      <div class="preview-footer-count" id="preview-count">0 sample rows</div>
      <div class="preview-footer-preset" id="preview-preset">Preset: None</div>
    </div>
  `;
}

async function refreshLivePreview() {
  const right = document.getElementById('right-panel');
  if (!right) return;
  const requestSeq = ++window._appState.previewRequestSeq;
  const slot = window._appState.activePreviewTabSlot;
  const mode = window._appState.previewMode || 'overview';
  const presetId = window._appState.previewPresetId;
  const params = new URLSearchParams({ mode });
  if (slot !== null && slot !== undefined) params.set('slot', String(slot));
  if (presetId) params.set('preset_id', presetId);
  if (previewDebugEnabled()) params.set('debug', 'true');
  if (previewCoverageEnabled()) params.set('coverage', 'true');
  try {
    previewDebugLog('request', {
      requestSeq,
      screen: window._appState.currentScreen,
      slot,
      mode,
      presetId,
      coverage: previewCoverageEnabled(),
      url: '/api/preview?' + params.toString(),
    });
    const data = await api('GET', '/preview?' + params.toString());
    if (requestSeq !== window._appState.previewRequestSeq) return;
    previewDebugLog('response', data.diagnostics || {
      rowCount: data.preview?.rows?.length || 0,
      activePreset: data.preview?.activePreset,
      activeTab: data.preview?.activeTab,
    });
    applyLivePreview(data.preview);
  } catch (e) {
    if (requestSeq !== window._appState.previewRequestSeq) return;
    previewDebugLog('error', { message: e.message, requestSeq });
    const body = document.getElementById('preview-body');
    if (body) {
      body.innerHTML = `<tr><td style="padding:16px;color:var(--danger)">Preview unavailable: ${escapeHtml(e.message)}</td></tr>`;
    }
  }
}

function applyLivePreview(preview) {
  const tabStrip = document.getElementById('preview-tab-strip');
  const head = document.getElementById('preview-head');
  const body = document.getElementById('preview-body');
  const count = document.getElementById('preview-count');
  const preset = document.getElementById('preview-preset');
  if (!tabStrip || !head || !body || !count || !preset) return;

  tabStrip.innerHTML = renderPreviewTabs(preview.tabs || []);
  const columns = preview.columns || [];
  head.innerHTML = `<tr>${columns.map(c => `<th class="${previewColumnClass(c.id)}">${escapeHtml(c.label)}</th>`).join('')}</tr>`;
  body.innerHTML = renderPreviewRows(preview.rows || [], columns);
  count.textContent = `${(preview.rows || []).length} / ${preview.totalSampleRows || 0} sample rows`;
  preset.textContent = `Preset: ${preview.activePreset?.name || preview.activePreset?.id || 'None'}`;
  document.querySelectorAll('.preview-mode-btn[data-preview-mode]').forEach(btn => {
    btn.classList.toggle('preview-mode-btn--active', btn.dataset.previewMode === preview.mode);
  });
  bindLivePreview();
}

function renderPreviewTabs(tabs) {
  if (!tabs.length) {
    return `<span style="font-size:10px;color:var(--text-muted)">No tabs defined</span>`;
  }
  return tabs.map((t, i) => {
    const color = t.colorARGB ? `#${t.colorARGB.slice(2)}` : '#00c8f0';
    return `<span class="preview-tab ${t.active ? 'preview-tab--active' : ''}" data-preview-slot="${t.slot}" style="
      display:inline-block;padding:3px 10px;margin-right:4px;
      font-size:10px;font-weight:700;letter-spacing:0.06em;
      border-bottom:2px solid ${color};color:${color};cursor:pointer;${t.active ? 'background:rgba(255,255,255,0.05);' : ''}
      text-transform:uppercase;
    " title="${escapeHtml(t.overviewPresetRef || '')}">${escapeHtml(t.label || `Tab ${i + 1}`)}</span>`;
  }).join('');
}

function renderPreviewRows(rows, columns) {
  if (!rows.length) {
    const span = Math.max(columns.length, 1);
    return `<tr><td colspan="${span}" style="padding:16px;color:var(--text-muted)">No sample rows match this preset. Add groups or adjust filtered states.</td></tr>`;
  }
  return rows.map(row => `
    <tr class="${rowClassName(row)}"${rowStyle(row)}>
      ${columns.map(column => {
        const value = row.cells?.[column.id] || '';
        const colClass = previewColumnClass(column.id);
        if (column.id === 'ICON') {
          const iconClass = `preview-icon preview-icon--${String(value).toLowerCase().replace(/[^a-z0-9_-]/g, '') || 'unknown'}`;
          return `<td class="${colClass}" title="${escapeHtml(row.groupName || value)}"><span class="${iconClass}" aria-label="${escapeHtml(row.groupName || value)}"></span></td>`;
        }
        const color = row.appearance?.flagColor || (column.id !== 'NAME' && column.id !== 'ICON' ? 'var(--text-secondary)' : '');
        const style = color ? ` style="color:${escapeHtml(color)}"` : '';
        return `<td class="${colClass}" title="${escapeHtml(value)}"${style}>${escapeHtml(value)}</td>`;
      }).join('')}
    </tr>
  `).join('');
}

function rowClassName(row) {
  const classes = [row.className || 'row-neutral'];
  if (row.appearance?.backgroundBlink) classes.push('row-blink-bg');
  if (row.appearance?.flagBlink) classes.push('row-blink-fg');
  return classes.join(' ');
}

function rowStyle(row) {
  const background = row.appearance?.backgroundColor;
  const styles = [];
  if (background) {
    styles.push(`--row-bg:${escapeHtml(background)}22`);
    styles.push(`--row-blink-bg:${escapeHtml(background)}55`);
    styles.push(`background:var(--row-bg)`);
  }
  if (row.appearance?.flagColor) {
    styles.push(`--row-fg:${escapeHtml(row.appearance.flagColor)}`);
  }
  return styles.length ? ` style="${styles.join(';')}"` : '';
}

function previewColumnClass(columnId) {
  if (columnId === 'ICON') return 'preview-col-icon row-bracket';
  if (columnId === 'NAME') return 'preview-col-name';
  if (columnId === 'DISTANCE') return 'preview-col-dist';
  if (columnId === 'TYPE') return 'preview-col-type';
  return 'preview-col-extra';
}

function previewDebugEnabled() {
  try {
    return window.localStorage.getItem('overviewForgePreviewDebug') === '1';
  } catch {
    return false;
  }
}

function previewCoverageEnabled() {
  try {
    return window.localStorage.getItem('overviewForgePreviewCoverage') === '1';
  } catch {
    return false;
  }
}

function previewDebugLog(label, data) {
  if (!previewDebugEnabled()) return;
  console.debug(`[OverviewForge preview ${label}]`, data);
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

// â”€â”€ File loading â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
window._loadFile = async function(path) {
  try {
    const data = await api('POST', '/document/load', { path });
    window._appState.currentDoc = data.document;
    window._appState.currentPath = data.path;
    window._appState.currentFileName = data.path.split(/[\\/]/).pop();
    document.getElementById('active-file-name').textContent = window._appState.currentFileName;
    document.getElementById('status-hint').textContent = `Loaded: ${window._appState.currentFileName}`;
    window._appState.validationResults = [];
    updateStatusBar(0, 0);
    renderScreen(window._appState.currentScreen);
    toast(`Loaded ${window._appState.currentFileName}`, 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
};

window._loadFileContent = async function(file) {
  try {
    const content = await file.text();
    const data = await api('POST', '/document/load-content', { filename: file.name, content });
    window._appState.currentDoc = data.document;
    window._appState.currentPath = data.path;
    window._appState.currentFileName = file.name;
    document.getElementById('active-file-name').textContent = file.name;
    document.getElementById('status-hint').textContent = `Loaded: ${file.name}`;
    window._appState.validationResults = [];
    updateStatusBar(0, 0);
    renderScreen(window._appState.currentScreen);
    toast(`Loaded ${file.name}`, 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
};

window._newFromTemplate = async function(template) {
  try {
    const data = await api('POST', '/document/new', { template });
    window._appState.currentDoc = data.document;
    window._appState.currentPath = null;
    window._appState.currentFileName = `New Overview (${template})`;
    document.getElementById('active-file-name').textContent = window._appState.currentFileName;
    document.getElementById('status-hint').textContent = 'New overview created â€” import or add tabs to get started';
    window._appState.validationResults = [];
    updateStatusBar(0, 0);
    renderScreen(window._appState.currentScreen);
    toast(`Created new ${template} overview`, 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
};

window._openImportModal = function() {
  document.getElementById('modal-import').style.display = 'flex';
  document.getElementById('import-path-input').focus();
};

function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.style.display = 'flex';
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.style.display = 'none';
}

window._runValidation = async function() {
  if (!window._appState.currentDoc) { toast('No overview loaded.', 'warn'); return; }
  try {
    const data = await api('POST', '/validate', undefined);
    window._appState.validationResults = data.results || [];
    updateStatusBar(data.warningCount, data.errorCount);
    applyValidationResults(data.results || []);
    if (window.renderImportExportValidationPanel) {
      window.renderImportExportValidationPanel(data.results || []);
    }
    const msg = data.errorCount > 0
      ? `${data.errorCount} error(s), ${data.warningCount} warning(s)`
      : data.warningCount > 0
        ? `${data.warningCount} warning(s) â€” no errors`
        : 'All checks passed';
    toast(msg, data.errorCount > 0 ? 'error' : data.warningCount > 0 ? 'warn' : 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
};

function updateStatusBar(warnings, errors) {
  const wEl = document.getElementById('status-warnings');
  const eEl = document.getElementById('status-errors');
  const wTxt = document.getElementById('status-warnings-text');
  const eTxt = document.getElementById('status-errors-text');
  wEl.style.display = warnings > 0 ? 'inline-flex' : 'none';
  eEl.style.display = errors > 0 ? 'inline-flex' : 'none';
  wTxt.textContent = `${warnings} warning${warnings !== 1 ? 's' : ''}`;
  eTxt.textContent = `${errors} error${errors !== 1 ? 's' : ''}`;
}

function openValidationPanel() {
  navigate('importexport');
  if (window._appState.validationResults.length > 0 && window.renderImportExportValidationPanel) {
    window.renderImportExportValidationPanel(window._appState.validationResults);
  }
  setTimeout(() => document.getElementById('ie-validation-panel')?.scrollIntoView({ block: 'center' }), 0);
}

function validationGroups(results) {
  const groups = {
    Tabs: [],
    Presets: [],
    Appearance: [],
    Columns: [],
    States: [],
    YAML: [],
    Other: [],
  };
  (results || []).forEach(result => {
    const code = result.code || '';
    const path = result.path || result.field || '';
    if (code.includes('TAB') || path.includes('tab')) groups.Tabs.push(result);
    else if (code.includes('PRESET') || path.includes('preset')) groups.Presets.push(result);
    else if (code.includes('COLOR') || code.includes('FLAG') || code.includes('BACKGROUND') || path.includes('appearance')) groups.Appearance.push(result);
    else if (code.includes('COLUMN') || path.includes('column')) groups.Columns.push(result);
    else if (code.includes('STATE') || path.includes('state')) groups.States.push(result);
    else if (code.includes('YAML') || code.includes('UNKNOWN') || path.includes('unknown')) groups.YAML.push(result);
    else groups.Other.push(result);
  });
  return groups;
}

function validationSeverityCounts(results) {
  return {
    errors: (results || []).filter(r => r.severity === 'error').length,
    warnings: (results || []).filter(r => r.severity === 'warning').length,
  };
}

// â”€â”€ Boot â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
document.addEventListener('DOMContentLoaded', () => {
  // Nav clicks
  document.querySelectorAll('.nav-item[data-screen]').forEach(el => {
    el.addEventListener('click', () => navigate(el.dataset.screen));
  });

  // Top bar buttons
  document.getElementById('btn-import').addEventListener('click', window._openImportModal);
  document.getElementById('btn-validate').addEventListener('click', window._runValidation);
  document.getElementById('btn-export').addEventListener('click', () => {
    navigate('importexport');
  });
  document.getElementById('btn-backup').addEventListener('click', () => {
    navigate('profiles');
  });
  document.getElementById('btn-help').addEventListener('click', () => {
    openModal('modal-help');
  });
  document.getElementById('btn-about').addEventListener('click', () => {
    openModal('modal-about');
  });
  document.getElementById('status-warnings').addEventListener('click', openValidationPanel);
  document.getElementById('status-errors').addEventListener('click', openValidationPanel);

  document.querySelectorAll('[data-close-modal]').forEach(btn => {
    btn.addEventListener('click', () => closeModal(btn.dataset.closeModal));
  });
  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.addEventListener('click', e => {
      if (e.target === e.currentTarget) e.currentTarget.style.display = 'none';
    });
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-backdrop').forEach(modal => {
        modal.style.display = 'none';
      });
    }
  });

  // Import modal
  document.getElementById('modal-import-close').addEventListener('click', () => {
    document.getElementById('modal-import').style.display = 'none';
  });
  document.getElementById('modal-import-cancel').addEventListener('click', () => {
    document.getElementById('modal-import').style.display = 'none';
  });
  document.getElementById('modal-import-confirm').addEventListener('click', () => {
    const file = document.getElementById('import-file-input').files?.[0];
    if (file) {
      document.getElementById('modal-import').style.display = 'none';
      window._loadFileContent(file);
      return;
    }
    const path = document.getElementById('import-path-input').value.trim();
    if (!path) { toast('Enter a file path.', 'warn'); return; }
    document.getElementById('modal-import').style.display = 'none';
    window._loadFile(path);
  });
  document.getElementById('import-path-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') document.getElementById('modal-import-confirm').click();
    if (e.key === 'Escape') document.getElementById('modal-import').style.display = 'none';
  });

  // Initial render
  navigate('dashboard');

  // Load existing document state from server on startup
  api('GET', '/document').then(data => {
    if (data.document) {
      window._appState.currentDoc = data.document;
      window._appState.currentPath = data.path;
      window._appState.currentFileName = data.path ? data.path.split(/[\\/]/).pop() : 'Loaded';
      document.getElementById('active-file-name').textContent = window._appState.currentFileName;
      renderScreen(window._appState.currentScreen);
    }
  }).catch(() => {});
});



