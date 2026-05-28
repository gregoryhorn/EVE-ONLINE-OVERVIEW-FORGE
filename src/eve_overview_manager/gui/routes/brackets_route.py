"""Brackets / ship labels CRUD route."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from eve_overview_manager.gui import state

router = APIRouter()


class LabelsUpdate(BaseModel):
    shipLabels: dict | None = None
    shipLabelOrder: list | None = None


@router.get("/document/labels")
def get_labels():
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    return JSONResponse({"labels": doc.get("labels", {})})


@router.patch("/document/labels")
def update_labels(update: LabelsUpdate):
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    lab = doc.setdefault("labels", {})
    if update.shipLabels is not None:
        lab["shipLabels"] = update.shipLabels
    if update.shipLabelOrder is not None:
        lab["shipLabelOrder"] = update.shipLabelOrder
    return JSONResponse({"labels": lab})
