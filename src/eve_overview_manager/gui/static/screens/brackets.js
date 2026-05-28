/* Brackets screen — ship label slots */

// Known label slot names from EVE ship label system
const SHIP_LABEL_SLOTS = [
  { key: 'Type',             label: 'Ship Type',       desc: 'Shows ship class name in brackets' },
  { key: 'Name',             label: 'Pilot Name',      desc: 'Pilot or entity name above bracket' },
  { key: 'Corporation',      label: 'Corporation',     desc: 'Corporation ticker or name' },
  { key: 'Alliance',         label: 'Alliance',        desc: 'Alliance ticker or name' },
  { key: 'Militia',          label: 'Militia',         desc: 'Faction warfare militia' },
  { key: 'Ship Name',        label: 'Ship Name',       desc: 'Custom ship name (if set)' },
  { key: 'Fleet Booster',    label: 'Fleet Booster',   desc: 'Indicates fleet command role' },
];

function renderBracketsScreen() {
  const doc = window._appState.currentDoc;
  if (!doc) {
    return `<div class="placeholder-screen"><p>Load an overview to view bracket labels.</p></div>`;
  }

  const labels = doc.labels || {};
  const shipLabels = labels.shipLabels || {};
  const order = labels.shipLabelOrder || [];

  // Build unified list: known slots first (in order if present), then any extra
  const knownKeys = SHIP_LABEL_SLOTS.map(s => s.key);
  const extraKeys = Object.keys(shipLabels).filter(k => !knownKeys.includes(k));

  const allSlots = SHIP_LABEL_SLOTS.map(s => ({
    key: s.key,
    label: s.label,
    desc: s.desc,
    config: shipLabels[s.key] || null,
    inOrder: order.includes(s.key),
  }));

  extraKeys.forEach(k => allSlots.push({
    key: k,
    label: k,
    desc: 'Custom slot from your overview',
    config: shipLabels[k],
    inOrder: order.includes(k),
  }));

  const hasAny = Object.keys(shipLabels).length > 0;

  const rows = allSlots.map(slot => {
    const isActive = slot.config !== null;
    const posIdx = order.indexOf(slot.key);
    const posLabel = posIdx >= 0 ? `Position ${posIdx + 1}` : '—';
    let configSummary = '—';
    if (slot.config && typeof slot.config === 'object') {
      const parts = [];
      if ('size' in slot.config)    parts.push(`size ${slot.config.size}`);
      if ('color' in slot.config)   parts.push(`color ${slot.config.color}`);
      if ('shown' in slot.config)   parts.push(slot.config.shown ? 'shown' : 'hidden');
      if ('state' in slot.config)   parts.push(`state ${slot.config.state}`);
      configSummary = parts.join(', ') || JSON.stringify(slot.config).slice(0, 60);
    } else if (slot.config !== null && slot.config !== undefined) {
      configSummary = String(slot.config).slice(0, 80);
    }

    return `
      <div class="bracket-row ${isActive ? 'bracket-row--active' : 'bracket-row--inactive'}">
        <div class="bracket-row-left">
          <div class="bracket-slot-name">${slot.label}</div>
          <div class="bracket-slot-desc">${slot.desc}</div>
        </div>
        <div class="bracket-row-center">
          <span class="bracket-config-summary" title="${configSummary}">${configSummary}</span>
        </div>
        <div class="bracket-row-right">
          ${isActive
            ? `<span class="bracket-badge bracket-badge--active">Active</span>`
            : `<span class="bracket-badge bracket-badge--inactive">Not set</span>`
          }
          <span class="bracket-pos-badge">${posLabel}</span>
        </div>
      </div>
    `;
  }).join('');

  const emptyMsg = !hasAny
    ? `<div class="brackets-no-data">No ship label data in this overview. Ship labels are configured in the EVE client.</div>`
    : '';

  return `
<div class="section-header">Brackets</div>
<div class="brackets-screen">
  <div class="brackets-hint">
    Ship bracket labels appear above entities in space. This view reflects the label configuration from your overview YAML.
    To change bracket labels, use the EVE client Overview Settings → Ship Labels tab, then re-import the YAML.
  </div>
  ${emptyMsg}
  <div class="bracket-list" id="bracket-list">
    ${rows}
  </div>
  <div class="brackets-raw-section">
    <div class="brackets-raw-header collapsible-header" data-target="brackets-raw-body">
      <svg class="collapse-arrow collapse-arrow--closed" width="10" height="10" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
      </svg>
      Raw label data
    </div>
    <div class="brackets-raw-body" id="brackets-raw-body" style="display:none">
      <pre class="brackets-raw-json">${JSON.stringify(labels, null, 2)}</pre>
    </div>
  </div>
</div>
  `;
}

function bindBracketsScreen() {
  document.querySelectorAll('.brackets-raw-header.collapsible-header').forEach(header => {
    header.addEventListener('click', () => {
      const body = document.getElementById(header.dataset.target);
      const arrow = header.querySelector('.collapse-arrow');
      if (!body) return;
      const isOpen = body.style.display !== 'none';
      body.style.display = isOpen ? 'none' : '';
      arrow.classList.toggle('collapse-arrow--open', !isOpen);
      arrow.classList.toggle('collapse-arrow--closed', isOpen);
    });
  });
}
