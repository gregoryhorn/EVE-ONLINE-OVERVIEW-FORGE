"""Live overview preview route."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from eve_overview_manager.gui import state
from eve_overview_manager.models.overview import OverviewDocument
from eve_overview_manager.preview import build_preview
from eve_overview_manager.services.preferences import GuiPreferences, load_gui_preferences
from eve_overview_manager.validation.sde import load_group_names

router = APIRouter()


@router.get("/preview")
def get_preview(
    slot: int | None = Query(default=None),
    mode: str = "overview",
    preset_id: str | None = Query(default=None),
    debug: bool = Query(default=False),
    coverage: bool = Query(default=False),
):
    doc_dict = state.get_document()
    if doc_dict is None:
        preview = build_preview(OverviewDocument(), active_slot=slot, mode=mode, preset_id=preset_id, coverage=coverage)
        return JSONResponse(_preview_response(preview, slot=slot, mode=mode, preset_id=preset_id, debug=debug, coverage=coverage))
    try:
        document = OverviewDocument.model_validate(doc_dict)
        preview = build_preview(
            document,
            active_slot=slot,
            mode=mode,
            group_names=_configured_group_names(),
            preset_id=preset_id,
            coverage=coverage,
        )
        return JSONResponse(_preview_response(preview, slot=slot, mode=mode, preset_id=preset_id, debug=debug, coverage=coverage))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/preview/self-test")
def get_preview_self_test(limit: int = Query(default=100, ge=1, le=500), coverage: bool = Query(default=True)):
    doc_dict = state.get_document()
    if doc_dict is None:
        raise HTTPException(status_code=400, detail="No overview document is loaded.")
    try:
        document = OverviewDocument.model_validate(doc_dict)
        group_names = _configured_group_names()
        tab_cases = [
            _preview_diagnostics(
                build_preview(document, active_slot=tab.slot, mode="overview", group_names=group_names, coverage=coverage),
                requested={"kind": "tab", "slot": tab.slot, "presetId": tab.overviewPresetRef, "coverage": coverage},
            )
            for tab in sorted(document.tabs, key=lambda item: item.slot)
        ]
        preset_cases = [
            _preview_diagnostics(
                build_preview(document, mode="overview", group_names=group_names, preset_id=preset.id, coverage=coverage),
                requested={"kind": "preset", "presetId": preset.id, "presetName": preset.name, "coverage": coverage},
            )
            for preset in document.presets[:limit]
        ]
        fingerprints = {case["fingerprint"] for case in preset_cases}
        return JSONResponse(
            {
                "summary": {
                    "tabCount": len(document.tabs),
                    "presetCount": len(document.presets),
                    "presetPreviewCount": len(preset_cases),
                    "coverage": coverage,
                    "distinctPresetFingerprints": len(fingerprints),
                    "zeroRowPresetIds": [
                        case["activePreset"]["id"]
                        for case in preset_cases
                        if case["activePreset"].get("id") and case["rowCount"] == 0
                    ],
                },
                "tabs": tab_cases,
                "presets": preset_cases,
            }
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _configured_group_names() -> dict[int, str]:
    preferences = load_gui_preferences()
    if not preferences.groupNamesPath:
        return {}
    path = Path(preferences.groupNamesPath)
    if not path.exists():
        return {}
    return load_group_names(path)


def _preview_response(
    preview: dict[str, Any],
    *,
    slot: int | None,
    mode: str,
    preset_id: str | None,
    debug: bool,
    coverage: bool,
) -> dict[str, Any]:
    response: dict[str, Any] = {"preview": preview}
    if debug:
        response["diagnostics"] = _preview_diagnostics(
            preview,
            requested={"kind": "single", "slot": slot, "mode": mode, "presetId": preset_id, "coverage": coverage},
        )
    return response


def _preview_diagnostics(preview: dict[str, Any], *, requested: dict[str, Any]) -> dict[str, Any]:
    rows = preview.get("rows") or []
    columns = preview.get("columns") or []
    active_tab = preview.get("activeTab") or {}
    active_preset = preview.get("activePreset") or {}
    return {
        "requested": requested,
        "mode": preview.get("mode"),
        "coverage": preview.get("coverage"),
        "activeTab": {
            "slot": active_tab.get("slot"),
            "label": active_tab.get("label"),
            "overviewPresetRef": active_tab.get("overviewPresetRef"),
            "bracketPresetRef": active_tab.get("bracketPresetRef"),
        },
        "activePreset": {
            "id": active_preset.get("id"),
            "name": active_preset.get("name"),
        },
        "rowCount": len(rows),
        "totalSampleRows": preview.get("totalSampleRows"),
        "columnIds": [column.get("id") for column in columns],
        "fingerprint": _preview_fingerprint(rows),
        "groupIds": _sorted_row_values(rows, "groupId"),
        "groupNames": _sorted_row_values(rows, "groupName"),
        "stateIds": sorted({state_id for row in rows for state_id in row.get("stateIds", [])}),
        "firstRows": [_diagnostic_row(row) for row in rows[:12]],
        "warnings": preview.get("warnings") or [],
    }


def _diagnostic_row(row: dict[str, Any]) -> dict[str, Any]:
    cells = row.get("cells") or {}
    return {
        "name": cells.get("NAME"),
        "type": cells.get("TYPE"),
        "distance": cells.get("DISTANCE"),
        "groupId": row.get("groupId"),
        "groupName": row.get("groupName"),
        "stateIds": row.get("stateIds") or [],
        "icon": cells.get("ICON"),
    }


def _preview_fingerprint(rows: list[dict[str, Any]]) -> str:
    payload = [
        {
            "groupId": row.get("groupId"),
            "stateIds": row.get("stateIds") or [],
            "name": (row.get("cells") or {}).get("NAME"),
            "type": (row.get("cells") or {}).get("TYPE"),
        }
        for row in rows
    ]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def _sorted_row_values(rows: list[dict[str, Any]], key: str) -> list[Any]:
    values = {row.get(key) for row in rows if row.get(key) is not None}
    return sorted(values, key=lambda item: str(item))
