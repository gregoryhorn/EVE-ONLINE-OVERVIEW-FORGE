"""GUI preferences and safe path helper routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from eve_overview_manager.services.filenames import unique_output_path
from eve_overview_manager.services.preferences import (
    GuiPreferences,
    load_gui_preferences,
    save_gui_preferences,
)

router = APIRouter()


class PreferencesUpdate(BaseModel):
    importExportFolder: str | None = None
    groupNamesPath: str | None = None


class UniquePathRequest(BaseModel):
    path: str


@router.get("/preferences")
def get_preferences():
    preferences = load_gui_preferences()
    return JSONResponse({"preferences": preferences.model_dump()})


@router.patch("/preferences")
def update_preferences(update: PreferencesUpdate):
    preferences = load_gui_preferences()
    if update.importExportFolder is not None:
        if not update.importExportFolder:
            raise HTTPException(status_code=400, detail="importExportFolder cannot be empty")
        preferences.importExportFolder = str(Path(update.importExportFolder))
    if "groupNamesPath" in update.model_fields_set:
        preferences.groupNamesPath = str(Path(update.groupNamesPath)) if update.groupNamesPath else None
    preferences = save_gui_preferences(preferences)
    return JSONResponse({"preferences": preferences.model_dump()})


@router.post("/paths/unique-output")
def get_unique_output_path(request: UniquePathRequest):
    if not request.path:
        raise HTTPException(status_code=400, detail="path is required")
    output_path = unique_output_path(Path(request.path))
    return JSONResponse({"requestedPath": request.path, "outputPath": str(output_path), "wouldOverwrite": output_path != Path(request.path)})
