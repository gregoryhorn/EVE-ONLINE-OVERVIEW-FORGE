from fastapi.testclient import TestClient

from eve_overview_manager.gui import state
from eve_overview_manager.gui.server import _build_app
from eve_overview_manager.yaml_io.parser import load_overview_yaml


def test_gui_preview_route_uses_loaded_document():
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), None)
    client = TestClient(_build_app())

    response = client.get("/api/preview")

    assert response.status_code == 200
    preview = response.json()["preview"]
    assert preview["activeTab"]["label"] == "NORMAL"
    assert preview["activePreset"]["name"] == "PRIMARY"
    assert [column["id"] for column in preview["columns"]] == [
        "ICON",
        "DISTANCE",
        "NAME",
        "TYPE",
        "ALLIANCE",
        "VELOCITY",
    ]


def test_gui_preview_route_accepts_bracket_mode():
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), None)
    client = TestClient(_build_app())

    response = client.get("/api/preview?mode=brackets")

    assert response.status_code == 200
    assert response.json()["preview"]["mode"] == "brackets"


def test_gui_preview_route_uses_configured_group_names(monkeypatch, tmp_path):
    group_names = tmp_path / "group_names.json"
    group_names.write_text('{"1657": "SDE Citadel"}', encoding="utf-8")
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), None)
    from eve_overview_manager.gui.routes import preview_route

    monkeypatch.setattr(
        preview_route,
        "load_gui_preferences",
        lambda: preview_route.GuiPreferences(importExportFolder=str(tmp_path), groupNamesPath=str(group_names)),
    )
    client = TestClient(_build_app())

    response = client.get("/api/preview")

    assert response.status_code == 200
    assert response.json()["preview"]["rows"][0]["groupName"] == "SDE Citadel"


def test_gui_preview_route_can_preview_specific_preset():
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), None)
    client = TestClient(_build_app())

    response = client.get("/api/preview?preset_id=PRIMARY")

    assert response.status_code == 200
    preview = response.json()["preview"]
    assert preview["activePreset"]["id"] == "PRIMARY"


def test_gui_preview_route_can_return_debug_diagnostics():
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), None)
    client = TestClient(_build_app())

    response = client.get("/api/preview?preset_id=PRIMARY&debug=true")

    assert response.status_code == 200
    diagnostics = response.json()["diagnostics"]
    assert diagnostics["requested"]["presetId"] == "PRIMARY"
    assert diagnostics["activePreset"]["id"] == "PRIMARY"
    assert diagnostics["rowCount"] == len(response.json()["preview"]["rows"])
    assert diagnostics["fingerprint"]
    assert diagnostics["firstRows"]


def test_gui_preview_self_test_reports_tab_and_preset_cases():
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), None)
    client = TestClient(_build_app())

    response = client.get("/api/preview/self-test")

    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["tabCount"] > 0
    assert data["summary"]["presetPreviewCount"] > 0
    assert data["summary"]["distinctPresetFingerprints"] > 0
    assert data["summary"]["coverage"] is True
    assert data["tabs"][0]["requested"]["kind"] == "tab"
    assert data["presets"][0]["requested"]["kind"] == "preset"
    assert data["presets"][0]["fingerprint"]


def test_gui_preview_route_uses_curated_mode_by_default_and_coverage_on_request():
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), None)
    client = TestClient(_build_app())

    curated = client.get("/api/preview?preset_id=PRIMARY&debug=true")
    coverage = client.get("/api/preview?preset_id=PRIMARY&coverage=true&debug=true")

    assert curated.status_code == 200
    assert coverage.status_code == 200
    assert curated.json()["diagnostics"]["coverage"] is False
    assert coverage.json()["diagnostics"]["coverage"] is True
    assert coverage.json()["diagnostics"]["rowCount"] >= curated.json()["diagnostics"]["rowCount"]
