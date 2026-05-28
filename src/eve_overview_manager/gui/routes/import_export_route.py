"""Import/export route helpers for the GUI."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from eve_overview_manager.gui import state
from eve_overview_manager.models.overview import OverviewDocument
from eve_overview_manager.services.filenames import unique_output_path

router = APIRouter()


class ExportRequest(BaseModel):
    path: str


class GenerateRequest(BaseModel):
    specPath: str
    outputPath: str
    outputFormat: str = "yaml"


@router.post("/export/yaml")
def export_yaml(request: ExportRequest):
    document = _current_document()
    output_path = unique_output_path(Path(request.path))
    from eve_overview_manager.yaml_io.exporter import export_overview_yaml

    export_overview_yaml(document, output_path)
    return JSONResponse({"status": "ok", "outputPath": str(output_path), "format": "yaml"})


@router.post("/export/json")
def export_json(request: ExportRequest):
    document = _current_document()
    output_path = unique_output_path(Path(request.path))
    from eve_overview_manager.json_io.exporter import export_overview_json

    export_overview_json(document, output_path)
    return JSONResponse({"status": "ok", "outputPath": str(output_path), "format": "json"})


@router.post("/export/preview")
def preview_export(request: ExportRequest):
    _current_document()
    requested_path = Path(request.path)
    output_path = unique_output_path(requested_path)
    return JSONResponse(
        {
            "requestedPath": str(requested_path),
            "outputPath": str(output_path),
            "wouldRename": output_path != requested_path,
        }
    )


@router.post("/import/generator")
def import_generator(request: GenerateRequest):
    spec_path = Path(request.specPath)
    if not spec_path.exists():
        raise HTTPException(status_code=404, detail=f"Generator spec not found: {spec_path}")
    output_path = unique_output_path(Path(request.outputPath))
    from eve_overview_manager.generator.builder import build_overview_document, load_generator_spec
    from eve_overview_manager.json_io.exporter import export_overview_json
    from eve_overview_manager.yaml_io.exporter import export_overview_yaml

    document = build_overview_document(load_generator_spec(spec_path))
    if request.outputFormat == "json":
        export_overview_json(document, output_path)
    elif request.outputFormat == "yaml":
        export_overview_yaml(document, output_path)
    else:
        raise HTTPException(status_code=400, detail="outputFormat must be yaml or json")
    state.set_document(document.model_dump(), spec_path)
    return JSONResponse({"status": "ok", "outputPath": str(output_path), "format": request.outputFormat, "document": document.model_dump()})


def _current_document() -> OverviewDocument:
    document = state.get_document()
    if document is None:
        raise HTTPException(status_code=400, detail="No overview document is loaded")
    return OverviewDocument.model_validate(document)
