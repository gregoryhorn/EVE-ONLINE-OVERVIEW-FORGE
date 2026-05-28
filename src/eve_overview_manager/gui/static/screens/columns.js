/* Columns screen — reorder and toggle overview columns */

const ALL_COLUMNS = [
  { id: 'TAG',                 label: 'Tag',                desc: 'Fleet/corp tag icon' },
  { id: 'ICON',                label: 'Icon',               desc: 'Entity type icon' },
  { id: 'DISTANCE',            label: 'Distance',           desc: 'Range to target' },
  { id: 'NAME',                label: 'Name',               desc: 'Pilot or entity name' },
  { id: 'TYPE',                label: 'Type',               desc: 'Ship or entity type' },
  { id: 'CORPORATION',         label: 'Corporation',        desc: 'Pilot corporation' },
  { id: 'ALLIANCE',            label: 'Alliance',           desc: 'Pilot alliance' },
  { id: 'FACTION',             label: 'Faction',            desc: 'Faction militia' },
  { id: 'MILITIA',             label: 'Militia',            desc: 'Militia membership' },
  { id: 'SIZE',                label: 'Size',               desc: 'Entity size class' },
  { id: 'VELOCITY',            label: 'Velocity',           desc: 'Current speed (m/s)' },
  { id: 'RADIALVELOCITY',      label: 'Radial Velocity',    desc: 'Speed toward/away (m/s)' },
  { id: 'TRANSVERSALVELOCITY', label: 'Transversal Vel.',   desc: 'Sideways speed (m/s)' },
  { id: 'ANGULARVELOCITY',     label: 'Angular Velocity',   desc: 'Angular speed (rad/s)' },
];

function renderColumnsScreen() {
  const doc = window._appState.currentDoc;
  if (!doc) {
    return `<div class="placeholder-screen"><p>Load an overview to edit columns.</p></div>`;
  }

  const cols = doc.columns || {};
  const order = cols.columnOrder || [];
  const enabled = new Set(cols.enabled || []);

  // Build ordered list: first those in columnOrder (in order), then remaining
  const inOrder = order.filter(id => ALL_COLUMNS.find(c => c.id === id));
  const remaining = ALL_COLUMNS.filter(c => !order.includes(c.id)).map(c => c.id);
  const fullOrder = [...inOrder, ...remaining];

  const rows = fullOrder.map((id, idx) => {
    const meta = ALL_COLUMNS.find(c => c.id === id) || { id, label: id, desc: '' };
    const isEnabled = enabled.has(id);
    const inOrderList = order.includes(id);
    return `
      <div class="col-row ${isEnabled ? 'col-row--enabled' : ''} ${!inOrderList ? 'col-row--extra' : ''}"
           draggable="true" data-id="${id}" data-idx="${idx}">
        <div class="col-drag-handle" title="Drag to reorder">⠿</div>
        <label class="col-toggle">
          <input type="checkbox" class="col-checkbox" data-col-id="${id}" ${isEnabled ? 'checked' : ''}>
          <span class="col-check-visual"></span>
        </label>
        <div class="col-info">
          <div class="col-name">${meta.label}</div>
          <div class="col-desc">${meta.desc}</div>
        </div>
        <div class="col-id-badge">${id}</div>
        <div class="col-row-actions">
          <button class="btn-icon col-move-up" type="button" title="Move up" data-col-id="${id}">↑</button>
          <button class="btn-icon col-move-down" type="button" title="Move down" data-col-id="${id}">↓</button>
        </div>
      </div>
    `;
  }).join('');

  return `
<div class="section-header">Columns</div>
<div class="columns-screen">
  <div class="columns-hint">
    Drag rows to set display order. Check to enable in the overview. Columns must be in the order list to appear.
  </div>
  <div class="col-list" id="col-list">
    ${rows}
  </div>
  <div class="columns-actions">
    <button class="btn-secondary" id="btn-cols-reset">Reset to Default</button>
    <button class="btn-primary" id="btn-cols-save">Save Columns</button>
  </div>
</div>
  `;
}

function bindColumnsScreen() {
  const list = document.getElementById('col-list');
  if (!list) return;

  // Drag-to-reorder
  let dragSrc = null;

  list.querySelectorAll('.col-row').forEach(row => {
    row.addEventListener('dragstart', e => {
      dragSrc = row;
      row.classList.add('col-row--dragging');
      e.dataTransfer.effectAllowed = 'move';
    });
    row.addEventListener('dragend', () => {
      row.classList.remove('col-row--dragging');
      list.querySelectorAll('.col-row').forEach(r => r.classList.remove('col-row--over'));
      dragSrc = null;
    });
    row.addEventListener('dragover', e => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      list.querySelectorAll('.col-row').forEach(r => r.classList.remove('col-row--over'));
      if (row !== dragSrc) row.classList.add('col-row--over');
    });
    row.addEventListener('drop', e => {
      e.preventDefault();
      if (!dragSrc || dragSrc === row) return;
      const rows = [...list.querySelectorAll('.col-row')];
      const srcIdx = rows.indexOf(dragSrc);
      const dstIdx = rows.indexOf(row);
      if (srcIdx < dstIdx) {
        row.after(dragSrc);
      } else {
        row.before(dragSrc);
      }
      _saveColumns({ silent: true });
    });
  });

  list.querySelectorAll('.col-checkbox').forEach(cb => {
    cb.addEventListener('change', () => {
      cb.closest('.col-row')?.classList.toggle('col-row--enabled', cb.checked);
      _saveColumns({ silent: true });
    });
  });

  list.querySelectorAll('.col-move-up').forEach(btn => {
    btn.addEventListener('click', () => {
      const row = btn.closest('.col-row');
      const previous = row?.previousElementSibling;
      if (!row || !previous) return;
      previous.before(row);
      _saveColumns({ silent: true });
    });
  });

  list.querySelectorAll('.col-move-down').forEach(btn => {
    btn.addEventListener('click', () => {
      const row = btn.closest('.col-row');
      const next = row?.nextElementSibling;
      if (!row || !next) return;
      next.after(row);
      _saveColumns({ silent: true });
    });
  });

  // Save
  document.getElementById('btn-cols-save')?.addEventListener('click', _saveColumns);

  // Reset
  document.getElementById('btn-cols-reset')?.addEventListener('click', () => {
    const defaultOrder = ['TAG', 'ICON', 'DISTANCE', 'NAME', 'TYPE'];
    const defaultEnabled = ['ICON', 'DISTANCE', 'NAME', 'TYPE'];
    api('PATCH', '/document/columns', { columnOrder: defaultOrder, enabled: defaultEnabled })
      .then(data => {
        window._appState.currentDoc.columns = data.columns;
        renderScreen('columns');
        refreshLivePreview();
        toast('Reset to default columns', 'success');
      })
      .catch(e => toast(e.message, 'error'));
  });
}

function _saveColumns(options = {}) {
  const list = document.getElementById('col-list');
  if (!list) return;

  const rows = [...list.querySelectorAll('.col-row')];
  const columnOrder = rows.map(r => r.dataset.id);
  const enabled = rows
    .filter(r => r.querySelector('.col-checkbox')?.checked)
    .map(r => r.dataset.id);

  api('PATCH', '/document/columns', { columnOrder, enabled })
    .then(data => {
      window._appState.currentDoc.columns = data.columns;
      refreshLivePreview();
      if (!options.silent) toast('Columns saved', 'success');
    })
    .catch(e => toast(e.message, 'error'));
}
