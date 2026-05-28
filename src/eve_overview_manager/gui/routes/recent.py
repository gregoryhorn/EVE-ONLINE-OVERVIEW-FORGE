"""Recent files route."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from eve_overview_manager.gui import state

router = APIRouter()


@router.get("/recent-files")
def recent_files():
    return JSONResponse({"recentFiles": state.get_recent_files()})
