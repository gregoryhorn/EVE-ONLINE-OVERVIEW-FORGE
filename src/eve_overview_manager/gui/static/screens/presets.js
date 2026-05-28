/* Presets screen */

// ── EVE group categories (common ones shown in overview presets) ──
let EVE_GROUPS = [
  // Ships
  { id: 'frigate',         gids: [25],                    label: 'Frigate',              cat: 'Ships' },
  { id: 'destroyer',       gids: [420],                   label: 'Destroyer',            cat: 'Ships' },
  { id: 'cruiser',         gids: [26],                    label: 'Cruiser',              cat: 'Ships' },
  { id: 'battlecruiser',   gids: [419],                   label: 'Battlecruiser',        cat: 'Ships' },
  { id: 'battleship',      gids: [27],                    label: 'Battleship',           cat: 'Ships' },
  { id: 'carrier',         gids: [547],                   label: 'Carrier',              cat: 'Ships' },
  { id: 'dreadnought',     gids: [485],                   label: 'Dreadnought',          cat: 'Ships' },
  { id: 'supercarrier',    gids: [659],                   label: 'Supercarrier',         cat: 'Ships' },
  { id: 'titan',           gids: [30],                    label: 'Titan',                cat: 'Ships' },
  { id: 'hauler',          gids: [28],                    label: 'Hauler / Industrial',  cat: 'Ships' },
  { id: 'freighter',       gids: [513],                   label: 'Freighter',            cat: 'Ships' },
  { id: 'capsule',         gids: [29],                    label: 'Capsule',              cat: 'Ships' },
  { id: 'shuttle',         gids: [31],                    label: 'Shuttle',              cat: 'Ships' },
  { id: 'mining_barge',    gids: [463],                   label: 'Mining Barge',         cat: 'Ships' },
  { id: 'exhumer',         gids: [543],                   label: 'Exhumer',              cat: 'Ships' },
  { id: 'recon',           gids: [833],                   label: 'Recon Ship',           cat: 'Ships' },
  { id: 'hac',             gids: [358],                   label: 'Heavy Assault Cruiser',cat: 'Ships' },
  { id: 'logi',            gids: [832],                   label: 'Logistics',            cat: 'Ships' },
  { id: 'interceptor',     gids: [831],                   label: 'Interceptor',          cat: 'Ships' },
  { id: 'hic',             gids: [894],                   label: 'Heavy Interdictor',    cat: 'Ships' },
  { id: 'dic',             gids: [541],                   label: 'Interdictor',          cat: 'Ships' },
  { id: 'fax',             gids: [1538],                  label: 'Force Auxiliary',      cat: 'Ships' },
  { id: 'rorqual',         gids: [883],                   label: 'Rorqual',              cat: 'Ships' },
  // NPCs
  { id: 'npc_frigate',     gids: [185],                   label: 'NPC Frigate',          cat: 'NPCs' },
  { id: 'npc_cruiser',     gids: [186],                   label: 'NPC Cruiser',          cat: 'NPCs' },
  { id: 'npc_battleship',  gids: [187],                   label: 'NPC Battleship',       cat: 'NPCs' },
  { id: 'npc_industrial',  gids: [188],                   label: 'NPC Industrial',       cat: 'NPCs' },
  { id: 'npc_hauler',      gids: [189],                   label: 'NPC Hauler',           cat: 'NPCs' },
  // Drones / Fighters
  { id: 'combat_drone',    gids: [100],                   label: 'Combat Drone',         cat: 'Drones & Fighters' },
  { id: 'mining_drone',    gids: [101],                   label: 'Mining Drone',         cat: 'Drones & Fighters' },
  { id: 'ewar_drone',      gids: [639],                   label: 'Electronic Warfare Drone', cat: 'Drones & Fighters' },
  { id: 'logistic_drone',  gids: [640],                   label: 'Logistic Drone',       cat: 'Drones & Fighters' },
  { id: 'web_drone',       gids: [641],                   label: 'Stasis Webifying Drone', cat: 'Drones & Fighters' },
  { id: 'neut_drone',      gids: [544],                   label: 'Energy Neutralizer Drone', cat: 'Drones & Fighters' },
  { id: 'salvage_drone',   gids: [1159],                  label: 'Salvage Drone',        cat: 'Drones & Fighters' },
  { id: 'light_fighter',   gids: [1652],                  label: 'Light Fighter',        cat: 'Drones & Fighters' },
  { id: 'heavy_fighter',   gids: [1653],                  label: 'Heavy Fighter',        cat: 'Drones & Fighters' },
  { id: 'support_fighter', gids: [1537],                  label: 'Support Fighter',      cat: 'Drones & Fighters' },
  { id: 'fighter_bomber',  gids: [1023],                  label: 'Fighter Bomber',       cat: 'Drones & Fighters' },
  // Structures
  { id: 'citadel',         gids: [1657],                  label: 'Citadel',              cat: 'Structures' },
  { id: 'ec',              gids: [1404],                  label: 'Engineering Complex',  cat: 'Structures' },
  { id: 'refinery',        gids: [1406],                  label: 'Refinery',             cat: 'Structures' },
  { id: 'upwell_jump',     gids: [1408],                  label: 'Upwell Jump Bridge',   cat: 'Structures' },
  { id: 'sovereignty_hub', gids: [1012],                  label: 'Sovereignty Hub',      cat: 'Structures' },
  { id: 'pos',             gids: [365],                   label: 'POS Tower',            cat: 'Structures' },
  { id: 'stargate',        gids: [10],                    label: 'Stargate',             cat: 'Structures' },
  { id: 'station',         gids: [15],                    label: 'Station',              cat: 'Structures' },
  // Deployables
  { id: 'bubble',          gids: [1082],                  label: 'Interdiction Sphere',  cat: 'Deployables' },
  { id: 'mobile_depot',    gids: [1246],                  label: 'Mobile Depot',         cat: 'Deployables' },
  { id: 'mobile_siphon',   gids: [1247],                  label: 'Mobile Siphon',        cat: 'Deployables' },
  { id: 'cyno_array',      gids: [838],                   label: 'Cynosural Generator Array', cat: 'Deployables' },
  { id: 'upwell_cyno',     gids: [2017],                  label: 'Upwell Cyno Beacon',   cat: 'Deployables' },
  // Celestials / Misc
  { id: 'asteroid',        gids: [9],                     label: 'Asteroid',             cat: 'Celestials' },
  { id: 'beacon',          gids: [310],                   label: 'Beacon',               cat: 'Celestials' },
  { id: 'wormhole',        gids: [988],                   label: 'Wormhole',             cat: 'Celestials' },
  { id: 'wreck',           gids: [12],                    label: 'Wreck',                cat: 'Celestials' },
  { id: 'cargo_container', gids: [12],                    label: 'Cargo Container',      cat: 'Celestials' },
];

// ── EVE states reference ─────────────────────────────────────
const EVE_STATES = [
  { id: 9,  label: 'Pilot has a security status below -5', color: '#ff6a00', desc: 'Security status below -5' },
  { id: 10, label: 'Pilot has a security status below 0', color: '#ffc000', desc: 'Security status below 0' },
  { id: 11, label: 'Pilot is in your fleet', color: '#8a2cff', desc: 'In your fleet' },
  { id: 12, label: 'Pilot is in your Capsuleer corporation', color: '#28b928', desc: 'Same capsuleer corporation' },
  { id: 13, label: 'Pilot is at war with your corporation/alliance', color: '#7d2f2f', desc: 'War target from corporation/alliance war' },
  { id: 14, label: 'Pilot is in your alliance', color: '#2878ff', desc: 'Same alliance' },
  { id: 15, label: 'Pilot has Excellent Standing.', color: '#2878ff', desc: 'Excellent standing' },
  { id: 16, label: 'Pilot has Good Standing.', color: '#2878ff', desc: 'Good standing' },
  { id: 17, label: 'Pilot has Neutral Standing', color: '#d8d8d8', desc: 'Neutral standing' },
  { id: 18, label: 'Pilot has Bad Standing.', color: '#ff6a00', desc: 'Bad standing' },
  { id: 19, label: 'Pilot has Terrible Standing.', color: '#d80000', desc: 'Terrible standing' },
  { id: 20, label: 'Pilot has No Standing.', color: '#d8d8d8', desc: 'No standing set' },
  { id: 21, label: 'Pilot (agent) is interactable', color: '#2878ff', desc: 'Agent is interactable' },
  { id: 36, label: 'Pilot is a suspect', color: '#8a6500', desc: 'Suspect timer active' },
  { id: 37, label: 'Pilot is a criminal', color: '#5a0000', desc: 'Criminal timer active' },
  { id: 44, label: 'Pilot is at war with your militia', color: '#7d2f2f', desc: 'Faction warfare militia target' },
  { id: 45, label: 'Pilot is in your militia or allied to your militia', color: '#8a2cff', desc: 'Friendly or allied militia' },
  { id: 48, label: 'Pilot is an ally in one or more of your wars', color: '#2878ff', desc: 'Ally in one or more wars' },
  { id: 49, label: 'Pilot is an ally in one or more of your wars', color: '#2878ff', desc: 'Ally in one or more wars' },
  { id: 50, label: 'Pilot is a suspect', color: '#8a6500', desc: 'Suspect timer active' },
  { id: 51, label: 'Pilot is a criminal', color: '#5a0000', desc: 'Criminal timer active' },
  { id: 52, label: 'Pilot has a limited engagement with you', color: '#007c78', desc: 'Limited engagement with you' },
  { id: 53, label: 'Pilot has a kill right on them that you can activate', color: '#ff6a00', desc: 'Kill right you can activate' },
  { id: 66, label: 'Pilot is in your Non Capsuleer corporation', color: '#28b928', desc: 'Same non-capsuleer corporation' },
  { id: 68, label: 'Pilot has retribution timer', color: '#8a6500', desc: 'Retribution timer' },
];

// ── Screen state ─────────────────────────────────────────────
let _presetsState = {
  presets: [],
  tabs: [],
  selectedId: null,
  groupQuery: '',
  groupCatalogLoaded: false,
};

// ── Main render ──────────────────────────────────────────────
function renderPresetsScreen() {
  return `
<div class="section-header">Presets</div>
<div class="presets-layout">
  <div class="presets-list-panel" id="presets-list-panel">
    <div id="presets-card-list"></div>
    <button class="btn-add-tab" id="btn-add-preset">
      <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd"/></svg>
      Add Preset
    </button>
  </div>
  <div class="presets-editor-panel" id="presets-editor-panel">
    <div class="tabs-editor-empty">Select a preset to edit it.</div>
  </div>
</div>
  `;
}

function renderPresetCards(presets, selectedId) {
  if (presets.length === 0) {
    return `<div style="padding:16px;font-size:12px;color:var(--text-muted)">No presets defined. Click Add Preset to create one.</div>`;
  }
  return presets.map(p => {
    const active = p.id === selectedId;
    const groupCount = (p.groups || []).length;
    const stateCount = (p.alwaysShownStates || []).length + (p.filteredStates || []).length;
    return `
      <div class="preset-card ${active ? 'preset-card--active' : ''}" data-id="${p.id}">
        <div class="preset-card-name">${p.name || p.id}</div>
        <div class="preset-card-meta">
          <span>${groupCount} group${groupCount !== 1 ? 's' : ''}</span>
          <span>·</span>
          <span>${stateCount} state${stateCount !== 1 ? 's' : ''}</span>
        </div>
      </div>
    `;
  }).join('');
}

function renderPresetEditor(preset, tabs = []) {
  if (!preset) return `<div class="tabs-editor-empty">Select a preset to edit it.</div>`;

  const groups = new Set((preset.groups || []).map(Number));
  const alwaysShown = preset.alwaysShownStates || [];
  const filtered = preset.filteredStates || [];
  const usedByTabs = tabs.filter(tab => _presetRefMatches(tab.overviewPresetRef, preset) || _presetRefMatches(tab.bracketPresetRef, preset));

  const query = (_presetsState.groupQuery || '').trim().toLowerCase();
  const selectedGroupIds = new Set((preset.groups || []).map(Number).filter(Number.isFinite));
  const groupItems = _filteredGroupCatalog(query, selectedGroupIds);
  const cats = [...new Set(groupItems.map(g => g.cat))];
  const groupCheckboxes = cats.map(cat => {
    const items = groupItems.filter(g => g.cat === cat);
    return `
      <div class="check-group-header">${cat}</div>
      ${items.map(g => `
        <label class="check-item">
          <input type="checkbox" class="group-check" data-gids="${_groupIds(g).join(',')}" ${_groupIds(g).some(id => groups.has(id)) ? 'checked' : ''} ${_groupIds(g).length ? '' : 'disabled'} />
          <span>${g.label}</span>
        </label>
      `).join('')}
    `;
  }).join('');

  const stateRows = EVE_STATES.map(s => {
    const isAlways = alwaysShown.includes(s.id);
    const isFiltered = filtered.includes(s.id);
    return `
      <tr class="state-editor-row" data-sid="${s.id}">
        <td class="state-name-cell">
          <span class="state-dot" style="background:${s.color}"></span>
          <span>${s.label}</span>
        </td>
        <td class="state-radio-cell">
          <input type="radio" name="state-${s.id}" class="state-radio" data-mode="always" ${isAlways ? 'checked' : ''} />
        </td>
        <td class="state-radio-cell">
          <input type="radio" name="state-${s.id}" class="state-radio" data-mode="filtered" ${isFiltered ? 'checked' : ''} />
        </td>
        <td class="state-radio-cell">
          <input type="radio" name="state-${s.id}" class="state-radio" data-mode="none" ${!isAlways && !isFiltered ? 'checked' : ''} />
        </td>
      </tr>
    `;
  }).join('');

  return `
    <div class="preset-editor-form">
      <div class="tab-editor-header">
        <h3 class="tab-editor-title">${preset.name || preset.id}</h3>
        <span class="tab-editor-slot-badge" style="font-family:var(--font-mono);font-size:10px">${preset.id}</span>
      </div>

      <div class="field-group">
        <label class="field-label">Preset Name</label>
        <input class="field-input" type="text" id="preset-name" value="${preset.name || ''}" placeholder="e.g. PVP Main, Mining Belt" />
      </div>

      <div class="field-group">
        <label class="field-label">Used By Tabs</label>
        <div class="preset-usage-list">
          ${usedByTabs.length ? usedByTabs.map(tab => `
            <span class="preset-usage-chip">
              ${tab.label || `Tab ${tab.slot}`}
              <span>${tab.overviewPresetRef === preset.id ? 'overview' : 'bracket'}</span>
            </span>
          `).join('') : '<span class="field-hint">No tabs currently use this preset.</span>'}
        </div>
      </div>

      <div class="preset-section-label">Ship Groups &amp; Entity Types</div>
      <div class="field-group">
        <input class="field-input" type="search" id="group-catalog-search" value="${escapeHtml(_presetsState.groupQuery)}" placeholder="Search ${EVE_GROUPS.length} standard groups..." />
        <div class="field-hint">${EVE_GROUPS.length} standard groups loaded. Selected imported groups stay visible while filtering.</div>
      </div>
      <div class="check-flow" id="group-checkboxes">
        ${groupCheckboxes}
      </div>

      <div class="preset-section-label" style="margin-top:20px">State Filters</div>
      <div class="field-hint" style="margin-bottom:8px">
        <strong>Always Show</strong> — visible regardless of other filters &nbsp;·&nbsp;
        <strong>Filtered</strong> — hidden from this preset's view &nbsp;·&nbsp;
        <strong>Default</strong> — let EVE decide (no override)
      </div>
      <div class="tab-editor-actions" style="justify-content:flex-start;margin-bottom:8px">
        <button class="btn-secondary" type="button" id="btn-states-all-filtered">Set All Filtered</button>
        <button class="btn-secondary" type="button" id="btn-states-all-default">Set All Default</button>
      </div>
      <table class="state-editor-table">
        <colgroup>
          <col style="width:auto" />
          <col style="width:110px" />
          <col style="width:90px" />
          <col style="width:80px" />
        </colgroup>
        <thead>
          <tr>
            <th style="text-align:left">State</th>
            <th>Always Show</th>
            <th>Filtered</th>
            <th>Default</th>
          </tr>
        </thead>
        <tbody>${stateRows}</tbody>
      </table>

      <div class="tab-editor-actions">
        <button class="btn-secondary" id="btn-duplicate-preset">Duplicate</button>
        <button class="btn-danger" id="btn-delete-preset">Delete Preset</button>
      </div>
    </div>
  `;
}

// ── Load + bind ──────────────────────────────────────────────
async function loadPresetsScreen() {
  try {
    await _loadGroupCatalog();
    const data = await api('GET', '/document/presets');
    _presetsState.presets = data.presets || [];
    _presetsState.tabs = data.tabs || [];
    if (_presetsState.selectedId === null && _presetsState.presets.length > 0) {
      _presetsState.selectedId = _presetsState.presets[0].id;
    }
    _refreshPresetsUI();
  } catch (e) {
    document.getElementById('center-panel').innerHTML = `
      <div class="section-header">Presets</div>
      <div class="empty-state" style="margin:32px"><div class="empty-state-title">No overview loaded</div><div class="empty-state-text">Load or create an overview from the Dashboard first.</div></div>
    `;
  }
}

function _refreshPresetsUI() {
  const listEl = document.getElementById('presets-card-list');
  const editorEl = document.getElementById('presets-editor-panel');
  if (!listEl || !editorEl) return;

  const preset = _presetsState.presets.find(p => p.id === _presetsState.selectedId) || null;
  listEl.innerHTML = renderPresetCards(_presetsState.presets, _presetsState.selectedId);
  editorEl.innerHTML = renderPresetEditor(preset, _presetsState.tabs);

  _bindPresetCards();
  if (preset) _bindPresetEditor(preset);
  _refreshPresetPreview();
}

function _bindPresetCards() {
  document.querySelectorAll('.preset-card[data-id]').forEach(el => {
    el.addEventListener('click', () => {
      _presetsState.selectedId = el.dataset.id;
      _refreshPresetsUI();
    });
  });

  document.getElementById('btn-add-preset')?.addEventListener('click', async () => {
    try {
      const data = await api('POST', '/document/presets', { name: 'New Preset' });
      _presetsState.presets = data.presets || [];
      _presetsState.selectedId = data.newId;
      _refreshPresetsUI();
      toast('Preset added', 'success');
    } catch(e) { toast(e.message, 'error'); }
  });
}

function _bindPresetEditor(preset) {
  const id = preset.id;

  document.getElementById('preset-name')?.addEventListener('input', async (e) => {
    document.querySelector('.tab-editor-title').textContent = e.target.value || preset.id;
    await _patchPreset(id, { name: e.target.value });
  });

  // Group checkboxes
  document.getElementById('group-catalog-search')?.addEventListener('input', e => {
    _presetsState.groupQuery = e.target.value;
    _refreshPresetsUI();
  });

  document.querySelectorAll('.group-check').forEach(cb => {
    cb.addEventListener('change', async () => {
      const checked = [...document.querySelectorAll('.group-check:checked')]
        .flatMap(c => (c.dataset.gids || '').split(',').filter(Boolean).map(Number));
      const represented = _representedGroupIds();
      const preservedImported = (preset.groups || [])
        .map(Number)
        .filter(groupId => Number.isFinite(groupId) && !represented.has(groupId));
      await _patchPreset(id, { groups: [...new Set([...checked, ...preservedImported])] });
    });
  });

  // State radios
  document.getElementById('btn-states-all-filtered')?.addEventListener('click', () => _setAllStateFilters(id, 'filtered'));
  document.getElementById('btn-states-all-default')?.addEventListener('click', () => _setAllStateFilters(id, 'none'));

  document.querySelectorAll('.state-editor-row').forEach(row => {
    row.querySelectorAll('.state-radio').forEach(radio => {
      radio.addEventListener('change', async () => {
        if (!radio.checked) return;
        await _saveStateFiltersFromDom(id);
      });
    });
  });

  document.getElementById('btn-duplicate-preset')?.addEventListener('click', async () => {
    try {
      const data = await api('POST', `/document/presets/${id}/duplicate`, {});
      _presetsState.presets = data.presets || [];
      _presetsState.selectedId = data.newId;
      _refreshPresetsUI();
      toast('Preset duplicated', 'success');
    } catch(e) { toast(e.message, 'error'); }
  });

  document.getElementById('btn-delete-preset')?.addEventListener('click', async () => {
    if (!confirm(`Delete preset "${preset.name || id}"?`)) return;
    try {
      const data = await api('DELETE', `/document/presets/${id}`);
      _presetsState.presets = data.presets || [];
      _presetsState.selectedId = _presetsState.presets[0]?.id ?? null;
      _refreshPresetsUI();
      toast('Preset deleted', 'warn');
    } catch(e) { toast(e.message, 'error'); }
  });
}

async function _patchPreset(id, fields) {
  try {
    const data = await api('PATCH', `/document/presets/${id}`, fields);
    _presetsState.presets = data.presets || [];
    window._appState.currentDoc.presets = data.presets || [];
    _refreshPresetPreview();
    // refresh card list counts without losing editor focus
    const listEl = document.getElementById('presets-card-list');
    if (listEl) listEl.innerHTML = renderPresetCards(_presetsState.presets, _presetsState.selectedId);
    _bindPresetCards();
  } catch(e) { toast(e.message, 'error'); }
}

async function _setAllStateFilters(id, mode) {
  document.querySelectorAll('.state-editor-row').forEach(row => {
    const radio = row.querySelector(`.state-radio[data-mode="${mode}"]`);
    if (radio) radio.checked = true;
  });
  await _saveStateFiltersFromDom(id);
}

async function _saveStateFiltersFromDom(id) {
  const always = [];
  const filtered = [];
  document.querySelectorAll('.state-editor-row').forEach(stateRow => {
    const stateId = parseInt(stateRow.dataset.sid, 10);
    const selected = stateRow.querySelector('.state-radio:checked');
    if (!Number.isFinite(stateId) || !selected) return;
    if (selected.dataset.mode === 'always') always.push(stateId);
    if (selected.dataset.mode === 'filtered') filtered.push(stateId);
  });
  await _patchPreset(id, { alwaysShownStates: always, filteredStates: filtered });
}

function _groupIds(group) {
  return (group.gids || []).map(Number).filter(Number.isFinite);
}

async function _loadGroupCatalog() {
  if (_presetsState.groupCatalogLoaded) return;
  try {
    const response = await fetch('/static/data/group_catalog.json?v=20260528-sde-catalog');
    if (!response.ok) throw new Error(response.statusText);
    const catalog = await response.json();
    if (Array.isArray(catalog.groups) && catalog.groups.length) {
      EVE_GROUPS = catalog.groups
        .map(group => ({
          id: String(group.id || ''),
          gids: _groupIds(group),
          label: String(group.label || group.id || 'Unnamed group'),
          cat: String(group.cat || 'Other'),
        }))
        .filter(group => group.id && group.gids.length);
    }
  } catch {
    // Keep the bundled fallback catalog if the static catalog cannot load.
  } finally {
    _presetsState.groupCatalogLoaded = true;
  }
}

function _filteredGroupCatalog(query, selectedGroupIds) {
  if (!query) return EVE_GROUPS;
  return EVE_GROUPS.filter(group => {
    const searchable = `${group.label} ${group.cat} ${_groupIds(group).join(' ')}`.toLowerCase();
    return searchable.includes(query) || _groupIds(group).some(id => selectedGroupIds.has(id));
  });
}

function _groupLabelById() {
  const labels = new Map();
  EVE_GROUPS.forEach(group => {
    _groupIds(group).forEach(id => {
      if (!labels.has(id)) labels.set(id, group.label);
    });
  });
  return labels;
}

function _representedGroupIds() {
  return new Set(EVE_GROUPS.flatMap(_groupIds));
}

function _presetRefMatches(ref, preset) {
  if (!ref || !preset) return false;
  const normalizedRef = String(ref).trim().toLowerCase();
  return [preset.id, preset.name]
    .filter(Boolean)
    .map(value => String(value).trim().toLowerCase())
    .includes(normalizedRef);
}

function _refreshPresetPreview() {
  window._appState.previewPresetId = _presetsState.selectedId;
  window._appState.previewShowTabs = false;
  refreshLivePreview();
}

function bindPresetsScreen() {
  loadPresetsScreen();
}

window._openPresetInEditor = function(presetId) {
  _presetsState.selectedId = presetId;
  navigate('presets');
};
