"""Snapshot routes for the GUI."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from eve_overview_manager.gui import state
from eve_overview_manager.models.overview import OverviewDocument
from eve_overview_manager.services.snapshots import create_overview_snapshot, list_snapshots

router = APIRouter()


class SnapshotCreateRequest(BaseModel):
    snapshotRoot: str
    operationType: str = "gui-snapshot"
    notes: str | None = None


@router.post("/snapshots/create")
def create_snapshot(request: SnapshotCreateRequest):
    if not request.snapshotRoot:
        raise HTTPException(status_code=400, detail="snapshotRoot is required")
    document = state.get_document()
    if document is None:
        raise HTTPException(status_code=400, detail="No overview document is loaded")
    manifest = create_overview_snapshot(
        OverviewDocument.model_validate(document),
        Path(request.snapshotRoot),
        operation_type=request.operationType,
        source_path=state.get_current_path(),
        notes=request.notes,
    )
    return JSONResponse({"status": "ok", "snapshot": manifest.model_dump()})


@router.get("/snapshots")
def get_snapshots(snapshotRoot: str):
    if not snapshotRoot:
        raise HTTPException(status_code=400, detail="snapshotRoot is required")
    snapshots = [snapshot.model_dump() for snapshot in list_snapshots(Path(snapshotRoot))]
    return JSONResponse({"snapshotRoot": snapshotRoot, "snapshots": snapshots})
