from pathlib import Path

from fastapi.testclient import TestClient

from eve_overview_manager.gui import state
from eve_overview_manager.gui.server import _build_app
from eve_overview_manager.yaml_io.parser import load_overview_yaml


def test_gui_export_yaml_uses_unique_output_path(tmp_path):
    output = tmp_path / "overview.yaml"
    output.write_text("existing", encoding="utf-8")
    state.set_document(load_overview_yaml("Examples/sample_overview.yaml").model_dump(), None)
    client = TestClient(_build_app())

    response = client.post("/api/export/yaml", json={"path": str(output)})

    assert response.status_code == 200
    assert response.json()["outputPath"] == str(tmp_path / "overview_2.yaml")
    assert (tmp_path / "overview_2.yaml").exists()


def test_gui_export_preview_reports_unique_output_path(tmp_path):
    output = tmp_path / "overview.yaml"
    output.write_text("existing", encoding="utf-8")
    state.set_document(load_overview_yaml("Examples/sample_overview.yaml").model_dump(), None)
    client = TestClient(_build_app())

    response = client.post("/api/export/preview", json={"path": str(output)})

    assert response.status_code == 200
    assert response.json()["requestedPath"] == str(output)
    assert response.json()["outputPath"] == str(tmp_path / "overview_2.yaml")
    assert response.json()["wouldRename"] is True


def test_gui_export_json_requires_loaded_document(tmp_path):
    state.set_document(None, None)
    client = TestClient(_build_app())

    response = client.post("/api/export/json", json={"path": str(tmp_path / "overview.json")})

    assert response.status_code == 400
    assert response.json()["detail"] == "No overview document is loaded"


def test_gui_import_generator_exports_and_sets_current_document(tmp_path):
    output = tmp_path / "generated.yaml"
    client = TestClient(_build_app())

    response = client.post(
        "/api/import/generator",
        json={"specPath": "Examples/sample_generator.json", "outputPath": str(output), "outputFormat": "yaml"},
    )

    assert response.status_code == 200
    assert response.json()["outputPath"] == str(output)
    assert output.exists()
    assert state.get_document()["meta"]["sourceFormat"] == "codex-generator"


def test_gui_document_load_content_accepts_browser_selected_yaml():
    client = TestClient(_build_app())
    content = Path("Examples/Real-Overview.yaml").read_text(encoding="utf-8")

    response = client.post("/api/document/load-content", json={"filename": "browser.yaml", "content": content})

    assert response.status_code == 200
    assert response.json()["path"] == "browser.yaml"
    assert response.json()["document"]["tabs"][0]["label"]
