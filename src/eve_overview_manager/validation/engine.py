"""Structured overview validation."""

from __future__ import annotations

import re

from eve_overview_manager.models.overview import OverviewDocument
from eve_overview_manager.models.validation import ValidationResult
from eve_overview_manager.validation import rules
from eve_overview_manager.validation.columns import KNOWN_COLUMNS
from eve_overview_manager.validation.group_validator import GroupValidator, NoopGroupValidator
from eve_overview_manager.validation.state_dictionary import KNOWN_STATE_IDS

ARGB_RE = re.compile(r"^[0-9A-Fa-f]{8}$")
STATE_BLINK_KEY_RE = re.compile(r"^(background|flag)_\d+$")
STATE_BLINK_KEY_WITH_ID_RE = re.compile(r"^(?:background|flag)_(\d+)$")
BUILTIN_PRESET_REFS = {"_BracketFilterShowAll"}
DEFAULT_PRESET_RE = re.compile(r"^DefaultPreset_\d+$")


def validate_overview(document: OverviewDocument, group_validator: GroupValidator | None = None) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    group_validator = group_validator or NoopGroupValidator()
    tab_limit = 5 if document.meta.compatibilityMode == "legacy" else document.meta.clientTabCap
    tab_rule = rules.TAB_LIMIT_LEGACY if document.meta.compatibilityMode == "legacy" else rules.TAB_LIMIT_CURRENT
    if len(document.tabs) > tab_limit:
        results.append(
            ValidationResult(
                code=tab_rule,
                severity="error",
                message=f"Active tabs must be <= {tab_limit}.",
                path="tabs",
                suggestedFix="Remove extra tab bindings or change compatibility mode.",
            )
        )

    seen_slots: set[int] = set()
    seen_presets: set[str] = set()
    preset_ids = {preset.id for preset in document.presets}

    for index, tab in enumerate(document.tabs):
        if tab.slot in seen_slots:
            results.append(
                ValidationResult(
                    code=rules.TAB_SLOT_UNIQUE,
                    severity="error",
                    message=f"Duplicate tab slot {tab.slot}.",
                    path=f"tabs[{index}].slot",
                    suggestedFix="Assign each tab a unique slot.",
                )
            )
        seen_slots.add(tab.slot)
        if tab.colorARGB is not None and not ARGB_RE.match(tab.colorARGB):
            results.append(
                ValidationResult(
                    code=rules.COLOR_FORMAT,
                    severity="error",
                    message="Tab color must be an 8-digit ARGB hex value.",
                    path=f"tabs[{index}].colorARGB",
                    suggestedFix="Use a value like FFFF4444.",
                )
            )
        for field_name, preset_ref in (("overviewPresetRef", tab.overviewPresetRef), ("bracketPresetRef", tab.bracketPresetRef)):
            if (
                preset_ref
                and preset_ref not in preset_ids
                and preset_ref not in BUILTIN_PRESET_REFS
                and not DEFAULT_PRESET_RE.match(preset_ref)
            ):
                results.append(
                    ValidationResult(
                        code=rules.PRESET_REF_EXISTS,
                        severity="error",
                        message=f"Preset reference {preset_ref!r} does not exist.",
                        path=f"tabs[{index}].{field_name}",
                        suggestedFix="Create the preset or update the tab reference.",
                    )
                )

    for index, preset in enumerate(document.presets):
        if preset.id in seen_presets:
            results.append(
                ValidationResult(
                    code=rules.PRESET_ID_UNIQUE,
                    severity="error",
                    message=f"Duplicate preset id {preset.id!r}.",
                    path=f"presets[{index}].id",
                    suggestedFix="Rename or merge duplicate presets.",
                )
            )
        seen_presets.add(preset.id)
        for group_index, group_id in enumerate(preset.groups):
            if not isinstance(group_id, int):
                results.append(
                    ValidationResult(
                        code=rules.GROUP_ID_INTEGER,
                        severity="error",
                        message="Group IDs must be integers.",
                        path=f"presets[{index}].groups[{group_index}]",
                    )
                )
                continue
            if not group_validator.is_known_group_id(group_id):
                results.append(
                    ValidationResult(
                        code=rules.GROUP_ID_KNOWN,
                        severity="warning",
                        message=f"Group ID {group_id} is not known to the configured group validator.",
                        path=f"presets[{index}].groups[{group_index}]",
                        suggestedFix="Check the group ID or refresh the local SDE data.",
                    )
                )
        for state_field in ("alwaysShownStates", "filteredStates"):
            for state_index, state_id in enumerate(getattr(preset, state_field)):
                if not isinstance(state_id, int):
                    results.append(
                        ValidationResult(
                            code=rules.STATE_ID_INTEGER,
                            severity="error",
                            message="State IDs must be integers.",
                            path=f"presets[{index}].{state_field}[{state_index}]",
                        )
                    )
                    continue
                if state_id not in KNOWN_STATE_IDS:
                    results.append(
                        ValidationResult(
                            code=rules.STATE_ID_KNOWN,
                            severity="warning",
                            message=f"State ID {state_id} is not in the known state dictionary.",
                            path=f"presets[{index}].{state_field}[{state_index}]",
                            suggestedFix="Verify the state ID and update the state dictionary if it is valid.",
                        )
                    )
        overlap = set(preset.alwaysShownStates).intersection(set(preset.filteredStates))
        if overlap:
            results.append(
                ValidationResult(
                    code=rules.STATE_INTERSECTION_WARN,
                    severity="warning",
                    message="A state appears in both always-shown and filtered lists.",
                    path=f"presets[{index}]",
                    suggestedFix="Keep each state in only one state list.",
                )
            )

    missing_columns = [column for column in document.columns.enabled if column not in document.columns.columnOrder]
    if missing_columns:
        results.append(
            ValidationResult(
                code=rules.COLUMN_SUBSET,
                severity="error",
                message="Enabled columns must exist in column order.",
                path="columns.enabled",
                suggestedFix=f"Add missing columns to columnOrder: {', '.join(missing_columns)}",
            )
        )
    unknown_columns = [
        column
        for column in [*document.columns.columnOrder, *document.columns.enabled]
        if column not in KNOWN_COLUMNS
    ]
    if unknown_columns:
        results.append(
            ValidationResult(
                code=rules.COLUMN_KNOWN,
                severity="warning",
                message="Some columns are not in the known overview column dictionary.",
                path="columns",
                suggestedFix=f"Review unknown columns: {', '.join(sorted(set(unknown_columns)))}",
            )
        )

    invalid_blink_keys = [key for key in document.appearance.stateBlinks if not STATE_BLINK_KEY_RE.match(key)]
    if invalid_blink_keys:
        results.append(
            ValidationResult(
                code=rules.STATE_BLINK_KEY_FORMAT,
                severity="warning",
                message="State blink keys should use background_<stateId> or flag_<stateId>.",
                path="appearance.stateBlinks",
                suggestedFix=f"Review invalid blink keys: {', '.join(invalid_blink_keys)}",
            )
        )

    for field_name in ("flagOrder", "flagStates", "backgroundOrder", "backgroundStates"):
        for state_index, state_id in enumerate(getattr(document.appearance, field_name)):
            if not isinstance(state_id, int):
                results.append(
                    ValidationResult(
                        code=rules.STATE_ORDER_INTEGER,
                        severity="error",
                        message="Appearance state IDs must be integers.",
                        path=f"appearance.{field_name}[{state_index}]",
                    )
                )
                continue
            if state_id not in KNOWN_STATE_IDS:
                results.append(
                    ValidationResult(
                        code=rules.STATE_ID_KNOWN,
                        severity="warning",
                        message=f"State ID {state_id} is not in the known state dictionary.",
                        path=f"appearance.{field_name}[{state_index}]",
                        suggestedFix="Verify the state ID and update the state dictionary if it is valid.",
                    )
                )

    for key in document.appearance.stateBlinks:
        match = STATE_BLINK_KEY_WITH_ID_RE.match(key)
        if match and int(match.group(1)) not in KNOWN_STATE_IDS:
            results.append(
                ValidationResult(
                    code=rules.STATE_ID_KNOWN,
                    severity="warning",
                    message=f"State ID {match.group(1)} is not in the known state dictionary.",
                    path=f"appearance.stateBlinks.{key}",
                    suggestedFix="Verify the state ID and update the state dictionary if it is valid.",
                )
            )

    return results
