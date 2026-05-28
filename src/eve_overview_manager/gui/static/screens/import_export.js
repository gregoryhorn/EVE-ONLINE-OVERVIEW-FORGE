/* Import / Export screen */

let _pendingExport = null;

function renderImportExportScreen() {
  const doc = window._appState.currentDoc;
  const currentPath = window._appState.currentPath || '';
  const fileName = window._appState.currentFileName || 'No file loaded';
  return `
    <div class="section-header">Import / Export</div>
    <div class="import-export-screen">
      <div class="card">
        <div class="card-header">
          <div class="card-header-left">Workspace Folder</div>
          <span class="mini-status" id="ie-pref-status">Loading</span>
        </div>
        <label class="field-label">Default import/export folder</label>
        <input class="field-input" id="ie-folder" type="text" value="" placeholder="%USERPROFILE%\\Documents\\EVE\\Overview" />
        <div class="ie-actions">
          <button class="btn-secondary" id="ie-save-folder">Remember Folder</button>
        </div>
        <label class="field-label" style="margin-top:12px">SDE group names JSON</label>
        <input class="field-input" id="ie-group-names-path" type="text" value="" placeholder="C:\\...\\group_names.json" />
        <div class="ie-actions">
          <button class="btn-secondary" id="ie-save-group-names">Remember Group Names</button>
          <button class="btn-secondary" id="ie-clear-group-names">Clear</button>
        </div>
        <p class="ie-note">Exports never overwrite existing files. If a filename exists, the app writes a numbered copy.</p>
      </div>

      <div class="dashboard-grid">
        <div class="card">
          <div class="card-header">
            <div class="card-header-left">Import</div>
          </div>
          <label class="field-label">YAML or canonical JSON path</label>
          <input class="field-input" id="ie-import-path" type="text" value="${currentPath}" placeholder="C:\\...\\overview.yaml" />
          <label class="field-label" style="margin-top:12px">Browse local file</label>
          <input class="field-input" id="ie-import-file" type="file" accept=".yaml,.yml,.json" />
          <div class="ie-actions">
            <button class="btn-primary" id="ie-load-file">Load File</button>
          </div>
          <p class="ie-note">XML import is intentionally deferred. YAML is the supported EVE overview format.</p>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-header-left">Export Current Document</div>
            <span class="mini-status">${doc ? fileName : 'No document'}</span>
          </div>
          <label class="field-label">Base filename</label>
          <input class="field-input" id="ie-export-name" type="text" value="${_defaultExportName()}" />
          <div class="ie-actions">
            <button class="btn-primary" id="ie-export-yaml" ${doc ? '' : 'disabled'}>Review YAML Export</button>
            <button class="btn-secondary" id="ie-export-json" ${doc ? '' : 'disabled'}>Review JSON Export</button>
          </div>
          <div class="ie-output" id="ie-export-output">Review the destination before writing an export file.</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-header-left">Generator Spec</div>
          <span class="mini-status">Optional</span>
        </div>
        <div class="ie-two-col">
          <div>
            <label class="field-label">Generator spec path</label>
            <input class="field-input" id="ie-generator-spec" type="text" value="" placeholder="Path to a local generator JSON spec" />
          </div>
          <div>
            <label class="field-label">Output filename</label>
            <input class="field-input" id="ie-generator-output" type="text" value="generated.yaml" />
          </div>
        </div>
        <div class="ie-actions">
          <button class="btn-primary" id="ie-generate-yaml">Generate YAML</button>
          <button class="btn-secondary" id="ie-generate-json">Generate JSON</button>
        </div>
        <div class="ie-output" id="ie-generator-result">Generator output will also become the current loaded document.</div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-header-left">Validation</div>
          <button class="btn-secondary btn-sm" id="ie-run-validation" ${doc ? '' : 'disabled'}>Run Check</button>
        </div>
        <div id="ie-validation-panel">
          ${doc ? _renderValidationEmptyState() : '<div class="empty-state" style="padding:20px"><div class="empty-state-title">No document loaded</div><div class="empty-state-text">Load YAML or JSON before validating.</div></div>'}
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-header-left">Snapshots</div>
          <span class="mini-status">Local restore points</span>
        </div>
        <label class="field-label">Snapshot root folder</label>
        <input class="field-input" id="ie-snapshot-root" type="text" value="" placeholder=".tmp\\snapshots" />
        <label class="field-label" style="margin-top:12px">Notes</label>
        <input class="field-input" id="ie-snapshot-notes" type="text" value="Manual GUI snapshot" />
        <div class="ie-actions">
          <button class="btn-primary" id="ie-create-snapshot" ${doc ? '' : 'disabled'}>Create Snapshot</button>
          <button class="btn-secondary" id="ie-list-snapshots">Refresh List</button>
        </div>
        <div class="ie-output" id="ie-snapshot-output">Snapshots write canonical JSON plus a checksum manifest.</div>
        <div class="snapshot-list" id="ie-snapshot-list"></div>
      </div>
    </div>
  `;
}

function bindImportExportScreen() {
  _loadImportExportPreferences();
  document.getElementById('ie-save-folder')?.addEventListener('click', _rememberImportExportFolder);
  document.getElementById('ie-save-group-names')?.addEventListener('click', _rememberGroupNamesPath);
  document.getElementById('ie-clear-group-names')?.addEventListener('click', _clearGroupNamesPath);
  document.getElementById('ie-load-file')?.addEventListener('click', _loadImportExportFile);
  document.getElementById('ie-export-yaml')?.addEventListener('click', () => _reviewCurrentDocumentExport('yaml'));
  document.getElementById('ie-export-json')?.addEventListener('click', () => _reviewCurrentDocumentExport('json'));
  document.getElementById('ie-generate-yaml')?.addEventListener('click', () => _generateFromSpec('yaml'));
  document.getElementById('ie-generate-json')?.addEventListener('click', () => _generateFromSpec('json'));
  document.getElementById('ie-run-validation')?.addEventListener('click', () => window._runValidation());
  document.getElementById('ie-create-snapshot')?.addEventListener('click', _createSnapshot);
  document.getElementById('ie-list-snapshots')?.addEventListener('click', _listSnapshots);
}

async function _loadImportExportPreferences() {
  try {
    const data = await api('GET', '/preferences');
    document.getElementById('ie-folder').value = data.preferences.importExportFolder || '';
    document.getElementById('ie-group-names-path').value = data.preferences.groupNamesPath || '';
    document.getElementById('ie-pref-status').textContent = 'Ready';
  } catch (e) {
    document.getElementById('ie-pref-status').textContent = 'Unavailable';
  }
}

async function _rememberGroupNamesPath() {
  const groupNamesPath = document.getElementById('ie-group-names-path').value.trim();
  if (!groupNamesPath) { toast('Enter a group_names.json path.', 'warn'); return; }
  try {
    await api('PATCH', '/preferences', { groupNamesPath });
    refreshLivePreview();
    toast('Group names preference saved', 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _clearGroupNamesPath() {
  try {
    await api('PATCH', '/preferences', { groupNamesPath: null });
    document.getElementById('ie-group-names-path').value = '';
    refreshLivePreview();
    toast('Group names preference cleared', 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _rememberImportExportFolder() {
  const folder = document.getElementById('ie-folder').value.trim();
  if (!folder) { toast('Enter a folder path.', 'warn'); return; }
  try {
    await api('PATCH', '/preferences', { importExportFolder: folder });
    toast('Folder preference saved', 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

function _loadImportExportFile() {
  const file = document.getElementById('ie-import-file')?.files?.[0];
  if (file) {
    window._loadFileContent(file);
    return;
  }
  const path = document.getElementById('ie-import-path').value.trim();
  if (!path) { toast('Enter a file path.', 'warn'); return; }
  window._loadFile(path);
}

async function _reviewCurrentDocumentExport(format) {
  const folder = document.getElementById('ie-folder').value.trim();
  const name = document.getElementById('ie-export-name').value.trim();
  if (!folder || !name) { toast('Folder and filename are required.', 'warn'); return; }
  const path = _joinPath(folder, _withExtension(name, format));
  try {
    const preview = await api('POST', '/export/preview', { path });
    const validation = await _validationSnapshot();
    _pendingExport = { format, path: preview.outputPath };
    document.getElementById('ie-export-output').innerHTML = _renderExportReview(format, preview, validation);
    document.getElementById('ie-confirm-export')?.addEventListener('click', _confirmCurrentDocumentExport);
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _confirmCurrentDocumentExport() {
  if (!_pendingExport) { toast('Review export destination first.', 'warn'); return; }
  try {
    const data = await api('POST', `/export/${_pendingExport.format}`, { path: _pendingExport.path });
    document.getElementById('ie-export-output').textContent = `Wrote ${data.outputPath}`;
    _pendingExport = null;
    toast(`Exported ${data.format.toUpperCase()}`, 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _validationSnapshot() {
  if (!window._appState.currentDoc) return { errorCount: 0, warningCount: 0, checked: false };
  try {
    const data = await api('POST', '/validate');
    window._appState.validationResults = data.results || [];
    updateStatusBar(data.warningCount, data.errorCount);
    if (window.renderImportExportValidationPanel) window.renderImportExportValidationPanel(data.results || []);
    return { errorCount: data.errorCount, warningCount: data.warningCount, checked: true };
  } catch {
    return { errorCount: 0, warningCount: 0, checked: false };
  }
}

function _renderExportReview(format, preview, validation) {
  const status = validation.checked
    ? validation.errorCount > 0
      ? `${validation.errorCount} error(s), ${validation.warningCount} warning(s)`
      : `${validation.warningCount} warning(s), no errors`
    : 'Validation not available';
  return `
    <div class="export-review">
      <div><strong>${format.toUpperCase()} export review</strong></div>
      <div>Requested: <span>${escapeHtml(preview.requestedPath)}</span></div>
      <div>Will write: <span>${escapeHtml(preview.outputPath)}</span></div>
      ${preview.wouldRename ? '<div class="export-review-warn">Existing file detected. A numbered filename will be used.</div>' : ''}
      <div>Validation: <span>${escapeHtml(status)}</span></div>
      <button class="btn-primary btn-sm" id="ie-confirm-export" type="button" ${validation.errorCount > 0 ? 'disabled' : ''}>Confirm Export</button>
    </div>
  `;
}

async function _generateFromSpec(format) {
  const folder = document.getElementById('ie-folder').value.trim();
  const specPath = document.getElementById('ie-generator-spec').value.trim();
  const name = document.getElementById('ie-generator-output').value.trim();
  if (!folder || !specPath || !name) { toast('Folder, spec path, and output filename are required.', 'warn'); return; }
  try {
    const data = await api('POST', '/import/generator', {
      specPath,
      outputPath: _joinPath(folder, _withExtension(name, format)),
      outputFormat: format,
    });
    window._appState.currentDoc = data.document;
    window._appState.currentPath = data.outputPath;
    window._appState.currentFileName = data.outputPath.split(/[\\/]/).pop();
    document.getElementById('active-file-name').textContent = window._appState.currentFileName;
    document.getElementById('ie-generator-result').textContent = `Wrote ${data.outputPath}`;
    renderScreen('importexport');
    toast(`Generated ${format.toUpperCase()}`, 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

function _defaultExportName() {
  const name = window._appState.currentFileName || 'overview.yaml';
  return name.replace(/\.(json|ya?ml)$/i, '.yaml');
}

function _withExtension(name, format) {
  const ext = format === 'json' ? '.json' : '.yaml';
  return name.replace(/\.(json|ya?ml)$/i, '') + ext;
}

function _joinPath(folder, name) {
  const sep = folder.includes('\\') ? '\\' : '/';
  return folder.replace(/[\\/]+$/, '') + sep + name;
}

async function _createSnapshot() {
  const snapshotRoot = document.getElementById('ie-snapshot-root').value.trim();
  const notes = document.getElementById('ie-snapshot-notes').value.trim();
  if (!snapshotRoot) { toast('Enter a snapshot root folder.', 'warn'); return; }
  try {
    const data = await api('POST', '/snapshots/create', {
      snapshotRoot,
      operationType: 'gui-manual',
      notes: notes || null,
    });
    document.getElementById('ie-snapshot-output').textContent = `Created ${data.snapshot.manifestPath}`;
    await _listSnapshots();
    toast('Snapshot created', 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _listSnapshots() {
  const snapshotRoot = document.getElementById('ie-snapshot-root').value.trim();
  const list = document.getElementById('ie-snapshot-list');
  if (!snapshotRoot) { toast('Enter a snapshot root folder.', 'warn'); return; }
  try {
    const data = await api('GET', `/snapshots?snapshotRoot=${encodeURIComponent(snapshotRoot)}`);
    const snapshots = data.snapshots || [];
    list.innerHTML = snapshots.length
      ? snapshots.slice(0, 5).map(_renderSnapshotRow).join('')
      : '<div class="empty-state" style="padding:14px"><div class="empty-state-title">No snapshots found</div></div>';
  } catch (e) {
    toast(e.message, 'error');
  }
}

function _renderSnapshotRow(snapshot) {
  return `
    <div class="snapshot-row">
      <div>
        <div class="snapshot-row-title">${escapeHtml(snapshot.operationType || 'snapshot')}</div>
        <div class="snapshot-row-path">${escapeHtml(snapshot.manifestPath || '')}</div>
      </div>
      <div class="snapshot-row-time">${escapeHtml(snapshot.createdAt || '')}</div>
    </div>
  `;
}

function _renderValidationEmptyState() {
  return `
    <div class="empty-state" style="padding:20px">
      <div class="empty-state-title">Not checked</div>
      <div class="empty-state-text">Run validation to inspect YAML structure, tabs, presets, states, appearance, and columns.</div>
    </div>
  `;
}

window.renderImportExportValidationPanel = function(results) {
  const panel = document.getElementById('ie-validation-panel');
  if (!panel) return;
  const counts = validationSeverityCounts(results);
  const groups = validationGroups(results);
  if (!results || results.length === 0) {
    panel.innerHTML = `
      <div class="validation-summary validation-summary--ok">
        <strong>All checks passed</strong>
        <span>No validation warnings or errors.</span>
      </div>
    `;
    return;
  }
  panel.innerHTML = `
    <div class="validation-summary ${counts.errors ? 'validation-summary--error' : 'validation-summary--warn'}">
      <strong>${counts.errors} errors / ${counts.warnings} warnings</strong>
      <span>Review grouped results before export or profile work.</span>
    </div>
    <div class="validation-groups">
      ${Object.entries(groups).filter(([, items]) => items.length > 0).map(([name, items]) => _renderValidationGroup(name, items)).join('')}
    </div>
  `;
};

function _renderValidationGroup(name, items) {
  const counts = validationSeverityCounts(items);
  const badge = counts.errors ? `${counts.errors} error${counts.errors === 1 ? '' : 's'}` : `${counts.warnings} warning${counts.warnings === 1 ? '' : 's'}`;
  const badgeClass = counts.errors ? 'val-badge--error' : 'val-badge--warn';
  return `
    <div class="validation-group">
      <div class="validation-group-header">
        <span>${escapeHtml(name)}</span>
        <span class="val-badge ${badgeClass}">${badge}</span>
      </div>
      ${items.map(_renderValidationIssue).join('')}
    </div>
  `;
}

function _renderValidationIssue(result) {
  const severityClass = result.severity === 'error' ? 'validation-issue--error' : 'validation-issue--warn';
  return `
    <div class="validation-issue ${severityClass}">
      <div class="validation-issue-code">${escapeHtml(result.code || 'UNKNOWN')}</div>
      <div class="validation-issue-message">${escapeHtml(result.message || '')}</div>
      <div class="validation-issue-path">${escapeHtml(result.path || '')}</div>
      ${result.suggestedFix ? `<div class="validation-issue-fix">${escapeHtml(result.suggestedFix)}</div>` : ''}
    </div>
  `;
}
