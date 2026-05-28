"""Tabs CRUD route."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from eve_overview_manager.gui import state

router = APIRouter()


class TabUpdate(BaseModel):
    slot: int
    label: str | None = None
    colorARGB: str | None = None
    overviewPresetRef: str | None = None
    bracketPresetRef: str | None = None


class TabCreate(BaseModel):
    label: str = "New Tab"
    colorARGB: str = "FF00C8F0"
    overviewPresetRef: str = ""
    bracketPresetRef: str = ""


@router.get("/document/tabs")
def get_tabs():
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    return JSONResponse({"tabs": doc.get("tabs", []), "presets": doc.get("presets", [])})


@router.patch("/document/tabs/{slot}")
def update_tab(slot: int, update: TabUpdate):
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    tabs = doc.setdefault("tabs", [])
    tab = next((t for t in tabs if t.get("slot") == slot), None)
    if tab is None:
        raise HTTPException(status_code=404, detail=f"Tab slot {slot} not found")
    if update.label is not None:
        tab["label"] = update.label
    if update.colorARGB is not None:
        tab["colorARGB"] = update.colorARGB
    if update.overviewPresetRef is not None:
        tab["overviewPresetRef"] = update.overviewPresetRef
    if update.bracketPresetRef is not None:
        tab["bracketPresetRef"] = update.bracketPresetRef
    return JSONResponse({"tabs": tabs})


@router.post("/document/tabs")
def add_tab(create: TabCreate):
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    tabs = doc.setdefault("tabs", [])
    tab_cap = int(doc.get("meta", {}).get("clientTabCap", 20))
    if len(tabs) >= tab_cap:
        raise HTTPException(status_code=400, detail=f"Maximum {tab_cap} tabs reached")
    next_slot = max((t.get("slot", 0) for t in tabs), default=0) + 1
    new_tab: dict[str, Any] = {
        "slot": next_slot,
        "label": create.label,
        "colorARGB": create.colorARGB,
        "overviewPresetRef": create.overviewPresetRef,
        "bracketPresetRef": create.bracketPresetRef,
    }
    tabs.append(new_tab)
    return JSONResponse({"tabs": tabs, "newSlot": next_slot})


@router.delete("/document/tabs/{slot}")
def delete_tab(slot: int):
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    tabs = doc.setdefault("tabs", [])
    before = len(tabs)
    doc["tabs"] = [t for t in tabs if t.get("slot") != slot]
    if len(doc["tabs"]) == before:
        raise HTTPException(status_code=404, detail=f"Tab slot {slot} not found")
    return JSONResponse({"tabs": doc["tabs"]})


@router.post("/document/tabs/{slot}/duplicate")
def duplicate_tab(slot: int):
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    tabs = doc.setdefault("tabs", [])
    tab_cap = int(doc.get("meta", {}).get("clientTabCap", 20))
    if len(tabs) >= tab_cap:
        raise HTTPException(status_code=400, detail=f"Maximum {tab_cap} tabs reached")
    src = next((t for t in tabs if t.get("slot") == slot), None)
    if src is None:
        raise HTTPException(status_code=404, detail=f"Tab slot {slot} not found")
    next_slot = max((t.get("slot", 0) for t in tabs), default=0) + 1
    new_tab = {**src, "slot": next_slot, "label": src.get("label", "Tab") + " (copy)"}
    tabs.append(new_tab)
    return JSONResponse({"tabs": tabs, "newSlot": next_slot})


@router.post("/document/tabs/reorder")
def reorder_tabs(body: dict):
    """Accepts {order: [slot, slot, ...]} and reassigns slots 1..N."""
    doc = state.get_document()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document loaded")
    order: list[int] = body.get("order", [])
    tabs = {t.get("slot"): t for t in doc.get("tabs", [])}
    reordered = []
    for new_slot, old_slot in enumerate(order, start=1):
        tab = tabs.get(old_slot)
        if tab:
            reordered.append({**tab, "slot": new_slot})
    doc["tabs"] = reordered
    return JSONResponse({"tabs": reordered})
