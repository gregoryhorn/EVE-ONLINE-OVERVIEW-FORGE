"""YAML parser foundation with unknown top-level preservation."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from ruamel.yaml import YAML

from eve_overview_manager.models.overview import (
    AppearanceConfig,
    ColumnsConfig,
    LabelsConfig,
    MiscConfig,
    OverviewDocument,
    Preset,
    TabBinding,
)
from eve_overview_manager.models.validation import ValidationResult

TAB_LABEL_COLOR_RE = re.compile(r"<color=0x([0-9A-Fa-f]{8})>")

KNOWN_TOP_LEVEL_KEYS = {
    "backgroundOrder",
    "backgroundStates",
    "columnOrder",
    "flagOrder",
    "flagStates",
    "overviewColumns",
    "presets",
    "shipLabelOrder",
    "shipLabels",
    "stateBlinks",
    "stateColorsNameList",
    "tabSetup",
    "userSettings",
}


def _warning(code: str, message: str, path: str, suggested_fix: str | None = None) -> ValidationResult:
    return ValidationResult(code=code, severity="warning", message=message, path=path, suggestedFix=suggested_fix)


def _pairs_to_dict(value: Any, *, path: str = "", warnings: list[ValidationResult] | None = None) -> dict[Any, Any]:
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, list):
        result: dict[Any, Any] = {}
        for index, item in enumerate(value):
            if isinstance(item, list) and len(item) == 2:
                result[item[0]] = item[1]
            elif warnings is not None:
                warnings.append(
                    _warning(
                        "YAML_PAIR_ENTRY_INVALID",
                        "Expected pair-list entry shaped as [key, value].",
                        f"{path}[{index}]" if path else f"[{index}]",
                        "Remove malformed entries or convert them to two-item YAML lists.",
                    )
                )
        return result
    if warnings is not None and value is not None:
        warnings.append(
            _warning(
                "YAML_PAIR_LIST_INVALID",
                "Expected a mapping or pair-list.",
                path,
                "Use YAML mapping syntax or a list of [key, value] pairs.",
            )
        )
    return {}


def _pair_key_order(value: Any) -> list[Any]:
    if isinstance(value, dict):
        return list(value.keys())
    if isinstance(value, list):
        return [item[0] for item in value if isinstance(item, list) and len(item) == 2]
    return []


def _rgb_float_list_to_argb(value: Any) -> str | None:
    if not (isinstance(value, list) and len(value) == 3):
        return None
    try:
        red, green, blue = [max(0, min(255, round(float(channel) * 255))) for channel in value]
    except (TypeError, ValueError):
        return None
    return f"FF{red:02X}{green:02X}{blue:02X}"


def _tab_color(fields: dict[Any, Any]) -> str | None:
    color = _rgb_float_list_to_argb(fields.get("color"))
    if color:
        return color
    name = fields.get("name")
    if isinstance(name, str):
        match = TAB_LABEL_COLOR_RE.search(name)
        if match:
            return match.group(1).upper()
    return None


def _parse_presets(raw_presets: Any, warnings: list[ValidationResult]) -> list[Preset]:
    presets: list[Preset] = []
    if raw_presets is None:
        return presets
    if not isinstance(raw_presets, list):
        warnings.append(_warning("YAML_PRESETS_INVALID", "Expected presets to be a list.", "presets"))
        return presets
    for index, raw in enumerate(raw_presets):
        if not (isinstance(raw, list) and len(raw) >= 2):
            warnings.append(
                _warning(
                    "YAML_PRESET_ENTRY_INVALID",
                    "Expected preset entry shaped as [name, pair-list].",
                    f"presets[{index}]",
                )
            )
            continue
        name = str(raw[0])
        fields = _pairs_to_dict(raw[1], path=f"presets[{index}][1]", warnings=warnings)
        presets.append(
            Preset(
                id=name,
                name=name,
                groups=fields.get("groups", []),
                alwaysShownStates=fields.get("alwaysShownStates", []),
                filteredStates=fields.get("filteredStates", []),
                fieldOrder=[str(item[0]) for item in raw[1] if isinstance(item, list) and len(item) == 2],
            )
        )
    return presets


def _parse_tab_setup(raw_tabs: Any, warnings: list[ValidationResult]) -> list[TabBinding]:
    tabs: list[TabBinding] = []
    if raw_tabs is None:
        return tabs
    if not isinstance(raw_tabs, list):
        warnings.append(_warning("YAML_TAB_SETUP_INVALID", "Expected tabSetup to be a list.", "tabSetup"))
        return tabs
    for index, raw in enumerate(raw_tabs):
        if not (isinstance(raw, list) and len(raw) >= 2):
            warnings.append(
                _warning(
                    "YAML_TAB_ENTRY_INVALID",
                    "Expected tab entry shaped as [slot, pair-list].",
                    f"tabSetup[{index}]",
                )
            )
            continue
        try:
            slot = int(raw[0])
        except (TypeError, ValueError):
            warnings.append(
                _warning(
                    "YAML_TAB_SLOT_INVALID",
                    "Expected tab slot to be an integer.",
                    f"tabSetup[{index}][0]",
                )
            )
            continue
        fields = _pairs_to_dict(raw[1], path=f"tabSetup[{index}][1]", warnings=warnings)
        known_fields = {"bracket", "color", "name", "overview"}
        tabs.append(
            TabBinding(
                slot=slot,
                label=str(fields.get("name", "")),
                overviewPresetRef=fields.get("overview"),
                bracketPresetRef=fields.get("bracket"),
                colorARGB=_tab_color(fields),
                unknown={str(key): value for key, value in fields.items() if key not in known_fields},
                fieldOrder=[str(item[0]) for item in raw[1] if isinstance(item, list) and len(item) == 2],
            )
        )
    return tabs


def load_overview_yaml(path: str | Path) -> OverviewDocument:
    yaml = YAML(typ="rt")
    source_path = Path(path)
    with source_path.open("r", encoding="utf-8") as file:
        data = yaml.load(file) or {}
    return _document_from_yaml_data(data, source_path=str(source_path))


def load_overview_yaml_text(text: str, *, source_path: str | None = None) -> OverviewDocument:
    yaml = YAML(typ="rt")
    data = yaml.load(text) or {}
    return _document_from_yaml_data(data, source_path=source_path)


def _document_from_yaml_data(data: Any, *, source_path: str | None = None) -> OverviewDocument:
    warnings: list[ValidationResult] = []
    if not isinstance(data, dict):
        warnings.append(
            _warning(
                "YAML_TOPLEVEL_INVALID",
                "Expected overview YAML top level to be a mapping.",
                "$",
                "Use an EVE overview YAML export with top-level keys.",
            )
        )
        data = {}

    document = OverviewDocument(
        tabs=_parse_tab_setup(data.get("tabSetup"), warnings),
        presets=_parse_presets(data.get("presets"), warnings),
        appearance=AppearanceConfig(
            flagOrder=data.get("flagOrder", []),
            flagStates=data.get("flagStates", []),
            backgroundOrder=data.get("backgroundOrder", []),
            backgroundStates=data.get("backgroundStates", []),
            stateBlinks=_pairs_to_dict(data.get("stateBlinks", {}), path="stateBlinks", warnings=warnings),
            stateColors=_pairs_to_dict(data.get("stateColorsNameList", {}), path="stateColorsNameList", warnings=warnings),
            stateBlinksOrder=[str(key) for key in _pair_key_order(data.get("stateBlinks", {}))],
            stateColorsOrder=[str(key) for key in _pair_key_order(data.get("stateColorsNameList", {}))],
        ),
        columns=ColumnsConfig(
            columnOrder=data.get("columnOrder", []),
            enabled=data.get("overviewColumns", []),
        ),
        labels=LabelsConfig(
            shipLabelOrder=data.get("shipLabelOrder", []),
            shipLabels=_pairs_to_dict(data.get("shipLabels", {}), path="shipLabels", warnings=warnings),
            shipLabelsOrder=_pair_key_order(data.get("shipLabels", {})),
        ),
        misc=MiscConfig(
            userSettings=_pairs_to_dict(data.get("userSettings", {}), path="userSettings", warnings=warnings),
            userSettingsOrder=[str(key) for key in _pair_key_order(data.get("userSettings", {}))],
        ),
        unknown={str(key): value for key, value in data.items() if key not in KNOWN_TOP_LEVEL_KEYS},
    )
    document.meta.sourcePath = source_path
    document.meta.topLevelKeyOrder = [str(key) for key in data.keys()]
    document.meta.importWarnings = warnings
    return document
