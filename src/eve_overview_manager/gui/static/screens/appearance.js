/* Appearance screen: state color tags, backgrounds, and blink */

const APPEARANCE_COLORS = [
  { id: 'darkTurquoise', label: 'Dark Turquoise', value: '#007c78' },
  { id: 'purple', label: 'Purple', value: '#5a148c' },
  { id: 'darkBlue', label: 'Dark Blue', value: '#0b2698' },
  { id: 'turquoise', label: 'Turquoise', value: '#00a8a8' },
  { id: 'yellow', label: 'Yellow', value: '#ffc000' },
  { id: 'blue', label: 'Blue', value: '#2878ff' },
  { id: 'violet', label: 'Violet', value: '#8a2cff' },
  { id: 'green', label: 'Green', value: '#28b928' },
  { id: 'orange', label: 'Orange', value: '#ff6a00' },
  { id: 'black', label: 'Black', value: '#000000' },
  { id: 'white', label: 'White', value: '#d8d8d8' },
  { id: 'red', label: 'Red', value: '#d80000' },
];

function renderAppearanceScreen() {
  const doc = window._appState.currentDoc;
  if (!doc) {
    return `<div class="placeholder-screen"><p>Load an overview to edit appearance.</p></div>`;
  }

  const app = doc.appearance || {};
  const flagStates = new Set([...(app.flagStates || []), ...(app.flagOrder || [])].map(Number));
  const bgStates = new Set([...(app.backgroundStates || []), ...(app.backgroundOrder || [])].map(Number));
  const blinks = app.stateBlinks || {};
  const colors = app.stateColors || {};
  const blinkSet = new Set(
    Object.entries(blinks)
      .filter(([, value]) => value === true || value === 1)
      .map(([key]) => Number(key.split('_').at(-1)))
  );

  const rows = EVE_STATES.map(state => {
    const flagColor = colors[`flag_${state.id}`] || _stateColor(state.id);
    const bgColor = colors[`background_${state.id}`] || _stateColor(state.id);
    return `
      <tr class="app-state-row" data-state-id="${state.id}">
        <td class="app-state-name-cell">
          <span class="state-dot" style="background:${state.color}"></span>
          <span>${state.label}</span>
        </td>
        <td class="app-check-cell">
          <input type="checkbox" class="app-cb app-cb--fg" ${flagStates.has(state.id) ? 'checked' : ''}>
        </td>
        <td class="app-check-cell">${_renderColorSelect('flag', state.id, flagColor)}</td>
        <td class="app-check-cell">
          <input type="checkbox" class="app-cb app-cb--bg" ${bgStates.has(state.id) ? 'checked' : ''}>
        </td>
        <td class="app-check-cell">${_renderColorSelect('background', state.id, bgColor)}</td>
        <td class="app-check-cell">
          <input type="checkbox" class="app-cb app-cb--blink" ${blinkSet.has(state.id) ? 'checked' : ''}>
        </td>
        <td class="app-state-desc">${state.desc}</td>
      </tr>
    `;
  }).join('');

  return `
<div class="section-header">Appearance</div>
<div class="appearance-screen">
  <div class="appearance-hint">
    <strong>Color Tag</strong> controls row text color.
    <strong>Background</strong> controls row background color.
    <strong>Blink</strong> flashes enabled color/background styling on and off in preview.
    Changes save immediately.
  </div>

  <div class="app-table-wrap">
    <table class="app-table">
      <colgroup>
        <col style="width:180px">
        <col style="width:80px">
        <col style="width:120px">
        <col style="width:95px">
        <col style="width:120px">
        <col style="width:70px">
        <col>
      </colgroup>
      <thead>
        <tr>
          <th class="app-th-name">State</th>
          <th class="app-th-center">Color Tag</th>
          <th class="app-th-center">Tag Color</th>
          <th class="app-th-center">Background</th>
          <th class="app-th-center">Bg Color</th>
          <th class="app-th-center">Blink</th>
          <th>Description</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  </div>

  <div class="appearance-actions">
    <button class="btn-secondary" id="btn-app-clear">Clear All</button>
    <button class="btn-primary" id="btn-app-save">Save Appearance</button>
  </div>
</div>
  `;
}

function bindAppearanceScreen() {
  document.getElementById('btn-app-save')?.addEventListener('click', () => _saveAppearance());
  document.getElementById('btn-app-clear')?.addEventListener('click', () => {
    document.querySelectorAll('.app-cb').forEach(checkbox => { checkbox.checked = false; });
    _saveAppearance({ silent: true });
  });

  document.querySelectorAll('.app-cb, .app-color-select').forEach(input => {
    input.addEventListener('change', () => _saveAppearance({ silent: true }));
  });
}

function _saveAppearance(options = {}) {
  const flagStates = [];
  const backgroundStates = [];
  const stateBlinks = {};
  const stateColors = {};

  document.querySelectorAll('.app-state-row').forEach(row => {
    const stateId = Number(row.dataset.stateId);
    const flagEnabled = row.querySelector('.app-cb--fg')?.checked;
    const bgEnabled = row.querySelector('.app-cb--bg')?.checked;
    const blinkEnabled = row.querySelector('.app-cb--blink')?.checked;
    if (!Number.isFinite(stateId)) return;

    if (flagEnabled) {
      flagStates.push(stateId);
      stateColors[`flag_${stateId}`] = row.querySelector('.app-color--flag')?.value || _stateColor(stateId);
    }
    if (bgEnabled) {
      backgroundStates.push(stateId);
      stateColors[`background_${stateId}`] = row.querySelector('.app-color--background')?.value || _stateColor(stateId);
    }
    if (blinkEnabled) {
      if (flagEnabled) stateBlinks[`flag_${stateId}`] = true;
      if (bgEnabled) stateBlinks[`background_${stateId}`] = true;
    }
  });

  api('PATCH', '/document/appearance', {
    flagStates,
    flagOrder: flagStates,
    backgroundStates,
    backgroundOrder: backgroundStates,
    stateBlinks,
    stateColors,
  })
    .then(data => {
      window._appState.currentDoc.appearance = data.appearance;
      refreshLivePreview();
      if (!options.silent) toast('Appearance saved', 'success');
    })
    .catch(error => toast(error.message, 'error'));
}

function _renderColorSelect(kind, stateId, selected) {
  return `
    <select class="app-color-select app-color--${kind}" data-sid="${stateId}" style="border-color:${_colorValue(selected)}">
      ${APPEARANCE_COLORS.map(color => `
        <option value="${color.id}" ${_colorMatches(selected, color) ? 'selected' : ''}>${color.label}</option>
      `).join('')}
    </select>
  `;
}

function _stateColor(stateId) {
  return EVE_STATES.find(state => state.id === stateId)?.color || 'white';
}

function _colorMatches(value, color) {
  const normalized = String(value || '').trim().toLowerCase();
  return normalized === color.id || normalized === color.value.toLowerCase();
}

function _colorValue(value) {
  const normalized = String(value || '').trim().toLowerCase();
  const color = APPEARANCE_COLORS.find(item => item.id === normalized || item.value.toLowerCase() === normalized);
  return color ? color.value : normalized;
}
