"""Presets CRUD route."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from eve_overview_manager.gui import state

router = APIRouter()


class PresetCreate(BaseModel):
    name: str = "New Preset"


class PresetUpdate(BaseModel):
    name: str | None = None
    groups: list | None = None
    alwaysShownStates: list | None = None
    filteredStates: list | None = None


@router.get("/document/presets")
def get_presets():
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    return JSONResponse({"presets": doc.get("presets", []), "tabs": doc.get("tabs", [])})


@router.post("/document/presets")
def add_preset(create: PresetCreate):
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    presets = doc.setdefault("presets", [])
    new_id = "preset-" + uuid.uuid4().hex[:8]
    new_preset = {
        "id": new_id,
        "name": create.name,
        "groups": [],
        "alwaysShownStates": [],
        "filteredStates": [],
    }
    presets.append(new_preset)
    return JSONResponse({"presets": presets, "newId": new_id})


@router.patch("/document/presets/{preset_id}")
def update_preset(preset_id: str, update: PresetUpdate):
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    presets = doc.get("presets", [])
    preset = next((p for p in presets if p.get("id") == preset_id), None)
    if preset is None:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_id}' not found")
    if update.name is not None:
        preset["name"] = update.name
    if update.groups is not None:
        preset["groups"] = update.groups
    if update.alwaysShownStates is not None:
        preset["alwaysShownStates"] = update.alwaysShownStates
    if update.filteredStates is not None:
        preset["filteredStates"] = update.filteredStates
    return JSONResponse({"presets": presets})


@router.delete("/document/presets/{preset_id}")
def delete_preset(preset_id: str):
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    before = len(doc.get("presets", []))
    doc["presets"] = [p for p in doc.get("presets", []) if p.get("id") != preset_id]
    if len(doc["presets"]) == before:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_id}' not found")
    return JSONResponse({"presets": doc["presets"]})


@router.post("/document/presets/{preset_id}/duplicate")
def duplicate_preset(preset_id: str):
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    presets = doc.setdefault("presets", [])
    src = next((p for p in presets if p.get("id") == preset_id), None)
    if src is None:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_id}' not found")
    new_id = "preset-" + uuid.uuid4().hex[:8]
    new_preset = {**src, "id": new_id, "name": src.get("name", "Preset") + " (copy)"}
    presets.append(new_preset)
    return JSONResponse({"presets": presets, "newId": new_id})
