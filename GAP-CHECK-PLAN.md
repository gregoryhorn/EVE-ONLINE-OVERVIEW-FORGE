# Gap Check And Remediation Plan

This plan captures what the current app must prove before more GUI work. It is based on the local research report plus the reviewed public overview tools, wikis, and community packs.

## Reviewed References

- EVE Overview Generator by Evan Sosenko: modular source files generate final importable YAML. Important concepts: reusable groups, states, presets, tab layouts, appearance, columns, labels, and settings.
- EVE University overview manipulation guide: practical in-game workflow and the user mental model for tabs, overview presets, bracket presets, types, states, columns, labels, and appearance.
- AIE overview settings guide: player-facing setup guidance and pack usage expectations.
- overview-eve.online: browser-based overview editor pattern; useful as UI reference, not a core dependency.
- iridiumops/overview: modern generated overview YAML releases, including 12-tab layouts.
- Balestrino/eve-overview: generator-derived Dharma pack with downloadable final YAML releases.
- Arziel1992/Z-S-Overview-Pack: modular Z-S source plus generated overview samples already used as fixtures.

## Added Sample Coverage

The app now includes representative importable YAML samples in `Examples/community-overviews/` from:

- Z-S Overview Pack
- EVE University unstylized pack variant from Z-S releases
- Jason/general public gist
- Iridium v3.9.0
- EVE Overview Generator v2.5.0
- Dharma/Balestrino 1.3

These are fixtures for parser, validator, preview, and GUI behavior. They are not endorsed defaults.

`Examples/standard_complete_overview.yaml` is the maintained first-party starter. The Dashboard exposes it as the Standard new-overview template so the app can create a practical tab/preset layout without requiring a manual file import.

## Remediation Plans

### 0. Workflow / Information Architecture

Status: Complete.

Problem:
The GUI exposes YAML sections as separate screens, but the EVE workflow starts from a tab, then the tab's overview preset, then global presentation settings.

Target behavior:
- Tabs is the main editor hub.
- Selecting a tab establishes the active overview preset, bracket preset, preview context, and quick links to edit the bound preset.
- Types & States and Brackets are moved to Advanced unless they gain a concrete user workflow.

Implementation steps:
1. Update the left navigation order to Dashboard, Tabs, Presets, Columns, Appearance, Import / Export, Profiles, Advanced.
2. Add an Advanced section that contains Types & States and Brackets.
3. Rework Tabs screen layout around selected tab details:
   - tab label
   - tab color
   - overview preset assignment
   - bracket preset assignment
   - direct action to edit assigned overview preset
   - direct action to inspect/change assigned bracket preset
4. Preserve existing routes where practical; do not remove backend APIs unless no longer referenced.
5. Update docs/screenshots checklist after the UI flow changes.

Likely files:
- `src/eve_overview_manager/gui/static/app.js`
- `src/eve_overview_manager/gui/static/index.html`
- `src/eve_overview_manager/gui/static/app.css`
- `src/eve_overview_manager/gui/static/screens/tabs.js`
- `src/eve_overview_manager/gui/static/screens/presets.js`
- `GUI-PLAN.md`

Tests:
- Add/update GUI route tests if navigation state is backend-visible.
- Add JS/browser smoke test later: import sample, select tab, jump to bound preset.
- Run `python -m pytest` after route changes.

Acceptance criteria:
- A user can load a community sample and understand each tab's assigned overview/bracket presets from the Tabs screen.
- The primary nav no longer suggests Types & States or Brackets are normal first-step editing workflows.
- The live preview follows the selected tab's overview preset.

Completion notes:
- Primary nav now follows Dashboard, Tabs, Presets, Columns, Appearance, Import / Export, Profiles, Advanced.
- Types & States and Brackets are reachable from Advanced instead of primary navigation.
- Tabs now shows overview and bracket preset assignments with direct actions to open the assigned preset editor.
- Bracket helper text now states that bracket presets do not drive the overview table preview.

### 1. Imported Preset Editing

Status: Complete for current GUI scope. Keep under regression as more community samples are added.

Problem:
The Presets page must show selected imported groups. If selected groups are invisible because they are not in the local checkbox catalog, the user cannot trust or edit the preset.

Target behavior:
- The selected preset's `groups` list is faithfully represented.
- Known groups render as checked named rows.
- Unknown groups render as selected numeric rows, not silently hidden.
- Toggling a group mutates the active preset and refreshes validation/preview.
- The Presets screen preview is driven by the selected preset, not by the active tab.
- The Presets screen preview does not show the tab strip; tabs assign presets, but preset editing should focus on the preset itself.
- The Presets screen shows which tabs currently use the selected preset so the assignment relationship is visible without making tabs the preview driver.

Implementation steps:
1. Inspect how `load_overview_yaml` maps YAML preset groups into `Preset.groups`.
2. Inspect the Presets screen group catalog and identify which sample groups are missing.
3. Build the group list as `known groups union selected preset groups`, sorted/grouped predictably.
4. Keep numeric IDs visible beside names.
5. On toggle, send the full updated group ID list to the backend.
6. Ensure preset edits update the canonical in-memory document.
7. Refresh preview and validation after save.
8. Add a preset-preview mode or route parameter that previews a specific preset ID directly.
9. Hide the preview tab strip on the Presets screen and label the preview as "Preset Preview".
10. Show "Used by tabs" metadata for the selected preset.

Likely files:
- `src/eve_overview_manager/gui/static/screens/presets.js`
- `src/eve_overview_manager/gui/routes/editor_routes.py`
- `src/eve_overview_manager/gui/state.py`
- `src/eve_overview_manager/preview/engine.py`
- `src/eve_overview_manager/gui/routes/preview_route.py`
- `src/eve_overview_manager/gui/static/app.js`
- `tests/test_gui_editor_routes.py`
- `tests/test_gui_preview_route.py`
- `tests/test_preview_engine.py`

Tests:
- Load `iridium-v390-main.yaml`, select several presets, assert selected groups are returned by API.
- Unit test unknown selected group IDs remain visible in preset payloads.
- Route test: update preset groups, then preview changes for matching sample entities.
- Preview route test: passing a preset ID previews that preset without requiring tab selection.
- Browser check: Presets screen preview has no tab strip and changes when a different preset is selected.

Acceptance criteria:
- No imported selected group disappears from the Presets page.
- Toggling one group changes the document and preview without a page reload.
- Export/re-import keeps the edited group list.
- Selecting different presets changes the preset preview directly.
- The preview area on Presets does not imply that the selected tab controls the preset preview.

Completion notes:
- Done: Presets route now returns tab context for usage display.
- Done: Presets screen shows which tabs use the selected preset.
- Done: Preview route supports direct `preset_id` preview.
- Done: Presets screen sets preview context to the selected preset and hides the tab strip.
- Done: Preview generates a clearly labeled row for selected imported group IDs that are not in the static preview catalog.
- Done: Presets selected-group summary now shows readable labels and hides raw numeric IDs from the main text.
- Done: Presets selected-group summary box was removed; selected imported groups now appear as normal editable checkboxes.
- Done: Preset usage matching now accepts preset ID or name, case-insensitively.
- Done: Preview refresh now ignores stale preview responses so the Presets selected-preset preview is not overwritten by an older tab-preview request.
- Done: unknown imported group IDs are preserved during checkbox edits but are not shown as duplicate generic checkboxes.
- Verified by focused GUI/preview tests and full regression during the GUI correctness pass.

### 2. State Filter Semantics

Status: Mostly complete. Remaining work is browser QA against more imported packs and any edge cases found there.

Problem:
State controls exist, but they must represent EVE's two-list model: always shown states and filtered states. Edits must affect visibility.

Target behavior:
- Each state can be default, always shown, or filtered.
- Always shown can force an entity visible even when type/group filtering would not show it.
- Filtered states hide matching entities unless always-show precedence applies.
- The UI makes the selected state mode obvious.
- The preview catalog contains at least one sample row for every state shown in the State Filters table, otherwise the user cannot confirm that a state filter works.
- State sample rows should be distributed across common entity types so always-show/filter behavior can be seen even when group selection changes.

Implementation steps:
1. Confirm current model fields: `alwaysShownStates` and `filteredStates`.
2. Confirm preview engine precedence and align it with the documented model.
3. Replace ambiguous state toggles with a three-mode control per state.
4. Save full `alwaysShownStates` and `filteredStates` arrays for the active preset.
5. Add sample preview entities covering every state exposed in the Presets State Filters table, including fleet, corp, alliance, standings, suspect, criminal, war target, militia, outlaw, NPC/faction states, and fleet broadcast/scram states where represented.
6. Refresh preview immediately after edits.
7. Add an empty-state message when a state has no matching sample row, but treat that as a temporary test gap rather than acceptable final behavior.

Likely files:
- `src/eve_overview_manager/models/overview.py`
- `src/eve_overview_manager/gui/static/screens/presets.js`
- `src/eve_overview_manager/preview/engine.py`
- `src/eve_overview_manager/validation/state_dictionary.py`
- `tests/test_preview_engine.py`
- `tests/test_validation_rules.py`

Tests:
- Preview hides a row when its state is filtered.
- Preview shows a row when its state is always shown.
- Test that every UI state ID has at least one sample entity in `SAMPLE_ENTITIES`.
- State appearing in both lists still triggers existing warning.
- GUI route saves state mode changes to the canonical document.

Acceptance criteria:
- Changing a state mode visibly changes the preview on presets where sample rows have that state.
- Imported always-shown and filtered states are selected correctly.
- Every state listed in the Presets state table can be demonstrated in the preview.
- Validation remains structured and does not produce tracebacks for malformed state data.

Completion notes:
- Done: Preview catalog includes generated state sample rows covering every visible state filter ID.
- Done: Presets direct-preview mode generates state sample rows against the selected preset's own group, so state filters can be tested without polluting normal tab preview.
- Done: State filter edits now affect preview visibility through the backend preview engine.
- Pending: keep state filter browser checks in the manual regression loop for several community packs.

### 3. Tab Binding Semantics

Status: Complete for current GUI scope.

Problem:
Tabs bind overview and bracket preset references. The GUI must make this explicit and must not get stuck loading preview/sample entities when a tab changes.

Target behavior:
- Selecting a tab is instant.
- The selected tab shows label, slot, color, overview preset ref, and bracket preset ref.
- The preview uses the selected tab's overview preset.
- Changing a tab's overview preset immediately changes preview context.

Implementation steps:
1. Inspect tab state flow from frontend selected tab to `/api/preview`.
2. Normalize tab selection by stable slot or generated frontend key; handle slot `0` correctly.
3. Update tab assignment controls to list existing preset IDs plus recognized built-ins.
4. Save assignment changes through the existing editor route.
5. After save, refresh document summary, active tab details, and preview.
6. Add direct "edit overview preset" navigation carrying the selected preset ID.

Likely files:
- `src/eve_overview_manager/gui/static/screens/tabs.js`
- `src/eve_overview_manager/gui/static/app.js`
- `src/eve_overview_manager/gui/routes/tabs_route.py`
- `src/eve_overview_manager/gui/routes/preview_route.py`
- `tests/test_gui_preview_route.py`
- `tests/test_gui_editor_routes.py`

Tests:
- Route test: selected tab slot returns correct overview/bracket preset refs.
- Preview route test: changing active tab changes active preset.
- GUI route test: updating tab preset assignment persists.

Acceptance criteria:
- Iridium 12-tab samples can be clicked through without loading loops.
- Preview row set changes when selected tabs reference different overview presets.
- Built-in bracket/default refs do not trigger false missing-preset errors.

Completion notes:
- Slot `0` and tabs beyond the old 8-tab assumption are handled.
- Current-mode tab creation uses the document tab cap, which defaults to 20.
- Tabs show overview and bracket preset refs, and preview follows the selected tab's overview preset.

### 4. Bracket Preset Handling

Status: Complete for overview-table scope; true bracket visualization remains deferred.

Problem:
Bracket presets affect in-space brackets, not the overview table. The current Brackets screen can mislead users.

Target behavior:
- Bracket assignment is visible from Tabs.
- Bracket preset editing is either an Advanced workflow or deferred.
- The main live preview remains overview-table focused until bracket preview has a real model.

Implementation steps:
1. Remove Brackets from primary navigation or move it under Advanced.
2. In Tabs, show the selected tab's bracket preset assignment beside overview preset assignment.
3. Allow assignment changes using the same preset list.
4. Clearly avoid using bracket refs to filter the overview table preview.
5. Document bracket preview as deferred unless a proper in-space bracket visualization is built later.

Likely files:
- `src/eve_overview_manager/gui/static/app.js`
- `src/eve_overview_manager/gui/static/screens/tabs.js`
- `src/eve_overview_manager/gui/static/screens/brackets.js`
- `src/eve_overview_manager/preview/engine.py`
- `GUI-PLAN.md`

Tests:
- Route test: bracket preset assignment persists independently of overview preset assignment.
- Preview test: overview preview uses `overviewPresetRef`, not `bracketPresetRef`.

Acceptance criteria:
- The user can see and change bracket preset assignments.
- No screen implies bracket presets control overview table rows.
- Bracket refs remain preserved during import/export.

Completion notes:
- Brackets was moved under Advanced.
- The confusing bracket-mode preview toggle was removed from the main preview.
- Tabs still expose bracket preset assignment so bracket refs remain visible and editable.

### 5. Column Model Accuracy

Status: Complete for current GUI scope. Keep under regression for imported community samples.

Problem:
Columns are global presentation, but the preview and UI must reflect imported `columnOrder` and enabled columns accurately.

Target behavior:
- Imported enabled columns show as enabled.
- Imported column order controls preview header/cell order.
- Toggling a column only changes displayed columns, not row visibility.
- Exported YAML reflects the edited column configuration.

Implementation steps:
1. Confirm parser/exporter maps EVE column keys into `ColumnsConfig.columnOrder` and `ColumnsConfig.enabled`.
2. Build the Columns screen from the document's union of known columns, ordered columns, and enabled columns.
3. Implement deterministic reorder controls if drag/drop is unreliable.
4. Ensure preview route returns columns in the active document order.
5. Add empty/unknown column handling that preserves unknown keys.

Likely files:
- `src/eve_overview_manager/models/overview.py`
- `src/eve_overview_manager/yaml_io/parser.py`
- `src/eve_overview_manager/yaml_io/exporter.py`
- `src/eve_overview_manager/gui/static/screens/columns.js`
- `src/eve_overview_manager/preview/engine.py`
- `tests/test_yaml_roundtrip.py`
- `tests/test_preview_engine.py`

Tests:
- Community sample column counts match expected counts.
- Preview headers follow document order.
- Toggling a column changes preview columns but row count remains stable.
- Roundtrip preserves column config.

Acceptance criteria:
- Samples with 6, 8, 9, and 10 enabled columns render matching preview headers.
- Column edits survive export and re-import.

Completion notes:
- Column checkboxes and order controls autosave.
- Preview headers/cells refresh from the backend after each change.
- Up/down controls supplement drag-and-drop so ordering is testable.

### 6. Appearance Model Accuracy

Problem:
Appearance settings are global state-priority presentation rules. The UI must show imported selections and preview priority effects.

Target behavior:
- Imported flag order, background order, state colors, and blink settings populate the UI.
- Edits update the canonical document.
- Preview row styling resolves from state priority after row visibility is determined.

Implementation steps:
1. Audit parser/exporter coverage for `flagOrder`, `flagStates`, `backgroundOrder`, `backgroundStates`, `stateBlinks`, and `stateColors`.
2. Show known states in priority order and preserve unknown states.
3. Make color editing validate ARGB format before save.
4. Apply background/text/blink metadata from preview output to row rendering.
5. Keep appearance separate from state visibility controls in Presets.

Likely files:
- `src/eve_overview_manager/yaml_io/parser.py`
- `src/eve_overview_manager/yaml_io/exporter.py`
- `src/eve_overview_manager/gui/static/screens/appearance.js`
- `src/eve_overview_manager/preview/engine.py`
- `src/eve_overview_manager/validation/rules.py`
- `tests/test_validation_rules.py`
- `tests/test_preview_engine.py`

Tests:
- Imported sample appearance states appear selected.
- Invalid ARGB is rejected by validation.
- Preview row includes resolved appearance metadata.
- Roundtrip preserves state color/blink lists.

Acceptance criteria:
- Stylized and unstylized samples show meaningful differences.
- Editing a color/background setting changes preview styling without changing visible rows.

Status:
- Done: Appearance screen populates imported color tag, background, color, and blink settings and autosaves edits.
- Done: Preview rows consume resolved flag/background color and blink metadata; blinking flashes enabled styling on/off about twice per second.
- Done: Color selectors are constrained to the 12-color in-game palette visible in the EVE color menu.
- Done: Default tag colors for the known state labels match the in-game Appearance state list.
- Done: Common local state labels were corrected to the exact in-game Appearance state labels from the user's screenshot, including fleet, non-capsuleer corp, capsuleer corp, alliance, standings, war, security status, criminal, suspect, limited engagement, kill right, militia, ally, agent, no-standing, and retribution states. The YAML numeric IDs remain the preserved source of truth.
- Done: Preview blink rendering separates foreground/color-tag blink from background blink so a color-tag blink no longer makes every row pulse.
- Verified: `node --check src\eve_overview_manager\gui\static\app.js`, `node --check src\eve_overview_manager\gui\static\screens\appearance.js`, `node --check src\eve_overview_manager\gui\static\screens\presets.js`, focused GUI/preview tests, full `python -m pytest`, and browser DOM checks for blink class application.

### 7. SDE Group Name Support

Status: Complete for local/offline metadata support; catalog refresh tooling remains a follow-up.

Problem:
Group IDs are hard to edit without names. The app needs local/bundled group metadata, while keeping validation offline by default.

Target behavior:
- Group controls show group names when local metadata is available.
- Numeric IDs remain visible.
- Unknown groups still appear and remain editable.
- Network download is never required for normal editing.

Implementation steps:
1. Use existing SDE group-name index builder as the source for local group metadata.
2. Add a small bundled fallback map for common sample groups if licensing/size is acceptable.
3. Load configured `group_names.json` in GUI preferences.
4. Pass group names to Presets and preview routes.
5. Add clear fallback labels like `Group 1234` for unknown IDs.

Likely files:
- `src/eve_overview_manager/sde/`
- `src/eve_overview_manager/gui/routes/preferences_route.py`
- `src/eve_overview_manager/gui/routes/preview_route.py`
- `src/eve_overview_manager/gui/static/screens/presets.js`
- `tests/test_sde.py`
- `tests/test_gui_preferences_routes.py`

Tests:
- Local group-name file maps IDs to names.
- Missing group-name file does not break GUI routes.
- Unknown selected group IDs remain visible.

Acceptance criteria:
- Preset editor is usable with names for common ships, structures, celestials, drones, NPCs, and deployables.
- Offline mode remains fully functional.

Completion notes:
- `build-group-name-index` can build local `group_names.json` from a CCP SDE archive.
- GUI preferences can point preview metadata at that local file.
- Presets uses a source-controlled standard group catalog generated from community samples and common SDE groups.
- Unknown group IDs still fall back to numeric labels and remain preserved.

### 8. Preview Entity Catalog

Status: Complete for current editing aid scope. Continue expanding only when real samples expose gaps.

Problem:
The preview cannot demonstrate filtering if the sample catalog lacks entities that match real presets.

Target behavior:
- Preview includes enough synthetic entities to exercise common overview types.
- Preview includes enough synthetic state coverage to exercise every visible state filter.
- Rows include group ID, group name, type name, state set, distance, and column values.
- Empty previews explain whether no sample rows matched or the preset is empty.
- Preview context changes by screen:
  - Tabs screen: preview follows selected tab's overview preset and may show the tab strip.
  - Presets screen: preview follows selected preset directly and should not show the tab strip.
  - Columns/Appearance screens: preview follows current tab/preset context because those are global presentation settings.

Implementation steps:
1. Expand the preview catalog with ships, capsules, structures, stargates, stations, planets, suns, moons, belts, anomalies/beacons, drones, fighters, probes, wrecks, containers, deployables, NPCs, and jump bridges.
2. Use group IDs from SDE/community samples where possible.
3. Assign representative states to rows so state filters visibly work.
4. Add preview summaries: active tab, active preset, matching row count, filtered row count.
5. Add preview context support for direct preset preview, separate from tab-driven preview.
6. Keep the catalog local and deterministic.

Likely files:
- `src/eve_overview_manager/preview/engine.py`
- `src/eve_overview_manager/preview/` if catalog is split out
- `src/eve_overview_manager/gui/routes/preview_route.py`
- `src/eve_overview_manager/gui/static/app.js`
- `src/eve_overview_manager/gui/static/screens/presets.js`
- `tests/test_preview_engine.py`
- `tests/test_gui_preview_route.py`

Tests:
- Common preset categories match at least one sample row.
- Every visible state filter ID matches at least one sample row.
- Direct preset preview returns rows for the requested preset independent of tab selection.
- Empty group list behavior is explicit and tested.
- State filter changes alter preview row counts.
- Direct preset state samples use an entity-style group from the selected preset and avoid misleading non-entity combinations such as `Sun with Fleet Member`.

Acceptance criteria:
- Loading community samples produces useful preview rows for common tabs.
- User group/state edits cause visible preview changes.
- Presets screen preview is selected-preset focused and has no tab strip.
- Preview remains clearly labeled as an editing aid, not the EVE client.

Progress notes:
- Corrected hard-coded group ID mismatches exposed by the local SDE group-name map, including Destroyer/Cruiser/Battleship, Citadel/Engineering Complex/Refinery, Upwell Jump Bridge, Upwell Cyno Beacon, Asteroid Belt, Station, and Sovereignty Hub.
- Direct preset state samples now use a ship/NPC-like group from the selected preset when available.
- Preview sample coverage now includes varied state rows for ships, drones, and structures/stations so state filters can be checked against more than player ships.
- Preview catalog explicitly includes Sun, Planet, Moon, Asteroid Belt, Encounter Surveillance System, and Abyssal Filament rows.
- Presets `Ship Groups & Entity Types` includes a fixed `Drones & Fighters` category with common drone and fighter groups.
- Normal preview is curated by default. Exhaustive generated rows for every selected imported group are available only through `coverage=true` or `localStorage.setItem('overviewForgePreviewCoverage', '1')`.
- Presets now loads a source-controlled standard group catalog from `static/data/group_catalog.json` instead of relying only on the small hand-written fallback list. The catalog includes 600+ SDE/community-sample groups and the GUI search field filters it without rebuilding from the currently loaded overview.
- Columns checkbox and order changes now autosave and refresh preview columns; explicit up/down controls supplement drag-and-drop.
- Appearance supports per-state color tag/background color selection, autosaves changes, uses the in-game state labels and 12-color palette, and preview blink animates enabled foreground/background styling separately roughly twice per second.

Follow-up:
- Improve category heuristics and labels in the generated standard catalog as more real overview files are reviewed.
- Add a maintained generator command so refreshing `static/data/group_catalog.json` from a newer SDE/community fixture set is repeatable.

### 9. Roundtrip Preservation

Status: Complete for current community fixture set. Keep as mandatory regression coverage.

Problem:
Community samples must not lose known or unknown data during import/export.

Target behavior:
- Import/export preserves tabs, presets, columns, labels, appearance, misc, unknown top-level keys, and modeled pair-list order.
- Roundtrip tests cover all community samples.

Implementation steps:
1. Add a parameterized test over every `Examples/community-overviews/*.yaml`.
2. Export each sample to a temporary file.
3. Re-import the exported file.
4. Compare summaries: tab count, preset count, enabled columns, known appearance keys, labels, misc, unknown top-level keys.
5. Add targeted checks for tab colors and pair-list order where sample data exists.
6. Fix parser/exporter issues one at a time as tests expose them.

Likely files:
- `src/eve_overview_manager/yaml_io/parser.py`
- `src/eve_overview_manager/yaml_io/exporter.py`
- `src/eve_overview_manager/yaml_io/roundtrip.py`
- `tests/test_yaml_roundtrip.py`
- `tests/test_examples.py`

Tests:
- New community sample roundtrip regression test.
- Existing YAML tests must remain green.

Acceptance criteria:
- All community samples parse, export, reparse, and preserve semantic summaries.
- Unknown data is not silently dropped.

Completion notes:
- Community overview fixtures are included under `Examples/community-overviews/`.
- Existing YAML/example tests cover parser and roundtrip behavior for the current sample set.

### 10. Modular Pack Support

Status: Deferred by design. Final importable YAML remains the supported editing format.

Problem:
Several serious overview projects are modular source systems, not just final YAML files. The current app edits final YAML only.

Target behavior for now:
- Final importable YAML remains the only editable format.
- Modular repos are documented as source references and fixture sources.
- The GUI does not pretend it can edit a generator project unless that feature is explicitly designed.

Future options:
- Read-only modular folder inspector: show parts, presets, groups, tabs, and generated output status.
- Explicit modular compiler: support a small app-owned generator spec, separate from third-party DSLs.
- No modular support: continue focusing on final YAML editing and export.

Implementation steps for current phase:
1. Keep modular-source imports out of the normal YAML import path.
2. Document which sample files are final importable YAML versus generator source.
3. If adding future modular support, create a separate design doc before implementation.
4. Add validation error messaging for users who try to import a partial modular YAML file as a full overview.

Likely files:
- `README.md`
- `GUI-PLAN.md`
- `Examples/community-overviews/README.md`
- `src/eve_overview_manager/yaml_io/parser.py` only if better partial-file diagnostics are needed

Tests:
- Optional parser test for a known partial modular file producing a clear import warning/error.

Acceptance criteria:
- Users understand that Phase 1 edits final EVE overview YAML files.
- Modular project support is not accidentally mixed into normal import/export behavior.

## Recommended Execution Order

1. Implement Gap 11 profile package core models and exporter.
2. Add package inspect/checksum verification.
3. Add package import/restore dry-run planner with same-ID character/account matching and mismatch blocking.
4. Add backup/execute integration for package import/restore, or adapt the existing clone plan executor if the plan shape remains compatible.
5. Add CLI commands for export, inspect, and import/restore planning.
6. Add GUI Profiles modes for `Same PC`, `Other PC`, and `Snapshots`.
7. Run browser QA for the current overview editor flows across the community samples.
8. Polish the full validation panel/status strip if browser QA does not expose higher-priority correctness issues.
9. Add a manual EVE import checklist for exported overview YAML files.

Completed earlier remediation:
- Workflow / information architecture.
- Imported preset editing.
- Tab binding semantics.
- Bracket handling for overview-table scope.
- Column model accuracy.
- Appearance model accuracy.
- SDE group-name support.
- Preview entity catalog.
- Current community-sample roundtrip preservation.
- Modular pack support marked deferred for final-YAML-only scope.

## Test Plan

Use this test plan for every remediation item. A gap is not complete until the relevant automated tests pass and the manual/browser checks have been recorded.

### Test Fixtures

Primary YAML fixtures:
- `Examples/community-overviews/iridium-v390-main.yaml`: modern 12-tab pack; useful for tab-cap, tab switching, and broad preset checks.
- `Examples/community-overviews/iridium-v390-icons.yaml`: tab label/icon variant; useful for tab labels and appearance checks.
- `Examples/community-overviews/overview-generator-default-pvp.yaml`: 8-tab generator output; useful for PvP preset/state checks.
- `Examples/community-overviews/overview-generator-default-pve.yaml`: 8-tab generator output; useful for PvE/NPC/celestial checks.
- `Examples/community-overviews/dharma-default-final.yaml`: 8-tab Dharma/Balestrino layout; useful for compact community pack behavior.
- `Examples/community-overviews/z-s-full-unstylized.yaml`: large Z-S/E-Uni style pack; useful for roundtrip and many-preset behavior.
- `Examples/community-overviews/jason-general-overview.yaml`: smaller general pack; useful for simple smoke checks.

Profile fixtures:
- `Examples/sample_profile_report.json` for GUI profile display.
- Temporary test directories created by pytest for profile clone/backup tests.

### Automated Test Layers

1. **Core model/parser tests**
   - Command: `python -m pytest tests/test_yaml_roundtrip.py tests/test_examples.py`
   - Use when changing parser/exporter/model behavior.
   - Required evidence: all community samples parse without unexpected import warnings; roundtrip summaries remain stable.

2. **Preview engine tests**
   - Command: `python -m pytest tests/test_preview_engine.py`
   - Use when changing tab selection, preset filtering, state semantics, columns, appearance, or preview sample rows.
   - Required evidence: row visibility, column output, active tab/preset metadata, and appearance metadata match expected values.

3. **GUI route tests**
   - Command: `python -m pytest tests/test_gui_editor_routes.py tests/test_gui_preview_route.py tests/test_gui_import_export_routes.py`
   - Use when changing backend GUI APIs or in-memory document mutation.
   - Required evidence: updates persist to the canonical document and preview route reflects the edited state.
   - Preview diagnostics: `/api/preview?debug=true` must report requested slot/preset, resolved active tab/preset, row count, column IDs, group IDs/names, state IDs, first rows, and fingerprint.
   - Preview self-test: `/api/preview/self-test` must report tab-driven and preset-driven cases with row counts and fingerprints so selected-preset changes can be compared programmatically.

4. **Validation tests**
   - Command: `python -m pytest tests/test_validation_rules.py`
   - Use when changing state, preset ref, column, color, or group validation.
   - Required evidence: expected warnings/errors are structured and no expected GUI operation returns a traceback.

5. **Full regression**
   - Command: `python -m pytest`
   - Run before marking any remediation item complete.
   - Required evidence: full suite passes.

### Browser / GUI Smoke Tests

Run these after any frontend behavior change. Use the local GUI and record pass/fail in the final implementation note.

Startup:
1. Start the app with `eve-overview gui`.
2. Open `http://localhost:7477`.
3. Confirm Dashboard loads without console-visible app errors.
4. For preview debugging, enable console logs with `localStorage.setItem('overviewForgePreviewDebug', '1')` and reload.
5. Open `http://localhost:7477/api/preview/self-test` after importing a document and confirm preset cases have fingerprints and nonzero row counts where sample rows match.

Workflow smoke:
1. Import `Examples/community-overviews/iridium-v390-main.yaml`.
2. Open Tabs.
3. Click at least three tabs, including a later tab beyond slot 8.
4. Confirm selected tab details show label, color, overview preset ref, and bracket preset ref.
5. Confirm preview active preset changes with tab selection.
6. Use the selected tab's Edit Overview Preset action.
7. Confirm Presets opens with the bound preset selected.
8. Toggle one group or state, then confirm preview changes.
9. Open Columns, toggle one column, and confirm headers/cells change but row count remains stable.
10. Open Appearance, change one safe visual setting, and confirm preview styling changes.
11. Validate and export to a unique filename.
12. Re-import the exported file and compare summary counts.

Navigation smoke:
1. Confirm primary nav order is Dashboard, Tabs, Presets, Columns, Appearance, Import / Export, Profiles, Advanced.
2. Confirm Types & States and Brackets are not presented as first-step primary workflows.
3. Confirm Advanced contains lower-frequency/reference tools.

Profile smoke:
1. Open Profiles.
2. Confirm the Local Profile Scan field auto-fills the detected default path when available.
3. Scan a temporary or known-safe profile root.
4. Select a source character and destination character.
5. Generate a dry-run overwrite plan.
6. Confirm no files are written during dry-run.
7. Confirm backup is required before execute controls become available.

Future package smoke after Gap 11 implementation:
1. Export a package from a source fixture.
2. Inspect the package and verify checksums.
3. Plan import against a matching destination fixture.
4. Plan import against a missing-character destination fixture and confirm it is blocked.
5. Save a known-good snapshot package and list it from the snapshot library.
6. Plan restore against the same character ID and confirm backup is required before execution.

### Per-Gap Validation Matrix

| Gap | Required automated tests | Required browser/manual checks |
|---|---|---|
| 0. Workflow / Information Architecture | GUI route tests if state/routing changes; full regression | Navigation smoke; Tabs hub workflow smoke |
| 1. Imported Preset Editing | GUI editor route tests; GUI preview route tests; preview engine tests; examples tests | Load Iridium/Z-S/Dharma; selected groups visible; selected preset preview has no tab strip; toggle group changes preview |
| 2. State Filter Semantics | Preview engine tests; validation tests; sample-state coverage test | Toggle always shown/filtered/default and confirm row visibility changes for each visible state |
| 3. Tab Binding Semantics | GUI preview route tests; editor route tests | Click 8-tab and 12-tab samples; active refs and preview update |
| 4. Bracket Preset Handling | Preview engine test proving overview preview uses overview ref; editor route test for bracket assignment | Confirm bracket assignment visible but not shown as overview-row filter |
| 5. Column Model Accuracy | Preview engine tests; YAML roundtrip tests | Toggle/reorder columns; row count stable; export/re-import preserves columns |
| 6. Appearance Model Accuracy | Preview engine tests; validation tests; roundtrip tests | Load stylized/unstylized samples; imported selections visible; style change appears |
| 7. SDE Group Name Support | SDE tests; GUI preference tests; editor route tests | Configure local `group_names.json`; names appear; unknown IDs still visible |
| 8. Preview Entity Catalog | Preview engine tests; GUI preview route tests | Common tabs and selected presets in community samples show meaningful rows or clear empty reason |
| 9. Roundtrip Preservation | Parameterized community roundtrip test; examples test | Export/re-import two representative samples and compare summaries |
| 10. Modular Pack Support | Optional parser diagnostic test | Attempt partial modular YAML import and confirm clear unsupported/partial-file message |
| 11. Profile Packages, Cross-PC Transfer, And Known-Good Restore | Package manifest tests; checksum tests; import/restore-plan mismatch tests; no-write dry-run tests | Export package on source fixture; save known-good snapshot; copy to destination fixture; block missing character/account IDs; require backup before import/restore |

## Gap 11. Profile Packages, Cross-PC Transfer, And Known-Good Restore

Status: Partially complete. Core package export, inspect, checksum verification, dry-run import planning, CLI package-backed execution, Profiles GUI modes, snapshot library foundation, and source/destination name comparison are implemented. Remaining work is visual polish and broader manual QA.

Problem:
- The current profile workflow is same-PC character overwrite inside an already scanned local profile folder.
- A common real workflow is moving profile/layout settings from one PC to another.
- Another real workflow is saving a known-good local character profile and restoring it later after experiments or client/profile drift.
- A raw folder clone is unsafe across machines because the destination PC may not have the same local account/profile files or character files.

Required behavior:
- Add a portable package format instead of asking users to copy loose `core_user_*.dat`, `core_char_*.dat`, or `prefs.ini` files.
- The source PC exports opaque files plus a manifest with schema version, app version, operation ID, timestamp, file type, source ID, size, SHA-256, and resolved character names when available.
- The same package format should support named local known-good snapshots with a user note and snapshot-library location.
- The destination PC scans its local profile folder before import.
- Import planning compares package IDs against destination IDs:
  - `core_char_<id>.dat` can target only the same character ID by default.
  - `core_user_<id>.dat` can target only the same account/profile ID by default.
  - `prefs.ini` can be included only when the user explicitly selects account/profile-scoped settings.
- Import is blocked by default when required character/account IDs are missing or mismatched.
- Import remains dry-run first, requires backup-before-write, never deletes target files, and writes an import audit manifest.
- Restore from a known-good snapshot follows the same rules: verify checksums, scan current local profile, compare IDs, dry-run, backup current files, execute, and write a restore audit manifest.

Likely files:
- `src/eve_overview_manager/profiles/package_exporter.py`
- `src/eve_overview_manager/profiles/package_import_planner.py`
- `src/eve_overview_manager/profiles/package_import_executor.py`
- `src/eve_overview_manager/profiles/profile_snapshot_library.py`
- `src/eve_overview_manager/models/profile.py`
- `src/eve_overview_manager/cli.py`
- `src/eve_overview_manager/gui/routes/profiles_route.py`
- `src/eve_overview_manager/gui/static/screens/profiles.js`
- `tests/test_profile_package_export.py`
- `tests/test_profile_package_import_planner.py`
- `tests/test_profile_package_import_executor.py`
- `tests/test_profile_snapshot_restore.py`

Implementation plan:
1. Done: Define `ProfileTransferManifest` and package file entries in the profile models.
2. Done: Implement package export to a zip file with `manifest.json` and opaque data files under a stable internal folder. Include optional snapshot name and note fields.
3. Done: Implement package inspection with checksum verification.
4. Done: Implement destination import planning that scans the destination profile and maps package files to same-ID destination files.
5. Done: Block missing or mismatched character/account IDs by default.
6. Done: Add a snapshot library helper that lists named local profile packages and verifies them before restore planning.
7. Done: Add a package-specific executor because package plans reference archive entries instead of normal filesystem source files.
8. Done: Add GUI mode switch: `Same PC`, `Other PC`, and `Snapshots`.
9. Done: Add `Other PC` package export/inspect/plan controls and a preflight action table with source/destination IDs and names where available.
10. Done: In `Snapshots`, add `Save Known Good` and `Restore Snapshot` controls with restore planning through the package preflight table.
11. Update README/GUI docs after the behavior is implemented.

Test plan:
- Export package fixture contains manifest and copied opaque files.
- Manifest SHA-256 values match package contents.
- Inspect package fails on checksum mismatch.
- CLI can export, inspect, and plan import from a package.
- Snapshot package stores user name/note and lists from the snapshot library.
- Snapshot restore planning verifies checksums before mapping files.
- Import planner maps same character IDs to destination files.
- Import planner blocks when destination character ID is missing.
- Import planner blocks account-scoped files when destination `core_user` ID is missing.
- Import planner never maps `core_char` to `core_user` or `prefs.ini`.
- Restore planner blocks when current local character/account IDs do not match the snapshot.
- Dry-run import/restore plan does not write files.
- Backup remains required before import/restore execution.
- Package import execution rejects missing backup coverage, mismatched package paths, corrupt packages, and plan/archive metadata mismatches.
- GUI route tests cover package export, inspect, import-plan, and guarded package execution responses.

Acceptance criteria:
- A user can safely export profile settings from PC A, copy one package to PC B, inspect it, see exactly which local destination files would be overwritten, and proceed only after destination IDs match and a backup is created.
- A user can save a named known-good profile snapshot locally, inspect it later, verify its checksums, compare it against the current local profile, and restore only after dry-run and backup.
- The UI clearly warns that EVE must be closed before import execution.
- The UI never implies that account-scoped files belong to a specific character.

### Completion Evidence

For each completed gap, record:
- Changed files.
- Automated commands run.
- Browser/manual checks run.
- Community samples used.
- Known limitations left open.
- Whether docs were updated.

## Manual Acceptance Checklist

Overview editor:
- Load each file in `Examples/community-overviews/`.
- Confirm no import warnings unless expected and documented.
- Select each tab and verify the linked overview preset changes.
- Select several presets and verify group/state controls match imported data.
- Toggle one group, one state, and one column; verify the preview changes.
- Export to a new filename without overwriting an existing file.
- Re-import the exported file and verify tab/preset/column summaries match.

Profiles:
- Open Profiles and confirm the default local EVE settings path is detected when present.
- For profile cloning, keep testing separate from overview YAML editing and use dry-run/backup flows only.
- For future profile packages, confirm package import/restore is blocked when character/account IDs do not match.
