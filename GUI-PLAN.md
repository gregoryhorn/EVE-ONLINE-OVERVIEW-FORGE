# Overview Forge GUI Plan

This document is the implementation plan for the local GUI. The visual direction is based primarily on the files in `GUI Example images/`, especially the dark EVE-style shell, persistent live preview, left navigation rail, and bottom status strip.

The GUI is a local browser app over the existing Python core. It must not bypass the safety rules already enforced by the CLI.

## Current Baseline

Stack:
- FastAPI backend served by `eve-overview gui`
- Plain HTML/CSS/JS frontend
- No npm, Node, Electron, or frontend build step
- Local browser target: `http://localhost:7477`

Existing GUI files:
- `src/eve_overview_manager/gui/server.py`
- `src/eve_overview_manager/gui/state.py`
- `src/eve_overview_manager/gui/routes/`
- `src/eve_overview_manager/gui/static/index.html`
- `src/eve_overview_manager/gui/static/app.css`
- `src/eve_overview_manager/gui/static/app.js`
- `src/eve_overview_manager/gui/static/screens/`

Existing screens/routes already present in code:
- Dashboard
- Tabs
- Presets
- Types & States
- Appearance
- Columns
- Brackets
- Validation route
- Recent files route

Major GUI work still pending:
- Work through `GAP-CHECK-PLAN.md` before more visual-only GUI work.
- Profiles visual polish and browser QA
- Import / Export screen polish: snapshots, deploy confirmation, richer validation
- Full validation panel workflow
- End-to-end GUI polish and browser smoke testing

Implemented GUI support services/routes:
- `GET /api/preferences`
- `PATCH /api/preferences`
- `POST /api/paths/unique-output`
- `POST /api/export/yaml`
- `POST /api/export/json`
- `POST /api/import/generator`
- `POST /api/profiles/scan`
- `POST /api/profiles/report`
- `POST /api/profiles/plan-clone`
- `POST /api/profiles/backup-plan`
- `POST /api/profiles/execute-clone`
- `POST /api/profiles/rollback-backup`
- `GET /api/preview`
- Preference storage defaults import/export to the current user's `Documents\EVE\Overview`.
- Unique output path generation prevents accidental overwrite.

Product decisions from user:
- Default import/export folder is the current user's `Documents\EVE\Overview`.
- If the user changes the import/export folder, remember the new folder.
- Do not overwrite existing exported files; generate a new filename instead.
- Character name resolution in the GUI defaults to on.
- Local SDE/group metadata should be included with the app where practical.
- Keep one in-memory document initially. Add periodic local draft autosave only after core workflows are stable.

## Visual Direction

Use the sample images as the main look-and-feel source of truth:

- `GUI Example images/APPLICATION SAMPLE IMAGE 2  .png`: Dashboard target.
- `GUI Example images/APPLICATION SAMPLE IMAGE 3  .png`: Appearance target.
- `GUI Example images/APPLICATION SAMPLE IMAGE 4  .png`: Types & States target.
- `GUI Example images/APPLICATION SAMPLE IMAGE 5  .png`: Tabs target.

Design principles:
- Dense, operational EVE-style interface.
- Dark translucent panels over a subtle starfield background.
- Persistent left navigation rail.
- Persistent top action bar.
- Persistent right-side live overview preview where screen space allows.
- Persistent bottom status strip with warning, validation, backup, and folder actions.
- No marketing/landing page.
- Avoid decorative cards that do not carry data or actions.
- Prefer compact tables, lists, segmented controls, toggles, color swatches, and icon buttons.

Visual tokens:

```text
Outer background:       #05080c / starfield image treatment
Panel background:       rgba(10, 15, 20, 0.86)
Panel border:           #22303a
Header/nav:             rgba(5, 8, 12, 0.92)
Accent cyan:            #00d4ff
Accent green:           #39ff88
Accent red:             #ff4444
Accent orange:          #ff9a22
Accent yellow:          #ffcc33
Accent purple:          #b56cff
Text primary:           #d8e0ea
Text secondary:         #7f8b99
Text muted:             #586370
```

Typography:
- Condensed/technical feel, similar to the screenshots.
- Use local/system font fallbacks; do not require network font loading.
- Keep UI text compact and scannable.
- Tables and numeric fields should use monospace or tabular figures.

Layout:
- Desktop first, because this is a local power-user tool.
- Left rail fixed width around 220-260px.
- Work area and preview area split according to screen:
  - Dashboard: summary/work cards left, live preview right.
  - Editing screens: editor left, live preview right.
- Profiles screen: full-width source/target workflow with status below; it does not show the overview live preview because profile cloning is separate from YAML preview behavior.
- Import screen: workflow left, contextual preview/status right.
- Bottom status strip remains visible on desktop.
- Mobile/tablet can stack panels, but this is not the primary design target.

## Product Boundaries

The GUI must remain a local configuration/editor tool:
- Do not modify the running EVE client.
- Do not automate in-game UI.
- Do not parse or edit `core_user_*.dat` or `core_char_*.dat`.
- Treat EVE profile files as opaque.
- Profile writes require a reviewed plan, verified backup, and audit output.
- Character name resolution defaults to on in the GUI, but normal non-GUI profile scanning remains offline unless resolution is requested.
- Normal profile scanning remains offline.
- ESI is not a core dependency.
- XML import is intentionally closed/deferred.

## Information Architecture

The GUI should follow the real EVE overview workflow, not expose every YAML section as an equal top-level destination. In EVE, users normally work from the overview tab outward:

1. Choose or create a tab.
2. Assign the tab's overview preset and bracket preset.
3. Edit the assigned overview preset's visible types/groups and state filters.
4. Adjust global columns, labels, and appearance rules.
5. Validate, export YAML, then import it manually in the EVE client.

The app should make this dependency chain obvious. A user should not need to understand the raw YAML layout before making a useful change.

Primary navigation order:

1. Dashboard
2. Tabs
3. Presets
4. Columns
5. Appearance
6. Import / Export
7. Profiles
8. Advanced

Advanced contains lower-frequency or reference tools:
- Types & States reference/catalog.
- Bracket preset assignment details, unless promoted into the Tabs screen.
- Raw YAML/canonical JSON inspection if added later.
- SDE/group metadata utilities.

Top action bar:
- Import YAML
- Validate
- Export
- Backup

Bottom status bar:
- Warning/error count.
- Short actionable warning text.
- Validation status and timestamp.
- Last backup status.
- Open backup folder action.

## Screen Status

| Screen | Current Status | Required Adjustment |
|---|---|---|
| Dashboard | Implemented | Includes Standard/Blank/PVP/Mining new-overview templates; align closer to sample image 2 and wire live validation/backup data where useful |
| Tabs | Implemented | Main editing hub: selected tab, overview preset assignment, bracket preset assignment, color/label, preset editor actions, and preview context |
| Presets | Implemented | Make this a preset editor reached from Tabs; show which tabs use the preset and make selected groups/states match imports |
| Types & States | Implemented | Moved under Advanced as a reference/catalog screen, not a primary workflow |
| Appearance | Implemented | Loads selected states, saves EVE-style appearance keys, and refreshes preview |
| Columns | Implemented | Uses document column config as preview source; polish only unless behavior gaps appear |
| Brackets | Implemented | Moved under Advanced; bracket preset assignment is visible from Tabs and does not control overview table rows |
| Profiles | Implemented | Character-copy workbench with source card, target character table, guarded backup/execute/rollback, and collapsed advanced folder clone |
| Import / Export | Implemented foundation | Browse import, remembered folders, unique filenames, grouped validation, export confirmation, and manual snapshots; add deploy guidance polish |
| Full validation panel | Implemented foundation | Import / Export panel groups validation details; future work can add filters and deep links |

## Overview Behavior Model

This section records the GUI behavior model confirmed from the research report, CCP support documentation, EVE University overview documentation, Evans Osenko's generator, and Z-S Overview Customizer.

Confirmed:
- A tab binds two related presets: an overview preset for the table and a bracket preset for in-space brackets.
- Presets combine type/group selection with state rules. Type/group membership decides which entity classes are eligible; state rules can force visibility or hide matching entities.
- Appearance settings are separate from visibility. Row text color, background, and blink behavior should be resolved from state priority after the row is considered visible.
- Column settings are separate from visibility. Hiding a column should change only the rendered columns, not whether an entity appears.
- EVE profile/layout files remain unrelated to preview generation and must stay opaque.

Workflow model:
- **Tabs are the control center.** Selecting a tab establishes the active overview preset, active bracket preset, preview context, and quick links into editing the bound preset.
- **Overview presets control table visibility.** The Presets screen should always make it clear which tabs use the selected preset. Editing groups/states edits the preset, not the tab. On the Presets screen, the live preview should be driven directly by the selected preset and should not show the tab strip.
- **Bracket presets control in-space bracket visibility.** They share the same preset data shape, but they do not control the overview table. Until a bracket-specific preview exists, bracket editing should be framed as "assigned bracket preset" rather than a fake overview preview mode.
- **Types & States are ingredients, not the main workflow.** Players do not normally start by editing the global type/state catalog. Keep it as a reference or advanced bulk-edit screen.
- **Columns are global presentation.** Column toggles and ordering should update the preview headers/cells for the active tab, but they should not affect which entities are visible.
- **Appearance is global state priority.** Appearance controls should show the current priority/order and color/background/blink settings. Edits should affect row styling after preset filtering has already decided visibility.
- **Import / Export is the safe boundary.** Import loads a YAML document into memory. Export writes a new unique file to `Documents\EVE\Overview` or the remembered folder. The user still imports the YAML manually inside EVE.
- **Profiles are a separate workflow.** Profile cloning copies opaque character/account settings. It should not be mixed with YAML overview editing, preview filtering, or export.

Expected user paths:
- **Load and inspect a pack:** Import YAML -> Dashboard summary -> Tabs -> select each tab -> inspect bound preset and preview.
- **Change what a tab shows:** Tabs -> select tab -> open bound overview preset -> change groups/states -> preview updates -> validate.
- **Create a new tab:** Tabs -> add tab -> assign overview preset and bracket preset -> choose color/label -> preview uses the assigned overview preset.
- **Create a new preset:** Presets -> duplicate or create preset -> choose groups/states -> assign it to one or more tabs from Tabs.
- **Tune display:** Columns/Appearance -> edit global presentation -> active tab preview updates without changing visibility.
- **Ship to EVE:** Validate -> Export with review -> save unique YAML -> manually import in EVE client.
- **Clone character layout/profile:** Profiles -> scan profile folder -> confirm the source character card -> select destination characters in the target table -> dry-run plan -> backup -> execute.
- **Save and restore known-good profile:** Profiles -> scan profile folder -> choose a known-good character/profile scope -> create a named local profile snapshot package -> later inspect snapshot -> compare against current local files -> dry-run restore -> backup current files -> restore.
- **Move profile settings to another PC:** Source PC -> scan profile folder -> select source character/account files -> export a portable transfer package -> copy the package manually to the other PC -> destination PC scans its local profile folder -> import package only after matching account/character IDs are confirmed -> dry-run plan -> backup -> execute.

Current implementation:
- `GET /api/preview` builds the live preview in Python from the current canonical document.
- The browser no longer owns the filtering logic; it renders backend preview rows, active tab state, and selected columns.
- The main preview should use the active tab's `overviewPresetRef`. Bracket-specific preview remains deferred until it can represent in-space bracket behavior accurately.
- The Presets screen needs a selected-preset preview context. That preview should hide tab controls and update when the selected preset changes, because presets are assigned to tabs but are edited independently.
- The preview uses a local sample catalog containing structures, stargates, celestials, ships, drones, wrecks, and deployables.
- Preview rows include a small local group-name map for the bundled sample catalog. Full SDE-backed type/group metadata is still pending.
- The core can build a separate SDE-backed `group_names.json` for future GUI metadata. The preview engine already accepts an optional group-name map and falls back to the bundled sample map.
- The Import / Export screen exposes a `group_names.json` preference. When set, `/api/preview` loads that local file and uses it for sample row group names.
- The Import / Export screen includes a grouped validation panel. It reuses `/api/validate`, groups results by subsystem, and shows result code, message, path, and suggested fix.
- Export actions use a review-before-write flow. The app resolves the final unique output path and validation status before enabling the final export confirmation.
- Manual snapshot creation is available from Import / Export. Snapshots write canonical JSON plus checksum manifests to a user-chosen local snapshot root and can be listed from the GUI.
- Presets, Appearance, and Columns received a correctness pass: loaded selections are reflected, saves update the canonical document, and live preview refreshes after edits.
- Appearance now uses the in-game state label wording, the 12-color EVE color picker palette, in-game default tag colors, and separate foreground/background blink rendering.
- Stabilization fixes: tab edits now refresh backend preview output, slot `0` tabs are handled correctly, Presets shows preserved raw numeric group IDs even when no checkbox mapping exists, and the confusing bracket-mode preview toggle is hidden until a proper bracket-specific view exists.
- Community overview fixtures in `Examples/community-overviews/` should be used during future GUI correctness passes so screens are checked against several real overview shapes, not only one local export.
- Preview rows expose resolved appearance metadata: flag state, background state, mapped colors, and blink flags. The GUI uses background color and blink markers when available, and color-tag blink is rendered separately from background blink.
- Empty preset group lists render no sample rows unless an always-shown state matches. This is more useful for editing than treating an empty group list as "show all."

Known approximation:
- The preview is an editor aid, not a live EVE client simulator. Exact icon art, full SDE type names, and per-tab column edge cases will be refined as real exports and SDE metadata are added. The sample catalog must still include rows for every visible state filter; otherwise state filter changes cannot be validated visually.

## Profiles Screen Plan

This is the next highest-value GUI screen because the core now supports safe profile workflows.

Core APIs to use:
- `scan_profiles`
- `build_profile_report`
- `resolve_character_names`
- `plan_clone`
- `create_backup_from_clone_plan`
- `execute_clone`
- `rollback_backup`

Existing CLI commands that define behavior:
- `scan-profiles`
- `profile-report`
- `plan-clone`
- `backup-plan`
- `execute-clone`
- `rollback-backup`

Future CLI/API commands needed for cross-PC transfer:
- `export-profile-package`
- `inspect-profile-package`
- `plan-profile-package-import`
- `execute-profile-package-import`
- Basic GUI routes, Profiles package controls, Same PC / Other PC / Snapshots mode switch, snapshot library list/save controls, and package preflight source/destination name comparison exist; next pass should focus on visual QA and workflow wording polish.

Primary visual structure:
- Left/work area: three-step workflow.
- Right/context area: selected profile report, character list, file readiness, and latest operation audit.
- Bottom strip: warnings, validation/backup state, open backup folder.

Step 1: Scan
- EVE root path input.
- Suggested path:
  `%LOCALAPPDATA%\CCP\EVE\c_ccp_eve_tq_tranquility`
- Button: Scan Profiles.
- Toggle: Resolve character names, default on.
- Optional cache path advanced field.
- Results list of `settings_*` folders.
- Each profile row shows:
  - Profile folder name.
  - `core_user` count.
  - `core_char` count.
  - `prefs.ini` present/missing.
  - Backup readiness.
  - Warning badge if placeholder/weird files exist.

Step 2: Inspect
- Selected profile report from `profile-report` shape.
- Use `Examples/sample_profile_report.json` as fixture during GUI development.
- Show character files as named rows when known:
  - Character name.
  - Character ID.
  - File name.
  - Size.
  - Last modified.
- Show `core_user_*` files separately because they are account/profile scoped and not mapped to character names.
- Show placeholder/weird files separately:
  - `core_char__.dat`
  - `core_user__.dat`
  - `core_char_('char', None, 'dat').dat`
- Do not imply ownership for `core_user_*` files.

Step 3: Character Overwrite Workflow
- Profile folder selector.
- Source character selector.
- Destination character multi-select.
- Button: Generate Character Overwrite Plan.
- The plan copies the selected source `core_char_<id>.dat` to each selected destination `core_char_<id>.dat`.
- `core_user_*.dat` and `prefs.ini` are profile/account scoped and stay in the advanced folder-clone workflow.

Step 4: Cross-PC Transfer Package Workflow
- This is separate from same-PC character overwrite.
- Source PC:
  - Scan the local EVE profile folder.
  - Select one source character and, optionally, account-scoped files.
  - Export a portable package such as `eve-profile-transfer.zip`.
  - Include copied opaque files plus a JSON manifest.
- Package manifest should include:
  - Tool schema version and app version.
  - Source profile path for user reference only.
  - Source machine timestamp and operation ID.
  - File list with file type, source file name, size, SHA-256, and source ID.
  - Character metadata from `core_char_<id>.dat`: character ID and resolved character name when available.
  - Account/profile metadata from `core_user_<id>.dat` without claiming character ownership.
  - Explicit note that `.dat` files are opaque and were not parsed.
- Destination PC:
  - User scans the local EVE profile folder on that PC.
  - User imports or inspects the package.
  - The app compares package character IDs/names with destination `core_char_<id>.dat` files.
  - The app compares account-scoped `core_user_<id>.dat` IDs only when account files are included.
  - Import is blocked by default if required character IDs are missing.
  - Import is blocked by default if destination account/profile IDs do not match included account-scoped files.
  - Any force/override option must be advanced, noisy, and still require backup.
- Import plan:
  - Always dry-run first.
  - Show source package file, destination file, file type, character/account ID, resolved names, overwrite status, and risk.
  - Never delete destination files.
  - Require backup-before-write and write an import audit manifest.
- GUI layout:
  - Add a transfer mode switch inside Profiles: `Same PC` and `Other PC`.
  - `Same PC` keeps the current source-card/target-table workflow.
  - `Other PC` shows two subflows: `Export Package` and `Import Package`.
  - Import Package must show a prominent preflight comparison table before enabling backup.

Step 5: Known-Good Profile Snapshot Workflow
- This is for saving a trusted local character/profile state and restoring it later.
- It should reuse the profile package manifest/checksum format where practical.
- Snapshot creation:
  - User scans a local profile folder.
  - User selects a character profile, and optionally account-scoped files if they understand the wider impact.
  - User enters a snapshot name and optional note, such as `Pre-war clean overview` or `Mining profile baseline`.
  - The app writes a local snapshot package under a user-chosen snapshot library folder.
  - Snapshot package includes opaque files plus manifest, checksums, character IDs/names, created timestamp, and user note.
- Snapshot restore:
  - User selects a saved profile snapshot.
  - The app verifies package checksums before planning restore.
  - The app scans the current local destination profile folder.
  - The app compares snapshot character/account IDs against current destination IDs.
  - Restore is blocked if the target character/account ID is missing unless a future advanced override exists.
  - Restore is always dry-run first, then backup current files, then execute.
  - Restore writes an audit manifest and keeps the pre-restore backup available for rollback.
- GUI layout:
  - Add `Snapshots` as a third mode inside Profiles after `Same PC` and `Other PC`, or add it as a section under `Other PC` if the package UI is shared.
  - Show saved snapshots as a list with name, character, profile scope, timestamp, file count, and verification status.
  - The restore preflight table should show snapshot file, current destination file, ID match, checksum status, overwrite status, and risk.

Advanced Folder Clone Workflow
- Source profile selector.
- Target profile selector.
- Toggles for `core_user`, `core_char`, `prefs.ini`, and Copy First To All.
- Button: Generate Dry-Run Plan.
- Plan table columns:
  - File type.
  - Source ID/name.
  - Target ID/name.
  - Risk.
  - Would overwrite.
  - Source file.
  - Target file.
- Button: Backup Targets.
- Backup summary:
  - Manifest path.
  - File count.
  - Checksum count.
  - Operation ID.
- Button: Execute Clone, disabled until plan is reviewed and backup exists.
- Confirmation modal must show exact overwrite count and backup manifest path.
- Post-execution panel:
  - Execution audit manifest path.
  - Operation ID.
  - Timestamp.
  - Per-action before/after checksums.
- Rollback panel:
  - Button: Roll Back From Backup.
  - Requires selecting the exact backup manifest.
  - Shows rollback manifest path after completion.

Safety rules:
- No execute button without a generated plan and verified backup.
- No destructive delete behavior.
- No `.dat` field parsing.
- EVE client close warning before execute/rollback.
- All write actions must display exact target files before running.

## Import / Export Screen Plan

Core APIs to use:
- `load_overview_yaml`
- `export_overview_yaml`
- `roundtrip_overview_yaml`
- `load_overview_json`
- `export_overview_json`
- `create_overview_snapshot`
- `restore_snapshot`
- `restore_snapshot_to_yaml`
- `build_overview_document`
- `generate-json`
- `generate-yaml`

Primary sections:

Import:
- Load EVE YAML.
- Load canonical JSON.
- Load generator spec JSON.
- Default folder: `%USERPROFILE%\Documents\EVE\Overview`.
- Remember the most recently selected import/export folder.
- Show import warnings from tolerant YAML parsing.
- Preserve unknown YAML keys.
- No XML path; show “XML import is intentionally deferred” if user selects XML.

Export:
- Export EVE-compatible YAML.
- Export canonical JSON.
- Export generated YAML/JSON from generator spec.
- Default export target: `%USERPROFILE%\Documents\EVE\Overview`.
- If a file already exists, do not overwrite it. Generate a new filename such as `name_2.yaml`, `name_3.yaml`, etc.
- Remember any user-selected export folder and use it as the next default.
- Require confirmation before writing directly to the EVE Overview folder.
- Create snapshot before overwriting app-managed outputs.

Validation:
- Run current validation engine.
- Optional local group ID file.
- Optional SDE workflow link:
  - Download SDE.
  - Build group index.
  - Validate with group IDs.
- Group validation remains offline after the local index exists.

Snapshots:
- List snapshots.
- Restore snapshot to explicit output path only.
- No overwrite unless confirmed.

## Validation Panel Plan

Use structured validation results:
- `code`
- `severity`
- `message`
- `path`
- `suggestedFix`

UI behavior:
- Group by section: tabs, presets, states, columns, appearance, unknown data, profiles.
- Clicking a validation row navigates to the relevant screen where possible.
- Bottom status bar shows counts.
- Warnings do not block export; errors require explicit acknowledgement.

Important rules to surface clearly:
- Current tab cap defaults to 20.
- Legacy cap is 5.
- Preset refs can use built-ins like `_BracketFilterShowAll` and `DefaultPreset_<digits>`.
- Unknown YAML data is preserved.
- SDE group checks are optional.

## Live Overview Preview

The live preview is the signature feature and should stay visible on major overview-editing screens.

Use sample images as reference:
- Tab strip at top with colored labels.
- Dense table with EVE-like columns.
- State-colored rows for fleet, suspect, criminal, alliance, neutral, drones, structures.
- “Live” indicator.
- Fit columns control.
- Previewing label at bottom.

Preview rows are synthetic. They must not imply live EVE data.
The default preview sample set should include real overview-style entities from `Overview Example Images/Overview-Normal.png`: Keepstar, Fortizar, Tatara, Sotiyo, Astrahus, Stargate, Ansiblex Jump Bridge, Cynosural Field/Beacon, Planet, Celestial Beacon, Sovereignty Hub, Sun, drones, moons, and ships. The preview must filter synthetic rows through the active tab's bound preset groups and state rules so user changes are reflected immediately.

Minimum preview row categories:
- Fleet member.
- Corp member.
- Alliance member.
- Neutral.
- Bad standing.
- Suspect.
- Criminal.
- War target.
- Drone.
- Structure.
- Stargate/celestial.

The preview should reflect:
- Current tab selection.
- Bound overview preset.
- Column order/enabled columns.
- Appearance color/background/blink settings.
- Bracket/label settings where practical.

## API Plan

Current implemented route naming uses `/api/document/...` paths for many edit operations. Continue that convention unless there is a strong reason to change.

Document:
- `GET /api/document`
- `POST /api/document/load`
- `POST /api/document/new`

Tabs:
- `GET /api/document/tabs`
- `POST /api/document/tabs`
- `PATCH /api/document/tabs/{slot}`
- `DELETE /api/document/tabs/{slot}`
- `POST /api/document/tabs/{slot}/duplicate`
- `POST /api/document/tabs/reorder`

Presets:
- `GET /api/document/presets`
- `POST /api/document/presets`
- `PATCH /api/document/presets/{preset_id}`
- `DELETE /api/document/presets/{preset_id}`
- `POST /api/document/presets/{preset_id}/duplicate`

Appearance/columns/brackets:
- `GET /api/document/appearance`
- `PATCH /api/document/appearance`
- `GET /api/document/columns`
- `PATCH /api/document/columns`
- `GET /api/document/labels`
- `PATCH /api/document/labels`

Validation:
- `POST /api/validate`

Profiles to add:
- `POST /api/profiles/scan`
- `POST /api/profiles/report`
- `POST /api/profiles/plan-clone`
- `POST /api/profiles/backup-plan`
- `POST /api/profiles/execute-clone`
- `POST /api/profiles/rollback-backup`

Import/export to add:
- `GET /api/preferences`
- `PATCH /api/preferences`
- `POST /api/paths/unique-output`
- `POST /api/import/yaml`
- `POST /api/import/json`
- `POST /api/import/generator`
- `GET /api/export/yaml`
- `GET /api/export/json`
- `POST /api/export/yaml/deploy`
- `POST /api/snapshots/create`
- `GET /api/snapshots`
- `POST /api/snapshots/restore`

Recent:
- `GET /api/recent-files`

## File Structure Target

Current route files should be kept and extended rather than renamed broadly.

Add when implementing remaining screens:

```text
src/eve_overview_manager/gui/routes/
  profiles_route.py
  import_export_route.py
  snapshots_route.py

src/eve_overview_manager/gui/static/screens/
  profiles.js
  import_export.js
```

Optional shared frontend helpers, only if duplication becomes real:

```text
src/eve_overview_manager/gui/static/components/
  live_preview.js
  profile_file_table.js
  validation_panel.js
```

Do not add a frontend framework during this phase.

## Build Phases From Here

Phase D polish:
- Align Dashboard, Tabs, Types & States, Appearance, Columns, and Brackets with the sample image visual system.
- Keep changes scoped to existing behavior.

Phase E Profiles:
- Add profile API routes.
- Add `profiles.js`.
- Build scan/report/plan/backup/execute/rollback flow.
- Use `Examples/sample_profile_report.json` during development.
- Verify no write button is enabled before backup requirements are met.

Phase F Import / Export:
- Add import/export routes.
- Add `import_export.js`.
- Support YAML, canonical JSON, generator specs, snapshots, validation, and deploy-to-overview-folder confirmation.

Phase G Validation and status:
- Full validation panel.
- Bottom status strip wired to real validation and backup state.
- Warning counts clickable.
- Section navigation from validation rows.

Phase H Browser QA:
- Start `eve-overview gui`.
- Use browser automation/screenshots at desktop widths.
- Verify sample images are followed for density, layout, and visual tone.
- Verify no overlapping text.
- Verify major workflows:
  - Load YAML.
  - Edit tabs.
  - Validate.
  - Export YAML.
  - Profile report.
  - Clone plan dry-run.
  - Backup/execute remains guarded.

## Dependency Notes

GUI dependencies belong in the existing optional dependency group:

```toml
[project.optional-dependencies]
gui = [
    "fastapi>=0.111",
    "uvicorn[standard]>=0.29",
]
```

Do not add npm dependencies or a frontend build tool.

## Open Decisions

1. Exact import/export file-picker behavior in browser:
   - Decision: default to the current user's `Documents\EVE\Overview`.
   - Remember changed folder.
   - Browser security limits direct local path access, so use server-side path fields plus browser upload controls where useful.

2. Deploy-to-`Documents\EVE\Overview`:
   - Should be explicit and confirmed.
   - Must not overwrite existing files; generate a unique filename.

3. Character name resolution in GUI:
   - Default on.
   - Toggle available in Profiles.
   - Use local cache.
   - Clearly label that public ESI is used only for name lookup.

4. SDE group names:
   - Local SDE/group metadata should be included with the app where practical.
   - If bundled metadata is missing or stale, fall back to numeric group IDs and let the user load/update local SDE data.

5. Auto-save:
   - Decision: keep one in-memory document initially.
   - Add periodic local draft save only after core workflows are stable.
