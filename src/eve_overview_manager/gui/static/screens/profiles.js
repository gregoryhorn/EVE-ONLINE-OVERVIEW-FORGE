/* Profiles screen */

window._profileState = {
  profiles: [],
  selectedProfilePath: '',
  characterFiles: [],
  selectedSourceCharacterId: '',
  selectedSource: '',
  selectedTarget: '',
  latestPlan: null,
  latestPlanKind: 'clone',
  latestBackupManifest: null,
  latestExecutionAudit: null,
  latestRollbackAudit: null,
  latestPackagePath: '',
  activeMode: 'same-pc',
  selectedSnapshotPath: '',
};

function renderProfilesScreen() {
  return `
    <div class="profile-copy-title">
      <div class="section-header">Profile Tools</div>
      <p>Safely copy, package, and restore local EVE overview and layout profile files.</p>
    </div>
    <div class="profiles-screen">
      <div class="card profile-scan-card">
        <div class="card-header">
          <div class="card-header-left">Local Profile Scan</div>
          <span class="mini-status">Read-only</span>
        </div>
        <label class="field-label">EVE settings root or profile folder</label>
        <input class="field-input" id="profile-root" type="text" value="" placeholder="%LOCALAPPDATA%\\CCP\\EVE\\c_ccp_eve_tq_tranquility" />
        <div class="profile-toggle-row">
          <label><input type="checkbox" id="profile-resolve-names" checked> Resolve character names</label>
        </div>
        <div class="ie-actions">
          <button class="btn-primary" id="profile-scan">Scan Profiles</button>
        </div>
      </div>

      <div class="profile-mode-tabs" role="tablist" aria-label="Profile workflow mode">
        <button class="profile-mode-tab is-active" data-profile-mode-tab="same-pc">Same PC</button>
        <button class="profile-mode-tab" data-profile-mode-tab="other-pc">Other PC</button>
        <button class="profile-mode-tab" data-profile-mode-tab="snapshots">Snapshots</button>
      </div>

      <div class="profile-mode-section" data-profile-mode-panel="same-pc">
      <div class="profile-copy-workflow">
        <div class="profile-copy-panel profile-source-panel">
          <div class="profile-step-header">
            <span class="profile-step-number">1</span>
            <span>Source Profile</span>
          </div>

          <label class="field-label">Profile folder</label>
          <select class="field-input" id="character-profile"></select>

          <label class="field-label">Source character</label>
          <select class="field-input" id="character-source"></select>

          <div id="profile-source-card" class="profile-source-card">
            <div class="ie-output">Scan profiles to select a source character.</div>
          </div>

          <div class="profile-source-actions">
            <button class="btn-secondary" id="profile-open-folder" disabled>Open Folder</button>
            <button class="btn-secondary" id="profile-rescan-inline">Rescan</button>
          </div>
        </div>

        <div class="profile-copy-panel profile-target-panel">
          <div class="profile-step-header">
            <span class="profile-step-number">2</span>
            <span>Target Characters</span>
            <span class="profile-target-count" id="profile-target-count">0 selected</span>
          </div>

          <div class="profile-target-table">
            <div class="profile-target-head">
              <span></span>
              <span></span>
              <span>Character Name</span>
              <span>Profile File</span>
              <span>Status</span>
            </div>
            <div class="profile-character-dest-list" id="character-destinations">
              <div class="ie-output">Scan and select a profile folder first.</div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-header-left">Character Overwrite Plan</div>
          <span class="mini-status">Dry-run first</span>
        </div>
        <p class="ie-note">Select one source character, then choose destination characters to overwrite with that character's core_char_*.dat settings. core_user_*.dat and prefs.ini are not part of this character-level workflow.</p>
        <div class="ie-actions">
          <button class="btn-primary" id="character-plan">Generate Character Overwrite Plan</button>
        </div>
        <div id="character-plan-output" class="ie-output">No character plan generated.</div>
      </div>

      <div class="profile-grid">
        <div class="card">
          <div class="card-header">
            <div class="card-header-left">Discovered Profiles</div>
            <span class="mini-status" id="profile-count">0</span>
          </div>
          <div class="profile-list" id="profile-list">
            <div class="ie-output">Run a scan to list profile folders.</div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-header-left">Selected Profile Report</div>
          </div>
          <div id="profile-report-panel" class="profile-report-panel">
            <div class="ie-output">Select a profile to inspect files and character names.</div>
          </div>
        </div>
      </div>

      <details class="profile-expert-details">
        <summary>Advanced folder clone plan</summary>
        <div class="card">
        <div class="card-header">
          <div class="card-header-left">Advanced Folder Clone Plan</div>
          <span class="mini-status">Legacy / expert</span>
        </div>
        <div class="profile-plan-controls">
          <div>
            <label class="field-label">Source profile</label>
            <select class="field-input" id="profile-source"></select>
          </div>
          <div>
            <label class="field-label">Target profile</label>
            <select class="field-input" id="profile-target"></select>
          </div>
        </div>
        <div class="profile-toggle-row">
          <label><input type="checkbox" id="clone-core-user" checked> core_user</label>
          <label><input type="checkbox" id="clone-core-char" checked> core_char</label>
          <label><input type="checkbox" id="clone-prefs"> prefs.ini</label>
          <label><input type="checkbox" id="clone-copy-first"> copy first to all</label>
        </div>
        <div class="ie-actions">
          <button class="btn-primary" id="profile-plan">Generate Dry-Run Plan</button>
        </div>
        <div id="profile-plan-output" class="ie-output">No plan generated.</div>
        </div>
      </details>
      </div>

      <div class="profile-mode-section" data-profile-mode-panel="other-pc" hidden>
        <div class="card">
          <div class="card-header">
            <div class="card-header-left">Portable Profile Package</div>
            <span class="mini-status">Manifest + checksums</span>
          </div>
          <p class="ie-note">Export a package on one PC, copy the zip manually to another PC, then inspect and plan import against the local destination profile. Character/account IDs must match before execution.</p>
          <div class="profile-plan-controls">
            <div>
              <label class="field-label">Package path</label>
              <input class="field-input" id="profile-package-path" type="text" value=".tmp\\eve-profile-transfer.zip" />
            </div>
            <div>
              <label class="field-label">Destination profile</label>
              <select class="field-input" id="package-destination-profile"></select>
            </div>
          </div>
          <div class="profile-toggle-row">
            <label><input type="checkbox" id="package-core-user"> core_user</label>
            <label><input type="checkbox" id="package-core-char" checked> core_char</label>
            <label><input type="checkbox" id="package-prefs"> prefs.ini</label>
          </div>
          <div class="ie-actions">
            <button class="btn-secondary" id="profile-export-package">Export From Selected Profile</button>
            <button class="btn-secondary" id="profile-inspect-package">Inspect Package</button>
            <button class="btn-primary" id="profile-plan-package-import">Plan Package Import</button>
          </div>
          <div id="profile-package-output" class="ie-output">Scan profiles, select a profile, then export or inspect a package.</div>
        </div>
      </div>

      <div class="profile-mode-section" data-profile-mode-panel="snapshots" hidden>
        <div class="card">
          <div class="card-header">
            <div class="card-header-left">Known-Good Profile Snapshots</div>
            <span class="mini-status">Package-backed</span>
          </div>
          <p class="ie-note">Save a known-good local profile package, verify it later, then plan restore against matching local character/account files before backup and execution.</p>
          <div class="profile-plan-controls">
            <div>
              <label class="field-label">Snapshot library root</label>
              <input class="field-input" id="profile-snapshot-root" type="text" value=".tmp\\profile-snapshots" />
            </div>
            <div>
              <label class="field-label">Restore destination profile</label>
              <select class="field-input" id="snapshot-destination-profile"></select>
            </div>
          </div>
          <div class="profile-plan-controls">
            <div>
              <label class="field-label">Snapshot name</label>
              <input class="field-input" id="profile-snapshot-name" type="text" value="Known Good" />
            </div>
            <div>
              <label class="field-label">Notes</label>
              <input class="field-input" id="profile-snapshot-notes" type="text" value="" placeholder="Optional note" />
            </div>
          </div>
          <div class="profile-toggle-row">
            <label><input type="checkbox" id="snapshot-core-user"> core_user</label>
            <label><input type="checkbox" id="snapshot-core-char" checked> core_char</label>
            <label><input type="checkbox" id="snapshot-prefs"> prefs.ini</label>
          </div>
          <div class="ie-actions">
            <button class="btn-secondary" id="profile-save-snapshot">Save Selected Profile Snapshot</button>
            <button class="btn-secondary" id="profile-list-snapshots">List Snapshots</button>
            <button class="btn-primary" id="profile-plan-snapshot-restore">Plan Restore From Selected</button>
          </div>
          <div id="profile-snapshot-output" class="ie-output">Choose a library root, then save or list snapshots.</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-header-left">Guarded Write Workflow</div>
          <span class="mini-status">Backup required</span>
        </div>
        <label class="field-label">Backup root</label>
        <input class="field-input" id="profile-backup-root" type="text" value=".tmp\\gui-profile-backups" />
        <div class="ie-actions">
          <button class="btn-primary" id="profile-backup-targets" disabled>Backup Targets</button>
          <button class="btn-secondary" id="profile-execute-clone" disabled>Execute Clone</button>
          <button class="btn-secondary" id="profile-rollback" disabled>Rollback From Backup</button>
        </div>
        <p class="ie-note">Close the EVE client before execute or rollback. The app never deletes target files.</p>
        <div id="profile-write-output" class="ie-output">Generate a non-blocked plan before backup or execution.</div>
      </div>
    </div>
  `;
}

function bindProfilesScreen() {
  _loadDefaultProfileRoot();
  document.getElementById('profile-scan')?.addEventListener('click', _scanProfiles);
  document.getElementById('profile-rescan-inline')?.addEventListener('click', _scanProfiles);
  document.getElementById('profile-open-folder')?.addEventListener('click', _openSelectedProfileFolder);
  document.getElementById('character-plan')?.addEventListener('click', _planCharacterClone);
  document.getElementById('profile-plan')?.addEventListener('click', _planProfileClone);
  document.getElementById('profile-backup-targets')?.addEventListener('click', _backupProfileTargets);
  document.getElementById('profile-execute-clone')?.addEventListener('click', _executeProfileClone);
  document.getElementById('profile-rollback')?.addEventListener('click', _rollbackProfileBackup);
  document.getElementById('profile-export-package')?.addEventListener('click', _exportProfilePackage);
  document.getElementById('profile-inspect-package')?.addEventListener('click', _inspectProfilePackage);
  document.getElementById('profile-plan-package-import')?.addEventListener('click', _planProfilePackageImport);
  document.getElementById('profile-save-snapshot')?.addEventListener('click', _saveProfileSnapshot);
  document.getElementById('profile-list-snapshots')?.addEventListener('click', _listProfileSnapshots);
  document.getElementById('profile-plan-snapshot-restore')?.addEventListener('click', _planProfileSnapshotRestore);
  document.querySelectorAll('[data-profile-mode-tab]').forEach(button => {
    button.addEventListener('click', () => _setProfileMode(button.dataset.profileModeTab));
  });
  _renderProfileSelects();
  _renderCharacterWorkflow();
  _renderProfileList();
  _setProfileMode(window._profileState.activeMode || 'same-pc');
  _syncProfileWriteButtons();
}

function _setProfileMode(mode) {
  window._profileState.activeMode = mode;
  document.querySelectorAll('[data-profile-mode-tab]').forEach(button => {
    button.classList.toggle('is-active', button.dataset.profileModeTab === mode);
  });
  document.querySelectorAll('[data-profile-mode-panel]').forEach(panel => {
    panel.hidden = panel.dataset.profileModePanel !== mode;
  });
}

async function _loadDefaultProfileRoot() {
  const input = document.getElementById('profile-root');
  if (!input || input.value.trim()) return;
  try {
    const data = await api('GET', '/profiles/default-root');
    if (data.profileRoot && !input.value.trim()) {
      input.value = data.profileRoot;
    }
  } catch {
    // Default path discovery is a convenience; manual path entry remains available.
  }
}

async function _scanProfiles() {
  const rootPath = document.getElementById('profile-root').value.trim();
  const resolveNames = document.getElementById('profile-resolve-names').checked;
  if (!rootPath) { toast('Enter a profile root path.', 'warn'); return; }
  try {
    const data = await api('POST', '/profiles/scan', { rootPath, resolveNames });
    window._profileState.profiles = data.profiles || [];
    window._profileState.selectedProfilePath = window._profileState.profiles[0]?.profilePath || '';
    window._profileState.characterFiles = window._profileState.profiles[0]?.characterFiles || [];
    window._profileState.selectedSourceCharacterId = String(window._profileState.characterFiles[0]?.characterId || '');
    window._profileState.selectedSource = window._profileState.profiles[0]?.profilePath || '';
    window._profileState.selectedTarget = window._profileState.profiles[1]?.profilePath || '';
    window._profileState.latestPlan = null;
    window._profileState.latestPlanKind = 'clone';
    window._profileState.latestBackupManifest = null;
    window._profileState.latestExecutionAudit = null;
    window._profileState.latestRollbackAudit = null;
    _renderProfileList();
    _renderProfileSelects();
    _renderCharacterWorkflow();
    _renderWriteStatus('Generate a non-blocked plan before backup or execution.');
    _syncProfileWriteButtons();
    toast(`Found ${window._profileState.profiles.length} profile(s)`, 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

function _renderProfileList() {
  const list = document.getElementById('profile-list');
  const count = document.getElementById('profile-count');
  if (!list) return;
  const profiles = window._profileState.profiles || [];
  if (count) count.textContent = String(profiles.length);
  if (!profiles.length) {
    list.innerHTML = `<div class="ie-output">Run a scan to list profile folders.</div>`;
    return;
  }
  list.innerHTML = profiles.map(profile => `
    <button class="profile-row" data-path="${_escapeAttr(profile.profilePath)}">
      <div>
        <div class="profile-row-title">${_fileName(profile.profilePath)}</div>
        <div class="profile-row-path">${profile.profilePath}</div>
      </div>
      <div class="profile-row-stats">
        <span>${profile.coreUserFiles.length} user</span>
        <span>${profile.coreCharFiles.length} char</span>
        <span>${profile.prefsFiles.length ? 'prefs' : 'no prefs'}</span>
      </div>
    </button>
  `).join('');
  list.querySelectorAll('.profile-row').forEach(row => {
    row.addEventListener('click', () => {
      window._profileState.selectedProfilePath = row.dataset.path;
      const profile = window._profileState.profiles.find(p => p.profilePath === row.dataset.path);
      window._profileState.characterFiles = profile?.characterFiles || [];
      window._profileState.selectedSourceCharacterId = String(window._profileState.characterFiles[0]?.characterId || '');
      _renderCharacterWorkflow();
      _loadProfileReport(row.dataset.path);
    });
  });
}

function _renderProfileSelects() {
  const profiles = window._profileState.profiles || [];
  const options = profiles.map(profile => `<option value="${_escapeAttr(profile.profilePath)}">${_fileName(profile.profilePath)}</option>`).join('');
  const source = document.getElementById('profile-source');
  const target = document.getElementById('profile-target');
  const packageDestination = document.getElementById('package-destination-profile');
  const snapshotDestination = document.getElementById('snapshot-destination-profile');
  if (source) {
    source.innerHTML = options;
    source.value = window._profileState.selectedSource || profiles[0]?.profilePath || '';
  }
  if (target) {
    target.innerHTML = options;
    target.value = window._profileState.selectedTarget || profiles[1]?.profilePath || profiles[0]?.profilePath || '';
  }
  if (packageDestination) {
    packageDestination.innerHTML = options;
    packageDestination.value = window._profileState.selectedProfilePath || profiles[0]?.profilePath || '';
  }
  if (snapshotDestination) {
    snapshotDestination.innerHTML = options;
    snapshotDestination.value = window._profileState.selectedProfilePath || profiles[0]?.profilePath || '';
  }
}

function _renderCharacterWorkflow() {
  const profiles = window._profileState.profiles || [];
  const profileSelect = document.getElementById('character-profile');
  if (profileSelect) {
    profileSelect.innerHTML = profiles.map(profile => `<option value="${_escapeAttr(profile.profilePath)}">${_fileName(profile.profilePath)}</option>`).join('');
    profileSelect.value = window._profileState.selectedProfilePath || profiles[0]?.profilePath || '';
    profileSelect.onchange = () => {
      window._profileState.selectedProfilePath = profileSelect.value;
      const selected = profiles.find(profile => profile.profilePath === profileSelect.value);
      window._profileState.characterFiles = selected?.characterFiles || [];
      window._profileState.selectedSourceCharacterId = String(window._profileState.characterFiles[0]?.characterId || '');
      _renderCharacterWorkflow();
    };
  }
  const characters = window._profileState.characterFiles || [];
  const source = document.getElementById('character-source');
  if (source) {
    source.innerHTML = characters
      .filter(character => character.characterId !== null && character.characterId !== undefined)
      .map(character => `<option value="${character.characterId}">${_characterLabel(character)}</option>`)
      .join('');
    source.value = window._profileState.selectedSourceCharacterId || '';
    source.onchange = () => {
      window._profileState.selectedSourceCharacterId = source.value;
      _renderCharacterDestinations();
      _renderSourceCharacterCard();
    };
  }
  _renderSourceCharacterCard();
  _renderCharacterDestinations();
}

function _renderCharacterDestinations() {
  const dest = document.getElementById('character-destinations');
  if (!dest) return;
  const sourceId = Number(document.getElementById('character-source')?.value || window._profileState.selectedSourceCharacterId);
  const characters = (window._profileState.characterFiles || [])
    .filter(character => character.characterId !== null && character.characterId !== undefined);
  const targets = characters.filter(character => Number(character.characterId) !== sourceId);
  dest.innerHTML = targets.length
    ? targets.map((character, index) => `
      <label class="profile-character-dest-row">
        <input type="checkbox" class="character-dest-check" value="${character.characterId}" ${index < 3 ? 'checked' : ''}>
        <span class="profile-character-icon" aria-hidden="true"></span>
        <span>
          <strong>${_characterName(character)}</strong>
          <small>${_characterIdLabel(character)}</small>
        </span>
        <span class="profile-target-file">${_fileName(character.path || character.filePath || character.name || '')}</span>
        <span class="profile-ready-status profile-ready-status--ready">Ready</span>
      </label>
    `).join('')
    : '<div class="ie-output">No destination characters available in this profile.</div>';
  dest.querySelectorAll('.character-dest-check').forEach(input => {
    input.addEventListener('change', _updateTargetCount);
  });
  _updateTargetCount();
}

function _renderSourceCharacterCard() {
  const card = document.getElementById('profile-source-card');
  const openButton = document.getElementById('profile-open-folder');
  if (!card) return;
  const profilePath = document.getElementById('character-profile')?.value || window._profileState.selectedProfilePath;
  const sourceId = Number(document.getElementById('character-source')?.value || window._profileState.selectedSourceCharacterId);
  const source = (window._profileState.characterFiles || []).find(character => Number(character.characterId) === sourceId);
  if (openButton) openButton.disabled = !profilePath;
  if (!source) {
    card.innerHTML = `<div class="ie-output">Select a source character.</div>`;
    return;
  }
  card.innerHTML = `
    <div class="profile-source-main">
      <div class="profile-source-emblem" aria-hidden="true"></div>
      <div>
        <div class="profile-source-name">${_characterName(source)}</div>
        <div class="profile-source-subtitle">${_fileName(profilePath)} · Local EVE profile</div>
      </div>
    </div>
    <dl class="profile-source-facts">
      <dt>Character Name</dt><dd>${_characterName(source)}</dd>
      <dt>Character ID</dt><dd>${_characterIdLabel(source)}</dd>
      <dt>Profile Path</dt><dd>${profilePath || '-'}</dd>
      <dt>Character File</dt><dd>${_fileName(source.path || source.filePath || source.name || '')}</dd>
    </dl>
    <div class="profile-source-status-row">
      <span class="profile-ready-status profile-ready-status--ready">Overview Ready</span>
      <span class="profile-ready-status">Client status not checked</span>
    </div>
  `;
}

function _updateTargetCount() {
  const count = document.querySelectorAll('.character-dest-check:checked').length;
  const total = document.querySelectorAll('.character-dest-check').length;
  const label = document.getElementById('profile-target-count');
  if (label) label.textContent = `${count} of ${total} selected`;
}

function _openSelectedProfileFolder() {
  const profilePath = document.getElementById('character-profile')?.value || window._profileState.selectedProfilePath;
  if (!profilePath) {
    toast('Select a profile folder first.', 'warn');
    return;
  }
  toast(`Open folder manually: ${profilePath}`, 'warn');
}

async function _loadProfileReport(profilePath) {
  const resolveNames = document.getElementById('profile-resolve-names')?.checked ?? true;
  try {
    const data = await api('POST', '/profiles/report', { profilePath, resolveNames, includeChecksums: false });
    _renderProfileReport(data.report);
  } catch (e) {
    toast(e.message, 'error');
  }
}

function _renderProfileReport(report) {
  const panel = document.getElementById('profile-report-panel');
  if (!panel) return;
  const characters = report.files.filter(file => file.fileType === 'core_char');
  panel.innerHTML = `
    <div class="profile-report-summary">
      <span>${report.counts.coreUser} core_user</span>
      <span>${report.counts.coreChar} core_char</span>
      <span>${report.counts.prefs} prefs</span>
      <span>${_formatBytes(report.totalBytes)}</span>
    </div>
    <div class="profile-character-list">
      ${characters.map(file => `
        <div class="profile-character-row">
          <div>
            <div class="profile-row-title">${file.characterName || file.name}</div>
            <div class="profile-row-path">${file.name}${file.characterId ? ` · ${file.characterId}` : ''}</div>
          </div>
          <span class="mini-status">${_formatBytes(file.size)}</span>
        </div>
      `).join('') || '<div class="ie-output">No character files found.</div>'}
    </div>
  `;
}

async function _planProfileClone() {
  const sourcePath = document.getElementById('profile-source').value;
  const targetPath = document.getElementById('profile-target').value;
  if (!sourcePath || !targetPath) { toast('Select source and target profiles.', 'warn'); return; }
  try {
    const data = await api('POST', '/profiles/plan-clone', {
      sourcePath,
      targetPath,
      copyCoreUser: document.getElementById('clone-core-user').checked,
      copyCoreChar: document.getElementById('clone-core-char').checked,
      copyPrefs: document.getElementById('clone-prefs').checked,
      copyFirstToAll: document.getElementById('clone-copy-first').checked,
      resolveNames: document.getElementById('profile-resolve-names').checked,
    });
    window._profileState.latestPlan = data.plan;
    window._profileState.latestPlanKind = 'clone';
    window._profileState.latestBackupManifest = null;
    window._profileState.latestExecutionAudit = null;
    window._profileState.latestRollbackAudit = null;
    _renderClonePlan(data.plan);
    _renderWriteStatus(data.plan.blocked ? 'Plan is blocked. Fix warnings before backup/execution.' : 'Plan ready. Back up target files before execution.');
    _syncProfileWriteButtons();
    toast(data.plan.blocked ? 'Plan has blocking warnings' : 'Dry-run plan generated', data.plan.blocked ? 'warn' : 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _planCharacterClone() {
  const profilePath = document.getElementById('character-profile')?.value;
  const sourceCharacterId = Number(document.getElementById('character-source')?.value);
  const targetCharacterIds = [...document.querySelectorAll('.character-dest-check:checked')].map(input => Number(input.value));
  if (!profilePath || !sourceCharacterId) { toast('Select a source character.', 'warn'); return; }
  if (!targetCharacterIds.length) { toast('Select at least one destination character.', 'warn'); return; }
  try {
    const data = await api('POST', '/profiles/plan-character-clone', {
      profilePath,
      sourceCharacterId,
      targetCharacterIds,
      resolveNames: document.getElementById('profile-resolve-names').checked,
    });
    window._profileState.latestPlan = data.plan;
    window._profileState.latestPlanKind = 'clone';
    window._profileState.latestBackupManifest = null;
    window._profileState.latestExecutionAudit = null;
    window._profileState.latestRollbackAudit = null;
    _renderClonePlan(data.plan);
    document.getElementById('character-plan-output').textContent = _clonePlanText(data.plan);
    _renderWriteStatus(data.plan.blocked ? 'Plan is blocked. Fix warnings before backup/execution.' : 'Character overwrite plan ready. Back up destination files before execution.');
    _syncProfileWriteButtons();
    toast(data.plan.blocked ? 'Plan has blocking warnings' : 'Character overwrite plan generated', data.plan.blocked ? 'warn' : 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _backupProfileTargets() {
  const plan = window._profileState.latestPlan;
  const backupRoot = document.getElementById('profile-backup-root').value.trim();
  if (!plan || plan.blocked) { toast('Generate a non-blocked plan first.', 'warn'); return; }
  if (!backupRoot) { toast('Enter a backup root.', 'warn'); return; }
  try {
    const data = await api('POST', '/profiles/backup-plan', { plan, backupRoot });
    window._profileState.latestBackupManifest = data.backupManifest;
    window._profileState.latestExecutionAudit = null;
    window._profileState.latestRollbackAudit = null;
    _renderWriteStatus(`Backup ready\nManifest: ${data.backupManifest.manifestPath}\nFiles: ${data.backupManifest.fileList.length}\nOperation: ${data.backupManifest.operationId}`);
    _syncProfileWriteButtons();
    toast('Target backup created', 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _executeProfileClone() {
  const plan = window._profileState.latestPlan;
  const backupManifest = window._profileState.latestBackupManifest;
  if (!plan || !backupManifest) { toast('Backup targets before execution.', 'warn'); return; }
  const overwriteCount = plan.actions.filter(action => action.wouldOverwrite).length;
  const isPackageImport = window._profileState.latestPlanKind === 'package-import' || window._profileState.latestPlanKind === 'snapshot-restore';
  const operationLabel = window._profileState.latestPlanKind === 'snapshot-restore' ? 'Snapshot restore' : (isPackageImport ? 'Package import' : 'Clone');
  const ok = window.confirm(`Close the EVE client before continuing.\n\nThis will overwrite ${overwriteCount} file(s).\nBackup manifest:\n${backupManifest.manifestPath}\n\nProceed?`);
  if (!ok) return;
  try {
    const data = isPackageImport
      ? await api('POST', '/profiles/package/execute-import', { plan, backupManifest, packagePath: window._profileState.latestPackagePath || undefined })
      : await api('POST', '/profiles/execute-clone', { plan, backupManifest });
    window._profileState.latestExecutionAudit = data.executionAudit;
    _renderWriteStatus(`${operationLabel} executed\nAudit: ${data.executionAudit.auditManifestPath}\nActions: ${data.executionAudit.actionsApplied.length}`);
    _syncProfileWriteButtons();
    toast(`${operationLabel} executed`, 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _exportProfilePackage() {
  const profilePath = document.getElementById('character-profile')?.value || window._profileState.selectedProfilePath;
  const packagePath = document.getElementById('profile-package-path')?.value.trim();
  if (!profilePath) { toast('Scan and select a source profile first.', 'warn'); return; }
  if (!packagePath) { toast('Enter a package path.', 'warn'); return; }
  try {
    const data = await api('POST', '/profiles/package/export', {
      profilePath,
      packagePath,
      includeCoreUser: document.getElementById('package-core-user').checked,
      includeCoreChar: document.getElementById('package-core-char').checked,
      includePrefs: document.getElementById('package-prefs').checked,
    });
    window._profileState.latestPackagePath = packagePath;
    _renderPackageStatus(`Package exported\nPath: ${data.manifest.packagePath}\nFiles: ${data.manifest.fileList.length}\nOperation: ${data.manifest.operationId}`);
    toast('Profile package exported', 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _inspectProfilePackage() {
  const packagePath = document.getElementById('profile-package-path')?.value.trim();
  if (!packagePath) { toast('Enter a package path.', 'warn'); return; }
  try {
    const data = await api('POST', '/profiles/package/inspect', { packagePath });
    window._profileState.latestPackagePath = packagePath;
    const manifest = data.inspection.manifest;
    const errors = data.inspection.errors?.length ? `\nErrors:\n${data.inspection.errors.join('\n')}` : '';
    _renderPackageStatus(`Package OK: ${data.inspection.ok}\nFiles: ${manifest?.fileList?.length || 0}\nSnapshot: ${manifest?.snapshotName || '-'}${errors}`);
    toast(data.inspection.ok ? 'Package verified' : 'Package has errors', data.inspection.ok ? 'success' : 'warn');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _planProfilePackageImport() {
  const packagePath = document.getElementById('profile-package-path')?.value.trim();
  const destinationProfilePath = document.getElementById('package-destination-profile')?.value;
  if (!packagePath) { toast('Enter a package path.', 'warn'); return; }
  if (!destinationProfilePath) { toast('Select a destination profile.', 'warn'); return; }
  try {
    const data = await api('POST', '/profiles/package/plan-import', {
      packagePath,
      destinationProfilePath,
      resolveNames: document.getElementById('profile-resolve-names').checked,
    });
    window._profileState.latestPlan = data.plan;
    window._profileState.latestPlanKind = 'snapshot-restore';
    window._profileState.latestPackagePath = packagePath;
    window._profileState.latestBackupManifest = null;
    window._profileState.latestExecutionAudit = null;
    window._profileState.latestRollbackAudit = null;
    _renderPackagePlan(data.plan);
    _renderWriteStatus(data.plan.blocked ? 'Package import plan is blocked. Fix warnings before backup/execution.' : 'Package import plan ready. Back up destination files before execution.');
    _syncProfileWriteButtons();
    toast(data.plan.blocked ? 'Package import plan blocked' : 'Package import plan generated', data.plan.blocked ? 'warn' : 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _saveProfileSnapshot() {
  const profilePath = document.getElementById('character-profile')?.value || window._profileState.selectedProfilePath;
  const libraryRoot = document.getElementById('profile-snapshot-root')?.value.trim();
  const snapshotName = document.getElementById('profile-snapshot-name')?.value.trim();
  if (!profilePath) { toast('Scan and select a profile first.', 'warn'); return; }
  if (!libraryRoot) { toast('Enter a snapshot library root.', 'warn'); return; }
  if (!snapshotName) { toast('Enter a snapshot name.', 'warn'); return; }
  try {
    const data = await api('POST', '/profiles/snapshots/save', {
      profilePath,
      libraryRoot,
      snapshotName,
      notes: document.getElementById('profile-snapshot-notes')?.value.trim() || null,
      includeCoreUser: document.getElementById('snapshot-core-user').checked,
      includeCoreChar: document.getElementById('snapshot-core-char').checked,
      includePrefs: document.getElementById('snapshot-prefs').checked,
    });
    window._profileState.selectedSnapshotPath = data.manifest.packagePath;
    _renderSnapshotStatus(`Snapshot saved\nPath: ${data.manifest.packagePath}\nFiles: ${data.manifest.fileList.length}`);
    await _listProfileSnapshots();
    toast('Profile snapshot saved', 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _listProfileSnapshots() {
  const libraryRoot = document.getElementById('profile-snapshot-root')?.value.trim();
  if (!libraryRoot) { toast('Enter a snapshot library root.', 'warn'); return; }
  try {
    const data = await api('POST', '/profiles/snapshots/list', { libraryRoot });
    _renderSnapshotList(data.snapshots || []);
    toast(`Found ${data.snapshots?.length || 0} snapshot(s)`, 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _planProfileSnapshotRestore() {
  const packagePath = window._profileState.selectedSnapshotPath;
  const destinationProfilePath = document.getElementById('snapshot-destination-profile')?.value;
  if (!packagePath) { toast('Select a snapshot first.', 'warn'); return; }
  if (!destinationProfilePath) { toast('Select a restore destination profile.', 'warn'); return; }
  try {
    const data = await api('POST', '/profiles/package/plan-import', {
      packagePath,
      destinationProfilePath,
      resolveNames: document.getElementById('profile-resolve-names').checked,
    });
    window._profileState.latestPlan = data.plan;
    window._profileState.latestPlanKind = 'package-import';
    window._profileState.latestPackagePath = packagePath;
    window._profileState.latestBackupManifest = null;
    window._profileState.latestExecutionAudit = null;
    window._profileState.latestRollbackAudit = null;
    _renderSnapshotPlan(data.plan);
    _renderWriteStatus(data.plan.blocked ? 'Snapshot restore plan is blocked. Fix warnings before backup/execution.' : 'Snapshot restore plan ready. Back up destination files before execution.');
    _syncProfileWriteButtons();
    toast(data.plan.blocked ? 'Snapshot restore plan blocked' : 'Snapshot restore plan generated', data.plan.blocked ? 'warn' : 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

async function _rollbackProfileBackup() {
  const backupManifest = window._profileState.latestBackupManifest;
  if (!backupManifest) { toast('No backup manifest is available.', 'warn'); return; }
  const ok = window.confirm(`Close the EVE client before continuing.\n\nThis will restore files from backup manifest:\n${backupManifest.manifestPath}\n\nProceed with rollback?`);
  if (!ok) return;
  try {
    const data = await api('POST', '/profiles/rollback-backup', { backupManifest });
    window._profileState.latestRollbackAudit = data.rollbackAudit;
    _renderWriteStatus(`Rollback complete\nAudit: ${data.rollbackAudit.auditManifestPath}\nActions: ${data.rollbackAudit.actionsApplied.length}`);
    _syncProfileWriteButtons();
    toast('Rollback complete', 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

function _syncProfileWriteButtons() {
  const plan = window._profileState.latestPlan;
  const backup = window._profileState.latestBackupManifest;
  const execution = window._profileState.latestExecutionAudit;
  const canBackup = Boolean(plan && !plan.blocked && plan.actions.length);
  const canExecute = Boolean(canBackup && backup && !execution);
  const canRollback = Boolean(backup && execution);
  const backupButton = document.getElementById('profile-backup-targets');
  const executeButton = document.getElementById('profile-execute-clone');
  const rollbackButton = document.getElementById('profile-rollback');
  if (backupButton) backupButton.disabled = !canBackup;
  if (executeButton) {
    executeButton.disabled = !canExecute;
    if (window._profileState.latestPlanKind === 'snapshot-restore') executeButton.textContent = 'Execute Restore';
    else if (window._profileState.latestPlanKind === 'package-import') executeButton.textContent = 'Execute Package Import';
    else executeButton.textContent = 'Execute Clone';
  }
  if (rollbackButton) rollbackButton.disabled = !canRollback;
}

function _renderWriteStatus(message) {
  const output = document.getElementById('profile-write-output');
  if (output) output.textContent = message;
}

function _renderPackageStatus(message) {
  const output = document.getElementById('profile-package-output');
  if (output) output.textContent = message;
}

function _renderPackagePlan(plan) {
  const output = document.getElementById('profile-package-output');
  if (!output) return;
  const warningHtml = plan.warnings?.length
    ? `<div class="profile-preflight-warnings">${plan.warnings.map(warning => `<div>${_escapeHtml(warning)}</div>`).join('')}</div>`
    : '';
  const rows = plan.actions?.length
    ? plan.actions.map(action => `
      <div class="profile-preflight-row">
        <span>${_escapeHtml(action.fileType)}</span>
        <span>
          <strong>${_escapeHtml(action.sourceName || action.sourceId || '-')}</strong>
          <small>${_escapeHtml(action.sourceId || '-')}</small>
        </span>
        <span>
          <strong>${_escapeHtml(action.targetName || action.targetId || '-')}</strong>
          <small>${_escapeHtml(_fileName(action.targetFile))}</small>
        </span>
        <span class="${action.wouldOverwrite ? 'profile-risk-warn' : ''}">${action.wouldOverwrite ? 'Overwrite' : 'Create'}</span>
        <span>${_escapeHtml(action.risk)}</span>
      </div>
    `).join('')
    : '<div class="ie-output">No import actions.</div>';
  output.innerHTML = `
    <div class="profile-preflight-summary">
      <span>Operation ${_escapeHtml(plan.operationId)}</span>
      <span>${plan.summary?.plannedActionCount || 0} action(s)</span>
      <span>${plan.blocked ? 'Blocked' : 'Ready for backup'}</span>
    </div>
    <div class="profile-preflight-table">
      <div class="profile-preflight-head">
        <span>Type</span>
        <span>Package Source</span>
        <span>Destination</span>
        <span>Write</span>
        <span>Risk</span>
      </div>
      ${rows}
    </div>
    ${warningHtml}
  `;
}

function _renderSnapshotStatus(message) {
  const output = document.getElementById('profile-snapshot-output');
  if (output) output.textContent = message;
}

function _renderSnapshotList(snapshots) {
  const output = document.getElementById('profile-snapshot-output');
  if (!output) return;
  if (!snapshots.length) {
    output.textContent = 'No snapshots found in this library.';
    return;
  }
  output.innerHTML = `
    <div class="profile-snapshot-list">
      ${snapshots.map(snapshot => `
        <button class="profile-snapshot-row ${snapshot.packagePath === window._profileState.selectedSnapshotPath ? 'is-selected' : ''}" data-snapshot-path="${_escapeAttr(snapshot.packagePath)}">
          <span>
            <strong>${_escapeHtml(snapshot.snapshotName || _fileName(snapshot.packagePath))}</strong>
            <small>${_escapeHtml(snapshot.notes || snapshot.timestamp || '')}</small>
          </span>
          <span class="${snapshot.ok ? 'profile-ready-status profile-ready-status--ready' : 'profile-ready-status'}">${snapshot.ok ? 'Verified' : 'Check failed'}</span>
          <span>${snapshot.fileCount} file(s)</span>
        </button>
      `).join('')}
    </div>
  `;
  output.querySelectorAll('.profile-snapshot-row').forEach(row => {
    row.addEventListener('click', () => {
      window._profileState.selectedSnapshotPath = row.dataset.snapshotPath;
      output.querySelectorAll('.profile-snapshot-row').forEach(item => item.classList.toggle('is-selected', item === row));
    });
  });
}

function _renderSnapshotPlan(plan) {
  _renderPackagePlan(plan);
  const packageOutput = document.getElementById('profile-package-output');
  const snapshotOutput = document.getElementById('profile-snapshot-output');
  if (packageOutput && snapshotOutput) {
    snapshotOutput.innerHTML = packageOutput.innerHTML;
  }
}

function _renderClonePlan(plan) {
  const output = document.getElementById('profile-plan-output');
  if (!output) return;
  output.textContent = _clonePlanText(plan);
}

function _clonePlanText(plan) {
  const rows = plan.actions.map(action => `${action.fileType}: ${action.sourceId || '-'} -> ${action.targetId || '-'} (${action.risk})`).join('\n');
  const warnings = plan.warnings.length ? `\n\nWarnings:\n${plan.warnings.join('\n')}` : '';
  return `Operation: ${plan.operationId}\nActions: ${plan.summary.plannedActionCount}\nBlocked: ${plan.blocked}\n\n${rows || 'No actions.'}${warnings}`;
}

function _fileName(path) {
  return String(path || '').split(/[\\/]/).pop() || path;
}

function _formatBytes(value) {
  if (value > 1024 * 1024) return `${(value / 1024 / 1024).toFixed(1)} MB`;
  if (value > 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${value} B`;
}

function _escapeAttr(value) {
  return String(value).replace(/"/g, '&quot;');
}

function _escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function _characterLabel(character) {
  return `${_characterName(character)} (${_characterIdLabel(character)})`;
}

function _characterName(character) {
  return character.characterName || `Character ${character.characterId}`;
}

function _characterIdLabel(character) {
  return character.characterId || 'unknown';
}
