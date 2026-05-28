"""Document load/save/new routes."""

from __future__ import annotations

from pathlib import Path
from importlib.resources import files

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from eve_overview_manager.gui import state
from eve_overview_manager.yaml_io.parser import load_overview_yaml

router = APIRouter()


class LoadRequest(BaseModel):
    path: str


class LoadContentRequest(BaseModel):
    filename: str
    content: str


class NewRequest(BaseModel):
    template: str = "blank"


@router.get("/document")
def get_document():
    doc = state.get_document()
    if doc is None:
        return JSONResponse({"document": None, "path": None})
    return JSONResponse({"document": doc, "path": str(state.get_current_path() or "")})


@router.post("/document/load")
def load_document(req: LoadRequest):
    path = Path(req.path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    try:
        if path.suffix.lower() in {".yaml", ".yml"}:
            from eve_overview_manager.yaml_io.parser import load_overview_yaml
            doc_obj = load_overview_yaml(path)
            doc = doc_obj.model_dump()
        else:
            doc = __import__("json").loads(path.read_text(encoding="utf-8"))
        state.set_document(doc, path)
        return JSONResponse({"status": "ok", "path": str(path), "document": doc})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/document/load-content")
def load_document_content(req: LoadContentRequest):
    filename = req.filename or "uploaded-overview.yaml"
    try:
        if filename.lower().endswith((".yaml", ".yml")):
            from eve_overview_manager.yaml_io.parser import load_overview_yaml_text

            doc_obj = load_overview_yaml_text(req.content, source_path=filename)
            doc = doc_obj.model_dump()
        elif filename.lower().endswith(".json"):
            doc = __import__("json").loads(req.content)
        else:
            raise HTTPException(status_code=400, detail="Only .yaml, .yml, and .json files are supported.")
        state.set_document(doc, None)
        return JSONResponse({"status": "ok", "path": filename, "document": doc})
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/document/new")
def new_document(req: NewRequest):
    doc = _template(req.template)
    state.set_document(doc, None)
    return JSONResponse({"status": "ok", "document": doc})


def _template(name: str) -> dict:
    normalized_name = name.strip().lower().replace("_", "-")
    if normalized_name in {"standard", "standard-complete", "standard-tabs"}:
        path = _standard_template_path()
        if path is None:
            raise HTTPException(status_code=500, detail="Standard overview template is not available.")
        doc = load_overview_yaml(path).model_dump()
        doc["meta"]["sourceFormat"] = "template"
        doc["meta"]["sourcePath"] = path.name
        return doc

    base = {
        "schemaVersion": "codex-overview/v1",
        "meta": {"sourceFormat": "new", "clientTabCap": 20, "compatibilityMode": "current"},
        "tabs": [],
        "presets": [],
        "appearance": {
            "flagOrder": [], "flagStates": [],
            "backgroundOrder": [], "backgroundStates": [],
            "stateBlinks": {}, "stateColors": {},
        },
        "columns": {"columnOrder": ["TAG", "ICON", "DISTANCE", "NAME", "TYPE"], "enabled": ["ICON", "DISTANCE", "NAME", "TYPE"]},
        "labels": {"shipLabelOrder": [], "shipLabels": {}},
        "misc": {"userSettings": {}},
        "unknown": {},
    }
    if name == "pvp":
        base["tabs"] = [{"slot": 1, "label": "PVP", "colorARGB": "FFFF4444", "overviewPresetRef": "pvp-main", "bracketPresetRef": ""}]
        base["presets"] = [{"id": "pvp-main", "name": "PVP Main", "groups": [], "alwaysShownStates": [], "filteredStates": []}]
    elif name == "mining":
        base["tabs"] = [{"slot": 1, "label": "Mining", "colorARGB": "FF44FF88", "overviewPresetRef": "mining-main", "bracketPresetRef": ""}]
        base["presets"] = [{"id": "mining-main", "name": "Mining Main", "groups": [], "alwaysShownStates": [], "filteredStates": []}]
    return base


def _standard_template_path() -> Path | None:
    packaged = files("eve_overview_manager").joinpath("templates", "standard_complete_overview.yaml")
    if packaged.is_file():
        return Path(str(packaged))
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "Examples" / "standard_complete_overview.yaml"
        if candidate.exists():
            return candidate
    return None
