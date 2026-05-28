from eve_overview_manager.models.profile import CharacterProfileFile
from eve_overview_manager.profiles.package_exporter import export_profile_package
from eve_overview_manager.profiles.package_import_planner import plan_profile_package_import
from eve_overview_manager.profiles.scanner import scan_profile


def test_package_import_planner_maps_matching_character_ids(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "core_char_100.dat").write_bytes(b"source-char")
    target_file = target / "core_char_100.dat"
    target_file.write_bytes(b"target-char")
    package = tmp_path / "profile.zip"
    export_profile_package(scan_profile(source), package)

    plan = plan_profile_package_import(package, scan_profile(target))

    assert plan.blocked is False
    assert plan.summary.dryRun is True
    assert plan.summary.requiresBackup is True
    assert len(plan.actions) == 1
    assert plan.actions[0].targetFile == str(target_file)
    assert target_file.read_bytes() == b"target-char"


def test_package_import_planner_includes_source_and_destination_character_names(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "core_char_100.dat").write_bytes(b"source-char")
    (target / "core_char_100.dat").write_bytes(b"target-char")
    package = tmp_path / "profile.zip"
    source_profile = scan_profile(source)
    source_profile.characterFiles = [CharacterProfileFile(path=str(source / "core_char_100.dat"), characterId=100, characterName="Mizz Betty")]
    target_profile = scan_profile(target)
    target_profile.characterFiles = [CharacterProfileFile(path=str(target / "core_char_100.dat"), characterId=100, characterName="Mizz Betty")]
    export_profile_package(source_profile, package)

    plan = plan_profile_package_import(package, target_profile)

    assert plan.actions[0].sourceName == "Mizz Betty"
    assert plan.actions[0].targetName == "Mizz Betty"


def test_package_import_planner_blocks_missing_character_id(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "core_char_100.dat").write_bytes(b"source-char")
    (target / "core_char_200.dat").write_bytes(b"target-char")
    package = tmp_path / "profile.zip"
    export_profile_package(scan_profile(source), package)

    plan = plan_profile_package_import(package, scan_profile(target))

    assert plan.blocked is True
    assert plan.actions == []
    assert "100" in plan.summary.missingTargetIds


def test_package_import_planner_blocks_missing_account_id(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "core_user_1.dat").write_bytes(b"source-user")
    (target / "core_user_2.dat").write_bytes(b"target-user")
    package = tmp_path / "profile.zip"
    export_profile_package(scan_profile(source), package, include_core_user=True, include_core_char=False)

    plan = plan_profile_package_import(package, scan_profile(target))

    assert plan.blocked is True
    assert plan.actions == []
    assert "1" in plan.summary.missingTargetIds
