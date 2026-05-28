"""Appearance CRUD route."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from eve_overview_manager.gui import state

router = APIRouter()


class AppearanceUpdate(BaseModel):
    stateColors: dict | None = None
    stateBlinks: dict | None = None
    flagOrder: list | None = None
    flagStates: list | None = None
    backgroundOrder: list | None = None
    backgroundStates: list | None = None


@router.get("/document/appearance")
def get_appearance():
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    return JSONResponse({"appearance": doc.get("appearance", {})})


@router.patch("/document/appearance")
def update_appearance(update: AppearanceUpdate):
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    app = doc.setdefault("appearance", {})
    if update.stateColors is not None:
        app["stateColors"] = update.stateColors
    if update.stateBlinks is not None:
        app["stateBlinks"] = update.stateBlinks
    if update.flagOrder is not None:
        app["flagOrder"] = update.flagOrder
    if update.flagStates is not None:
        app["flagStates"] = update.flagStates
    if update.backgroundOrder is not None:
        app["backgroundOrder"] = update.backgroundOrder
    if update.backgroundStates is not None:
        app["backgroundStates"] = update.backgroundStates
    return JSONResponse({"appearance": app})
