"""Columns CRUD route."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from eve_overview_manager.gui import state

router = APIRouter()


class ColumnsUpdate(BaseModel):
    columnOrder: list[str] | None = None
    enabled: list[str] | None = None


@router.get("/document/columns")
def get_columns():
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    return JSONResponse({"columns": doc.get("columns", {})})


@router.patch("/document/columns")
def update_columns(update: ColumnsUpdate):
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    cols = doc.setdefault("columns", {})
    if update.columnOrder is not None:
        cols["columnOrder"] = update.columnOrder
    if update.enabled is not None:
        cols["enabled"] = update.enabled
    return JSONResponse({"columns": cols})
