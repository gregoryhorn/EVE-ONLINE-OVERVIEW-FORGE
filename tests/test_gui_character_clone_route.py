from fastapi.testclient import TestClient

from eve_overview_manager.gui.server import _build_app


def test_gui_plan_character_clone_route(tmp_path):
    profile = tmp_path / "settings_Default"
    profile.mkdir()
    (profile / "core_char_100.dat").write_text("source", encoding="utf-8")
    (profile / "core_char_200.dat").write_text("target", encoding="utf-8")
    client = TestClient(_build_app())

    response = client.post(
        "/api/profiles/plan-character-clone",
        json={
            "profilePath": str(profile),
            "sourceCharacterId": 100,
            "targetCharacterIds": [200],
            "resolveNames": False,
        },
    )

    assert response.status_code == 200
    plan = response.json()["plan"]
    assert plan["blocked"] is False
    assert plan["actions"][0]["sourceId"] == "100"
    assert plan["actions"][0]["targetId"] == "200"
