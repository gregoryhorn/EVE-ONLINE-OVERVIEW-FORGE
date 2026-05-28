from fastapi.testclient import TestClient

from eve_overview_manager.gui import state
from eve_overview_manager.gui.server import _build_app
from eve_overview_manager.yaml_io.parser import load_overview_yaml


def test_gui_preset_patch_accepts_numeric_groups_and_updates_document():
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), None)
    client = TestClient(_build_app())

    response = client.patch("/api/document/presets/PRIMARY", json={"groups": [25, 26]})

    assert response.status_code == 200
    preset = next(p for p in state.get_document()["presets"] if p["id"] == "PRIMARY")
    assert preset["groups"] == [25, 26]


def test_gui_presets_route_returns_tab_usage_context():
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), None)
    client = TestClient(_build_app())

    response = client.get("/api/document/presets")

    assert response.status_code == 200
    assert response.json()["presets"]
    assert response.json()["tabs"]


def test_gui_new_standard_template_loads_bundled_overview():
    client = TestClient(_build_app())

    response = client.post("/api/document/new", json={"template": "standard"})

    assert response.status_code == 200
    document = response.json()["document"]
    assert document["meta"]["sourceFormat"] == "template"
    assert document["meta"]["sourcePath"] == "standard_complete_overview.yaml"
    assert [tab["label"] for tab in document["tabs"]][:4] == ["General", "PvP", "Fleet", "Warp To"]
    assert len(document["presets"]) >= 12
    assert state.get_document()["tabs"] == document["tabs"]


def test_gui_appearance_patch_uses_eve_style_blink_keys():
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), None)
    client = TestClient(_build_app())

    response = client.patch(
        "/api/document/appearance",
        json={
            "flagStates": [44],
            "flagOrder": [44],
            "backgroundStates": [44],
            "backgroundOrder": [44],
            "stateBlinks": {"background_44": True},
            "stateColors": {"flag_44": "red", "background_44": "orange"},
        },
    )

    assert response.status_code == 200
    appearance = state.get_document()["appearance"]
    assert appearance["stateBlinks"] == {"background_44": True}
    assert appearance["backgroundOrder"] == [44]


def test_gui_appearance_patch_updates_preview_style_metadata():
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), None)
    client = TestClient(_build_app())

    response = client.patch(
        "/api/document/appearance",
        json={
            "flagStates": [20],
            "flagOrder": [20],
            "backgroundStates": [20],
            "backgroundOrder": [20],
            "stateBlinks": {"flag_20": True, "background_20": True},
                "stateColors": {"flag_20": "turquoise", "background_20": "purple"},
        },
    )
    preview_response = client.get("/api/preview")

    assert response.status_code == 200
    appearance = preview_response.json()["preview"]["rows"][0]["appearance"]
    assert appearance["flagColor"] == "#00a8a8"
    assert appearance["backgroundColor"] == "#5a148c"
    assert appearance["flagBlink"] is True
    assert appearance["backgroundBlink"] is True


def test_preview_render_splits_flag_and_background_blink_classes():
    from pathlib import Path

    app_js = Path("src/eve_overview_manager/gui/static/app.js").read_text(encoding="utf-8")
    app_css = Path("src/eve_overview_manager/gui/static/app.css").read_text(encoding="utf-8")

    assert "row-blink-bg" in app_js
    assert "row-blink-fg" in app_js
    assert "classes.push('row-blink')" not in app_js
    assert "row-background-blink-flash" in app_css
    assert "row-flag-blink-flash" in app_css


def test_gui_tabs_add_uses_document_tab_cap():
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), None)
    client = TestClient(_build_app())

    response = client.post("/api/document/tabs", json={"label": "NEW"})

    assert response.status_code == 200
    assert len(response.json()["tabs"]) == 10


def test_gui_columns_patch_updates_preview_columns():
    state.set_document(load_overview_yaml("Examples/Real-Overview.yaml").model_dump(), None)
    client = TestClient(_build_app())

    response = client.patch(
        "/api/document/columns",
        json={"columnOrder": ["NAME", "TYPE", "ICON", "DISTANCE"], "enabled": ["NAME", "TYPE"]},
    )
    preview_response = client.get("/api/preview")

    assert response.status_code == 200
    assert response.json()["columns"]["enabled"] == ["NAME", "TYPE"]
    assert [column["id"] for column in preview_response.json()["preview"]["columns"]] == ["NAME", "TYPE"]
