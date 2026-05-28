from pathlib import Path

from fastapi.testclient import TestClient

from eve_overview_manager.gui.routes import preferences_route
from eve_overview_manager.gui.server import _build_app


def test_gui_preferences_routes_load_and_update_preferences(monkeypatch, tmp_path):
    stored = preferences_route.GuiPreferences(importExportFolder=str(tmp_path / "Overview"))
    monkeypatch.setattr(preferences_route, "load_gui_preferences", lambda: stored)
    monkeypatch.setattr(preferences_route, "save_gui_preferences", lambda preferences: preferences)
    client = TestClient(_build_app())

    get_response = client.get("/api/preferences")
    patch_response = client.patch(
        "/api/preferences",
        json={"importExportFolder": str(tmp_path / "Changed"), "groupNamesPath": str(tmp_path / "group_names.json")},
    )

    assert get_response.status_code == 200
    assert get_response.json()["preferences"]["importExportFolder"] == str(tmp_path / "Overview")
    assert patch_response.status_code == 200
    assert patch_response.json()["preferences"]["importExportFolder"] == str(tmp_path / "Changed")
    assert patch_response.json()["preferences"]["groupNamesPath"] == str(tmp_path / "group_names.json")


def test_gui_unique_output_path_route_never_returns_existing_path(tmp_path):
    output = tmp_path / "overview.yaml"
    output.write_text("existing", encoding="utf-8")
    client = TestClient(_build_app())

    response = client.post("/api/paths/unique-output", json={"path": str(output)})

    assert response.status_code == 200
    assert response.json()["requestedPath"] == str(output)
    assert response.json()["outputPath"] == str(tmp_path / "overview_2.yaml")
    assert response.json()["wouldOverwrite"] is True
