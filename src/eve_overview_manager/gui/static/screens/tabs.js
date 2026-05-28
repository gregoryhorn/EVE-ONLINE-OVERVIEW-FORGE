/* Tabs screen */

// ── State ────────────────────────────────────────────────────
let _tabsState = {
  tabs: [],
  presets: [],
  selectedSlot: null,
};

// ── Main render ──────────────────────────────────────────────
function renderTabsScreen() {
  return `
<div class="section-header">Tabs</div>
<div class="tabs-layout">
  <div class="tabs-list-panel" id="tabs-list-panel">
    <div id="tabs-pill-list"></div>
    <button class="btn-add-tab" id="btn-add-tab">
      <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd"/></svg>
      Add Tab
    </button>
  </div>
  <div class="tabs-editor-panel" id="tabs-editor-panel">
    <div class="tabs-editor-empty">Select a tab to edit its settings.</div>
  </div>
</div>
  `;
}

function renderTabPills(tabs, selectedSlot) {
  if (tabs.length === 0) {
    return `<div style="padding:16px;font-size:12px;color:var(--text-muted)">No tabs defined. Click Add Tab to create one.</div>`;
  }
  return tabs.map(tab => {
    const color = argbToHex(tab.colorARGB);
    const active = tab.slot === selectedSlot;
    return `
      <div class="tab-pill ${active ? 'tab-pill--active' : ''}" data-slot="${tab.slot}" draggable="true">
        <span class="tab-pill-swatch" style="background:${color}"></span>
        <span class="tab-pill-label">${tab.label || `Tab ${tab.slot}`}</span>
        <span class="tab-pill-slot">Slot ${tab.slot}</span>
      </div>
    `;
  }).join('');
}

function renderTabEditor(tab, presets) {
  if (!tab) {
    return `<div class="tabs-editor-empty">Select a tab to edit its settings.</div>`;
  }
  const color = argbToHex(tab.colorARGB);
  const presetOptions = presets.map(p =>
    `<option value="${p.id}" ${tab.overviewPresetRef === p.id ? 'selected' : ''}>${p.name || p.id}</option>`
  ).join('');
  const emptyOpt = `<option value="">— None —</option>`;

  return `
    <div class="tab-editor-form">
      <div class="tab-editor-header">
        <div class="tab-editor-color-swatch" style="background:${color}" id="editor-swatch"></div>
        <h3 class="tab-editor-title">${tab.label || `Tab ${tab.slot}`}</h3>
        <span class="tab-editor-slot-badge">Slot ${tab.slot}</span>
      </div>

      <div class="field-group">
        <label class="field-label">Tab Name</label>
        <input class="field-input" type="text" id="tab-name" value="${tab.label || ''}" maxlength="12" placeholder="e.g. PVP, Mining, AFK" />
        <div class="field-hint">Max 12 characters. Shown as the tab label in EVE.</div>
      </div>

      <div class="field-group">
        <label class="field-label">Tab Color</label>
        <div class="color-picker-row">
          <input type="color" id="tab-color-picker" value="${color}" class="color-native-picker" />
          <input class="field-input color-hex-input" type="text" id="tab-color-hex" value="${color}" maxlength="7" placeholder="#RRGGBB" />
          <div class="color-preview-swatch" id="color-live-swatch" style="background:${color}"></div>
        </div>
        <div class="field-hint">ARGB stored as FF + RGB. Alpha is always 100%.</div>
      </div>

      <div class="field-group">
        <label class="field-label">Overview Preset</label>
        <select class="field-select" id="tab-overview-preset">
          ${emptyOpt}${presetOptions}
        </select>
        <div class="field-hint">Which entities appear in the overview for this tab.</div>
      </div>

      <div class="field-group">
        <label class="field-label">Bracket Preset</label>
        <select class="field-select" id="tab-bracket-preset">
          ${emptyOpt}${presetOptions}
        </select>
        <div class="field-hint">Which brackets appear in space for this tab.</div>
      </div>

      <div class="tab-editor-actions">
        <button class="btn-secondary" id="btn-duplicate-tab">Duplicate</button>
        <button class="btn-danger" id="btn-delete-tab">Delete Tab</button>
      </div>
    </div>
  `;
}

// ── Helpers ──────────────────────────────────────────────────
function argbToHex(argb) {
  if (!argb || argb.length < 6) return '#00c8f0';
  const rgb = argb.length === 8 ? argb.slice(2) : argb;
  return '#' + rgb.toLowerCase();
}

function hexToArgb(hex) {
  const clean = hex.replace('#', '');
  if (clean.length !== 6) return null;
  return 'FF' + clean.toUpperCase();
}

// ── Load + bind ──────────────────────────────────────────────
async function loadTabsScreen() {
  try {
    const data = await api('GET', '/document/tabs');
    _tabsState.tabs = data.tabs || [];
    _tabsState.presets = data.presets || [];
    if (_tabsState.selectedSlot === null && _tabsState.tabs.length > 0) {
      _tabsState.selectedSlot = _tabsState.tabs[0].slot;
    }
    _refreshTabsUI();
  } catch (e) {
    document.getElementById('center-panel').innerHTML = `
      <div class="section-header">Tabs</div>
      <div class="empty-state" style="margin:32px"><div class="empty-state-title">No overview loaded</div><div class="empty-state-text">Load or create an overview from the Dashboard first.</div></div>
    `;
  }
}

function _refreshTabsUI() {
  const listEl = document.getElementById('tabs-pill-list');
  const editorEl = document.getElementById('tabs-editor-panel');
  if (!listEl || !editorEl) return;

  const tab = _tabsState.tabs.find(t => t.slot === _tabsState.selectedSlot) || null;
  listEl.innerHTML = renderTabPills(_tabsState.tabs, _tabsState.selectedSlot);
  editorEl.innerHTML = renderTabEditor(tab, _tabsState.presets);

  _bindTabPills();
  if (tab) _bindTabEditor(tab);
  _refreshLivePreviewFromState();
}

function _bindTabPills() {
  document.querySelectorAll('.tab-pill[data-slot]').forEach(el => {
    el.addEventListener('click', () => {
      _tabsState.selectedSlot = parseInt(el.dataset.slot, 10);
      _refreshTabsUI();
    });
  });

  // Drag-to-reorder
  let dragSlot = null;
  document.querySelectorAll('.tab-pill[draggable]').forEach(el => {
    el.addEventListener('dragstart', () => { dragSlot = parseInt(el.dataset.slot, 10); el.style.opacity = '0.5'; });
    el.addEventListener('dragend', () => { el.style.opacity = ''; dragSlot = null; });
    el.addEventListener('dragover', e => { e.preventDefault(); });
    el.addEventListener('drop', async () => {
      const targetSlot = parseInt(el.dataset.slot, 10);
      if (dragSlot === null || dragSlot === targetSlot) return;
      const order = _tabsState.tabs.map(t => t.slot);
      const fromIdx = order.indexOf(dragSlot);
      const toIdx = order.indexOf(targetSlot);
      order.splice(fromIdx, 1);
      order.splice(toIdx, 0, dragSlot);
      try {
        const data = await api('POST', '/document/tabs/reorder', { order });
        _tabsState.tabs = data.tabs || [];
        _tabsState.selectedSlot = _tabsState.tabs.find(t => t.label === _tabsState.tabs[toIdx]?.label)?.slot ?? _tabsState.selectedSlot;
        _refreshTabsUI();
      } catch(e) { toast(e.message, 'error'); }
    });
  });

  // Add tab button
  const addBtn = document.getElementById('btn-add-tab');
  if (addBtn) {
    addBtn.addEventListener('click', async () => {
      try {
        const data = await api('POST', '/document/tabs', {});
        _tabsState.tabs = data.tabs || [];
        _tabsState.selectedSlot = data.newSlot;
        _refreshTabsUI();
        toast('Tab added', 'success');
      } catch(e) { toast(e.message, 'error'); }
    });
  }
}

function _bindTabEditor(tab) {
  const slot = tab.slot;

  // Live name update
  const nameEl = document.getElementById('tab-name');
  nameEl?.addEventListener('input', async () => {
    const val = nameEl.value;
    document.querySelector('.tab-editor-title').textContent = val || `Tab ${slot}`;
    await _patchTab(slot, { label: val });
  });

  // Color picker sync
  const pickerEl = document.getElementById('tab-color-picker');
  const hexEl = document.getElementById('tab-color-hex');
  const swatchEl = document.getElementById('color-live-swatch');
  const headerSwatchEl = document.getElementById('editor-swatch');

  function applyColor(hex) {
    if (!/^#[0-9a-fA-F]{6}$/.test(hex)) return;
    if (swatchEl) swatchEl.style.background = hex;
    if (headerSwatchEl) headerSwatchEl.style.background = hex;
    const argb = hexToArgb(hex);
    if (argb) _patchTab(slot, { colorARGB: argb });
    _refreshLivePreviewFromState();
  }

  pickerEl?.addEventListener('input', () => {
    if (hexEl) hexEl.value = pickerEl.value;
    applyColor(pickerEl.value);
  });
  hexEl?.addEventListener('change', () => {
    const hex = hexEl.value.startsWith('#') ? hexEl.value : '#' + hexEl.value;
    if (pickerEl) pickerEl.value = hex;
    applyColor(hex);
  });

  // Preset dropdowns
  document.getElementById('tab-overview-preset')?.addEventListener('change', async (e) => {
    await _patchTab(slot, { overviewPresetRef: e.target.value });
  });
  document.getElementById('tab-bracket-preset')?.addEventListener('change', async (e) => {
    await _patchTab(slot, { bracketPresetRef: e.target.value });
  });

  // Duplicate
  document.getElementById('btn-duplicate-tab')?.addEventListener('click', async () => {
    try {
      const data = await api('POST', `/document/tabs/${slot}/duplicate`, {});
      _tabsState.tabs = data.tabs || [];
      _tabsState.selectedSlot = data.newSlot;
      _refreshTabsUI();
      toast('Tab duplicated', 'success');
    } catch(e) { toast(e.message, 'error'); }
  });

  // Delete
  document.getElementById('btn-delete-tab')?.addEventListener('click', async () => {
    if (!confirm(`Delete tab "${tab.label || `Tab ${slot}`}"?`)) return;
    try {
      const data = await api('DELETE', `/document/tabs/${slot}`);
      _tabsState.tabs = data.tabs || [];
      _tabsState.selectedSlot = _tabsState.tabs[0]?.slot ?? null;
      _refreshTabsUI();
      toast('Tab deleted', 'warn');
    } catch(e) { toast(e.message, 'error'); }
  });
}

async function _patchTab(slot, fields) {
  try {
    const data = await api('PATCH', `/document/tabs/${slot}`, { slot, ...fields });
    _tabsState.tabs = data.tabs || [];
    _refreshLivePreviewFromState();
  } catch(e) { toast(e.message, 'error'); }
}

function _refreshLivePreviewFromState() {
  // Sync _appState.currentDoc.tabs so renderLivePreview uses real data
  if (window._appState.currentDoc) {
    window._appState.currentDoc.tabs = _tabsState.tabs;
  }
  const right = document.getElementById('right-panel');
  if (right) right.innerHTML = renderLivePreview(window._appState.currentDoc);
  bindLivePreview();
  refreshLivePreview();
}

function renderTabEditor(tab, presets) {
  if (!tab) {
    return `<div class="tabs-editor-empty">Select a tab to edit its settings.</div>`;
  }
  const color = argbToHex(tab.colorARGB);
  const overviewPresetOptions = presets.map(p =>
    `<option value="${p.id}" ${tab.overviewPresetRef === p.id ? 'selected' : ''}>${p.name || p.id}</option>`
  ).join('');
  const bracketPresetOptions = presets.map(p =>
    `<option value="${p.id}" ${tab.bracketPresetRef === p.id ? 'selected' : ''}>${p.name || p.id}</option>`
  ).join('');
  const emptyOpt = `<option value="">None</option>`;

  return `
    <div class="tab-editor-form">
      <div class="tab-editor-header">
        <div class="tab-editor-color-swatch" style="background:${color}" id="editor-swatch"></div>
        <h3 class="tab-editor-title">${tab.label || `Tab ${tab.slot}`}</h3>
        <span class="tab-editor-slot-badge">Slot ${tab.slot}</span>
      </div>

      <div class="field-group">
        <label class="field-label">Tab Name</label>
        <input class="field-input" type="text" id="tab-name" value="${tab.label || ''}" maxlength="12" placeholder="e.g. PVP, Mining, AFK" />
        <div class="field-hint">Max 12 characters. Shown as the tab label in EVE.</div>
      </div>

      <div class="field-group">
        <label class="field-label">Tab Color</label>
        <div class="color-picker-row">
          <input type="color" id="tab-color-picker" value="${color}" class="color-native-picker" />
          <input class="field-input color-hex-input" type="text" id="tab-color-hex" value="${color}" maxlength="7" placeholder="#RRGGBB" />
          <div class="color-preview-swatch" id="color-live-swatch" style="background:${color}"></div>
        </div>
        <div class="field-hint">ARGB stored as FF + RGB. Alpha is always 100%.</div>
      </div>

      <div class="field-group">
        <label class="field-label">Overview Preset</label>
        <select class="field-select" id="tab-overview-preset">
          ${emptyOpt}${overviewPresetOptions}
        </select>
        <div class="field-hint">Controls which rows appear in the overview table for this tab.</div>
      </div>

      <div class="field-group">
        <label class="field-label">Bracket Preset</label>
        <select class="field-select" id="tab-bracket-preset">
          ${emptyOpt}${bracketPresetOptions}
        </select>
        <div class="field-hint">Controls in-space brackets. It does not control the overview table preview.</div>
      </div>

      <div class="tab-workflow-actions">
        <button class="btn-secondary" id="btn-edit-overview-preset" ${tab.overviewPresetRef ? '' : 'disabled'}>Edit Overview Preset</button>
        <button class="btn-secondary" id="btn-edit-bracket-preset" ${tab.bracketPresetRef ? '' : 'disabled'}>Inspect Bracket Preset</button>
      </div>

      <div class="tab-editor-actions">
        <button class="btn-secondary" id="btn-duplicate-tab">Duplicate</button>
        <button class="btn-danger" id="btn-delete-tab">Delete Tab</button>
      </div>
    </div>
  `;
}

function _bindTabEditor(tab) {
  const slot = tab.slot;

  const nameEl = document.getElementById('tab-name');
  nameEl?.addEventListener('input', async () => {
    const val = nameEl.value;
    document.querySelector('.tab-editor-title').textContent = val || `Tab ${slot}`;
    await _patchTab(slot, { label: val });
  });

  const pickerEl = document.getElementById('tab-color-picker');
  const hexEl = document.getElementById('tab-color-hex');
  const swatchEl = document.getElementById('color-live-swatch');
  const headerSwatchEl = document.getElementById('editor-swatch');

  function applyColor(hex) {
    if (!/^#[0-9a-fA-F]{6}$/.test(hex)) return;
    if (swatchEl) swatchEl.style.background = hex;
    if (headerSwatchEl) headerSwatchEl.style.background = hex;
    const argb = hexToArgb(hex);
    if (argb) _patchTab(slot, { colorARGB: argb });
    _refreshLivePreviewFromState();
  }

  pickerEl?.addEventListener('input', () => {
    if (hexEl) hexEl.value = pickerEl.value;
    applyColor(pickerEl.value);
  });
  hexEl?.addEventListener('change', () => {
    const hex = hexEl.value.startsWith('#') ? hexEl.value : '#' + hexEl.value;
    if (pickerEl) pickerEl.value = hex;
    applyColor(hex);
  });

  document.getElementById('tab-overview-preset')?.addEventListener('change', async (e) => {
    await _patchTab(slot, { overviewPresetRef: e.target.value });
  });
  document.getElementById('tab-bracket-preset')?.addEventListener('change', async (e) => {
    await _patchTab(slot, { bracketPresetRef: e.target.value });
  });
  document.getElementById('btn-edit-overview-preset')?.addEventListener('click', () => {
    if (tab.overviewPresetRef && window._openPresetInEditor) window._openPresetInEditor(tab.overviewPresetRef);
  });
  document.getElementById('btn-edit-bracket-preset')?.addEventListener('click', () => {
    if (tab.bracketPresetRef && window._openPresetInEditor) window._openPresetInEditor(tab.bracketPresetRef);
  });

  document.getElementById('btn-duplicate-tab')?.addEventListener('click', async () => {
    try {
      const data = await api('POST', `/document/tabs/${slot}/duplicate`, {});
      _tabsState.tabs = data.tabs || [];
      _tabsState.selectedSlot = data.newSlot;
      _refreshTabsUI();
      toast('Tab duplicated', 'success');
    } catch(e) { toast(e.message, 'error'); }
  });

  document.getElementById('btn-delete-tab')?.addEventListener('click', async () => {
    if (!confirm(`Delete tab "${tab.label || `Tab ${slot}`}"?`)) return;
    try {
      const data = await api('DELETE', `/document/tabs/${slot}`);
      _tabsState.tabs = data.tabs || [];
      _tabsState.selectedSlot = _tabsState.tabs[0]?.slot ?? null;
      _refreshTabsUI();
      toast('Tab deleted', 'warn');
    } catch(e) { toast(e.message, 'error'); }
  });
}

function bindTabsScreen() {
  loadTabsScreen();
}
