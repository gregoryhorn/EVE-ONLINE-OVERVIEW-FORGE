from pathlib import Path
import json


def test_presets_group_catalog_includes_drones_and_fighters():
    catalog_js = Path("src/eve_overview_manager/gui/static/screens/presets.js").read_text(encoding="utf-8")

    expected_labels = [
        "Combat Drone",
        "Mining Drone",
        "Electronic Warfare Drone",
        "Logistic Drone",
        "Stasis Webifying Drone",
        "Energy Neutralizer Drone",
        "Salvage Drone",
        "Light Fighter",
        "Heavy Fighter",
        "Support Fighter",
        "Fighter Bomber",
    ]

    for label in expected_labels:
        assert f"label: '{label}'" in catalog_js
    assert "cat: 'Drones & Fighters'" in catalog_js


def test_standard_group_catalog_is_source_controlled_and_broad():
    catalog = json.loads(Path("src/eve_overview_manager/gui/static/data/group_catalog.json").read_text(encoding="utf-8"))
    labels = {group["label"] for group in catalog["groups"]}
    categories = {group["cat"] for group in catalog["groups"]}

    assert catalog["schemaVersion"] == "overview-group-catalog/v1"
    assert catalog["groupCount"] >= 600
    assert len(catalog["groups"]) == catalog["groupCount"]
    assert {"Ships", "Drones & Fighters", "NPCs", "Structures", "Deployables", "Celestials"} <= categories
    assert {"Combat Drone", "Citadel", "Encounter Surveillance System", "Abyssal Filaments"} <= labels


def test_dashboard_exposes_standard_overview_template():
    dashboard_js = Path("src/eve_overview_manager/gui/static/screens/dashboard.js").read_text(encoding="utf-8")

    assert 'data-template="standard"' in dashboard_js
    assert "Standard" in dashboard_js


def test_profiles_screen_exposes_package_modes_and_preflight_table():
    profiles_js = Path("src/eve_overview_manager/gui/static/screens/profiles.js").read_text(encoding="utf-8")

    assert 'data-profile-mode-tab="same-pc"' in profiles_js
    assert 'data-profile-mode-tab="other-pc"' in profiles_js
    assert 'data-profile-mode-tab="snapshots"' in profiles_js
    assert "profile-preflight-table" in profiles_js
    assert "/profiles/package/plan-import" in profiles_js
    assert "/profiles/snapshots/save" in profiles_js
    assert "/profiles/snapshots/list" in profiles_js
    assert "Package Source" in profiles_js
    assert "action.sourceName" in profiles_js
    assert "action.targetName" in profiles_js
    assert "Profile Tools" in profiles_js
    assert "Execute Package Import" in profiles_js
    assert "Execute Restore" in profiles_js
