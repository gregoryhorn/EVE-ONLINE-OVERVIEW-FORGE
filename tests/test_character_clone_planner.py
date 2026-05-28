from pathlib import Path

from eve_overview_manager.profiles.clone_planner import plan_character_clone
from eve_overview_manager.profiles.scanner import scan_profile


def test_plan_character_clone_copies_source_character_to_destinations(tmp_path):
    profile = tmp_path / "settings_Default"
    profile.mkdir()
    (profile / "core_char_100.dat").write_text("source", encoding="utf-8")
    (profile / "core_char_200.dat").write_text("target", encoding="utf-8")
    (profile / "core_char_300.dat").write_text("target", encoding="utf-8")

    plan = plan_character_clone(scan_profile(profile), source_character_id=100, target_character_ids=[200, 300])

    assert plan.blocked is False
    assert [Path(action.sourceFile).name for action in plan.actions] == ["core_char_100.dat", "core_char_100.dat"]
    assert [Path(action.targetFile).name for action in plan.actions] == ["core_char_200.dat", "core_char_300.dat"]
    assert all(action.fileType == "core_char" for action in plan.actions)


def test_plan_character_clone_blocks_missing_destination(tmp_path):
    profile = tmp_path / "settings_Default"
    profile.mkdir()
    (profile / "core_char_100.dat").write_text("source", encoding="utf-8")

    plan = plan_character_clone(scan_profile(profile), source_character_id=100, target_character_ids=[200])

    assert plan.blocked is True
    assert plan.summary.missingTargetIds == ["200"]
