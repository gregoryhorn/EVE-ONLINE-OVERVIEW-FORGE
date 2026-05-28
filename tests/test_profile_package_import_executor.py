from eve_overview_manager.profiles.backup import create_backup_from_clone_plan
from eve_overview_manager.profiles.package_exporter import export_profile_package
from eve_overview_manager.profiles.package_import_executor import execute_profile_package_import
from eve_overview_manager.profiles.package_import_planner import plan_profile_package_import
from eve_overview_manager.profiles.scanner import scan_profile


def test_execute_profile_package_import_applies_verified_package_with_backup(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    backup_root = tmp_path / "backups"
    source.mkdir()
    target.mkdir()
    (source / "core_char_100.dat").write_bytes(b"source-char")
    target_file = target / "core_char_100.dat"
    target_file.write_bytes(b"target-char")
    package = tmp_path / "profile.zip"
    export_profile_package(scan_profile(source), package)
    plan = plan_profile_package_import(package, scan_profile(target))
    backup = create_backup_from_clone_plan(plan, backup_root)

    audit = execute_profile_package_import(plan, backup)

    assert target_file.read_bytes() == b"source-char"
    assert audit.operationId == plan.operationId
    assert audit.auditManifestPath == str(backup_root / backup.timestamp / "package_import_execution_manifest.json")
    assert audit.actionsApplied[0].sha256Before
    assert audit.actionsApplied[0].bytesCopied == len(b"source-char")


def test_execute_profile_package_import_rejects_missing_backup_coverage(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    backup_root = tmp_path / "backups"
    source.mkdir()
    target.mkdir()
    (source / "core_char_100.dat").write_bytes(b"source-char")
    target_file = target / "core_char_100.dat"
    target_file.write_bytes(b"target-char")
    package = tmp_path / "profile.zip"
    export_profile_package(scan_profile(source), package)
    plan = plan_profile_package_import(package, scan_profile(target))
    backup = create_backup_from_clone_plan(plan.model_copy(update={"actions": []}), backup_root)

    try:
        execute_profile_package_import(plan, backup)
    except ValueError as error:
        assert "Backup manifest does not cover planned target files" in str(error)
    else:
        raise AssertionError("execute_profile_package_import should require backup coverage.")


def test_execute_profile_package_import_rejects_mismatched_package_path(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    backup_root = tmp_path / "backups"
    source.mkdir()
    target.mkdir()
    (source / "core_char_100.dat").write_bytes(b"source-char")
    (target / "core_char_100.dat").write_bytes(b"target-char")
    package = tmp_path / "profile.zip"
    other_package = tmp_path / "other.zip"
    export_profile_package(scan_profile(source), package)
    export_profile_package(scan_profile(source), other_package)
    plan = plan_profile_package_import(package, scan_profile(target))
    backup = create_backup_from_clone_plan(plan, backup_root)

    try:
        execute_profile_package_import(plan, backup, package_path=other_package)
    except ValueError as error:
        assert "different package" in str(error)
    else:
        raise AssertionError("execute_profile_package_import should reject mismatched package paths.")
