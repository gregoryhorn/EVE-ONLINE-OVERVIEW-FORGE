from pathlib import Path

from fastapi.testclient import TestClient

from eve_overview_manager.gui import state
from eve_overview_manager.gui.server import _build_app
from eve_overview_manager.yaml_io.parser import load_overview_yaml


def test_gui_create_snapshot_writes_manifest(tmp_path):
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), Path("Examples/Real-Overview.yaml"))
    client = TestClient(_build_app())

    response = client.post("/api/snapshots/create", json={"snapshotRoot": str(tmp_path), "notes": "gui test"})

    assert response.status_code == 200
    snapshot = response.json()["snapshot"]
    assert snapshot["notes"] == "gui test"
    assert Path(snapshot["documentPath"]).exists()
    assert Path(snapshot["manifestPath"]).exists()


def test_gui_list_snapshots_returns_created_snapshot(tmp_path):
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), None)
    client = TestClient(_build_app())
    client.post("/api/snapshots/create", json={"snapshotRoot": str(tmp_path)})

    response = client.get("/api/snapshots", params={"snapshotRoot": str(tmp_path)})

    assert response.status_code == 200
    assert len(response.json()["snapshots"]) == 1


def test_gui_create_snapshot_requires_document(tmp_path):
    state.set_document(None, None)
    client = TestClient(_build_app())

    response = client.post("/api/snapshots/create", json={"snapshotRoot": str(tmp_path)})

    assert response.status_code == 400
