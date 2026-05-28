/* Types & States reference screen */

function renderTypesScreen() {
  const presets = window._appState.currentDoc?.presets || [];
  const stateSections = _buildStateSections(presets);
  const groupSections = _buildGroupSections(presets);
  const presetCount = presets.length;

  return `
<div class="section-header">Types &amp; States</div>
<div class="types-layout">

  <div class="types-panel">
    <div class="types-panel-header">
      <span>Entity Types &amp; Groups</span>
      <input class="types-search" type="text" id="types-search" placeholder="Search…" />
    </div>
    ${presetCount === 0 ? `<div class="types-no-doc-hint">Load an overview to see preset usage counts.</div>` : ''}
    <div class="types-panel-body" id="types-group-list">
      ${groupSections}
    </div>
  </div>

  <div class="types-panel">
    <div class="types-panel-header">
      <span>Overview States</span>
      <input class="types-search" type="text" id="states-search" placeholder="Search…" />
    </div>
    ${presetCount === 0 ? `<div class="types-no-doc-hint">Load an overview to see preset usage counts.</div>` : ''}
    <div class="types-panel-body" id="types-state-list">
      ${stateSections}
    </div>
  </div>

</div>
  `;
}

function _buildStateSections(presets) {
  return EVE_STATES.map(s => {
    const usedIn = presets.filter(p =>
      (p.alwaysShownStates || []).includes(s.id) || (p.filteredStates || []).includes(s.id)
    );
    const alwaysIn = presets.filter(p => (p.alwaysShownStates || []).includes(s.id));
    const filteredIn = presets.filter(p => (p.filteredStates || []).includes(s.id));

    let usageBadge = '';
    if (presets.length > 0) {
      if (usedIn.length === 0) {
        usageBadge = `<span class="usage-badge usage-badge--none">unused</span>`;
      } else {
        const parts = [];
        if (alwaysIn.length) parts.push(`always: ${alwaysIn.map(p => p.name || p.id).join(', ')}`);
        if (filteredIn.length) parts.push(`filtered: ${filteredIn.map(p => p.name || p.id).join(', ')}`);
        usageBadge = `<span class="usage-badge usage-badge--used" title="${parts.join(' | ')}">${usedIn.length} preset${usedIn.length !== 1 ? 's' : ''}</span>`;
      }
    }

    return `
      <div class="ref-row state-ref-row" data-label="${s.label.toLowerCase()} ${s.desc.toLowerCase()}">
        <div class="ref-row-left">
          <span class="state-dot" style="background:${s.color}"></span>
          <div>
            <div class="ref-row-name">${s.label}</div>
            <div class="ref-row-desc">${s.desc}</div>
          </div>
        </div>
        <div class="ref-row-right">
          ${usageBadge}
          <span class="ref-id-badge">ID ${s.id}</span>
        </div>
      </div>
    `;
  }).join('');
}

function _buildGroupSections(presets) {
  const cats = [...new Set(EVE_GROUPS.map(g => g.cat))];
  return cats.map(cat => {
    const items = EVE_GROUPS.filter(g => g.cat === cat);
    return `
      <div class="ref-category" data-cat="${cat.toLowerCase()}">
        <div class="ref-category-header collapsible-header" data-target="cat-${cat}">
          <svg class="collapse-arrow collapse-arrow--open" width="10" height="10" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
          ${cat}
          <span class="cat-count">${items.length}</span>
        </div>
        <div class="collapsible-body" id="cat-${cat}">
          ${items.map(g => {
            const usedIn = presets.filter(p => (p.groups || []).includes(g.id));
            let usageBadge = '';
            if (presets.length > 0) {
              if (usedIn.length === 0) {
                usageBadge = `<span class="usage-badge usage-badge--none">unused</span>`;
              } else {
                const names = usedIn.map(p => p.name || p.id).join(', ');
                usageBadge = `<span class="usage-badge usage-badge--used" title="${names}">${usedIn.length} preset${usedIn.length !== 1 ? 's' : ''}</span>`;
              }
            }
            return `
              <div class="ref-row group-ref-row" data-label="${g.label.toLowerCase()} ${cat.toLowerCase()}">
                <div class="ref-row-name">${g.label}</div>
                <div class="ref-row-right">
                  ${usageBadge}
                  <span class="ref-id-badge">${g.id}</span>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }).join('');
}

function bindTypesScreen() {
  document.querySelectorAll('.collapsible-header').forEach(header => {
    header.addEventListener('click', () => {
      const targetId = header.dataset.target;
      const body = document.getElementById(targetId);
      const arrow = header.querySelector('.collapse-arrow');
      if (!body) return;
      const isOpen = body.style.display !== 'none';
      body.style.display = isOpen ? 'none' : '';
      arrow.classList.toggle('collapse-arrow--open', !isOpen);
      arrow.classList.toggle('collapse-arrow--closed', isOpen);
    });
  });

  document.getElementById('types-search')?.addEventListener('input', e => {
    const q = e.target.value.toLowerCase();
    document.querySelectorAll('.group-ref-row').forEach(el => {
      el.style.display = (!q || el.dataset.label.includes(q)) ? '' : 'none';
    });
    document.querySelectorAll('.ref-category').forEach(cat => {
      const visible = [...cat.querySelectorAll('.group-ref-row')].some(r => r.style.display !== 'none');
      cat.style.display = visible ? '' : 'none';
      if (q) {
        const body = cat.querySelector('.collapsible-body');
        const arrow = cat.querySelector('.collapse-arrow');
        if (body) body.style.display = '';
        if (arrow) { arrow.classList.add('collapse-arrow--open'); arrow.classList.remove('collapse-arrow--closed'); }
      }
    });
  });

  document.getElementById('states-search')?.addEventListener('input', e => {
    const q = e.target.value.toLowerCase();
    document.querySelectorAll('.state-ref-row').forEach(el => {
      el.style.display = (!q || el.dataset.label.includes(q)) ? '' : 'none';
    });
  });
}
