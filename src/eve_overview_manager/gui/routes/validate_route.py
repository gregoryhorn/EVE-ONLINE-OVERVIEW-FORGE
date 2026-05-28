"""Validation route."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from eve_overview_manager.gui import state

router = APIRouter()


@router.post("/validate")
def validate():
    doc_dict = state.get_document()
    if doc_dict is None:
        raise HTTPException(status_code=400, detail="No document loaded.")
    try:
        from eve_overview_manager.models.overview import OverviewDocument
        from eve_overview_manager.validation.engine import validate_overview
        doc_obj = OverviewDocument.model_validate(doc_dict)
        results = [r.model_dump() for r in validate_overview(doc_obj)]
        errors = sum(1 for r in results if r["severity"] == "error")
        warnings = sum(1 for r in results if r["severity"] == "warning")
        return JSONResponse({"results": results, "errorCount": errors, "warningCount": warnings})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
