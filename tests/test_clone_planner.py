from pathlib import Path

from eve_overview_manager.profiles.backup import create_backup, create_backup_from_clone_plan, rollback_backup, verify_backup
from eve_overview_manager.profiles.clone_executor import execute_clone
from eve_overview_manager.profiles.clone_planner import CloneOptions, parse_cloneable_file, plan_clone
from eve_overview_manager.profiles.scanner import scan_profile


def test_backup_manifest_includes_sha256_checksums(tmp_path):
    profile = tmp_path / "profile"
    backup_root = tmp_path / "backups"
    profile.mkdir()
    file_path = profile / "prefs.ini"
    file_path.write_text("[prefs]\n", encoding="utf-8")

    manifest = create_backup([file_path], backup_root, source_path=profile, target_path=profile)

    assert len(manifest.fileList[0].sha256) == 64
    assert verify_backup(manifest).ok is True
    assert (backup_root / manifest.timestamp / "backup_manifest.json").exists()
    assert manifest.backupRoot == str(backup_root)
    assert manifest.manifestPath == str(backup_root / manifest.timestamp / "backup_manifest.json")


def test_backup_verification_fails_when_file_changes(tmp_path):
    profile = tmp_path / "profile"
    backup_root = tmp_path / "backups"
    profile.mkdir()
    file_path = profile / "prefs.ini"
    file_path.write_text("[prefs]\n", encoding="utf-8")
    manifest = create_backup([file_path], backup_root, source_path=profile, target_path=profile)

    Path(manifest.fileList[0].backupPath).write_text("changed", encoding="utf-8")

    result = verify_backup(manifest)
    assert result.ok is False
    assert "Checksum mismatch" in result.errors[0]


def test_rollback_backup_restores_original_files_and_writes_audit(tmp_path):
    profile = tmp_path / "profile"
    backup_root = tmp_path / "backups"
    profile.mkdir()
    file_path = profile / "prefs.ini"
    file_path.write_text("original", encoding="utf-8")
    manifest = create_backup([file_path], backup_root, source_path=profile, target_path=profile)
    file_path.write_text("changed", encoding="utf-8")

    audit = rollback_backup(manifest)

    assert file_path.read_text(encoding="utf-8") == "original"
    assert audit.auditManifestPath == str(backup_root / manifest.timestamp / "rollback_manifest.json")
    assert Path(audit.auditManifestPath).exists()
    assert len(audit.actionsApplied) == 1
    entry = audit.actionsApplied[0]
    assert entry.sha256Before is not None
    assert entry.sha256After == entry.backupSha256
    assert entry.bytesRestored == len(b"original")


def test_rollback_backup_rejects_corrupted_backup(tmp_path):
    profile = tmp_path / "profile"
    backup_root = tmp_path / "backups"
    profile.mkdir()
    file_path = profile / "prefs.ini"
    file_path.write_text("original", encoding="utf-8")
    manifest = create_backup([file_path], backup_root, source_path=profile, target_path=profile)
    Path(manifest.fileList[0].backupPath).write_text("corrupt", encoding="utf-8")

    try:
        rollback_backup(manifest)
    except ValueError as error:
        assert "Checksum mismatch" in str(error)
    else:
        raise AssertionError("rollback_backup should reject corrupted backups")


def test_backup_from_clone_plan_copies_unique_target_files(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    backup_root = tmp_path / "backups"
    source.mkdir()
    target.mkdir()
    (source / "core_user_1.dat").write_bytes(b"source")
    (target / "core_user_2.dat").write_bytes(b"target")
    (target / "core_user_3.dat").write_bytes(b"target")
    plan = plan_clone(
        scan_profile(source),
        scan_profile(target),
        CloneOptions(copy_core_user=True, copy_first_to_all=True),
    )
    plan.actions.append(plan.actions[0].model_copy())

    manifest = create_backup_from_clone_plan(plan, backup_root)

    assert manifest.operationType == "clone-plan-backup"
    assert manifest.operationId == plan.operationId
    assert len(manifest.fileList) == 2
    assert {entry.sourcePath for entry in manifest.fileList} == {str(target / "core_user_2.dat"), str(target / "core_user_3.dat")}
    assert verify_backup(manifest).ok is True


def test_clone_planner_creates_dry_run_copy_actions(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "core_user_1.dat").write_bytes(b"source")
    (target / "core_user_1.dat").write_bytes(b"target")

    plan = plan_clone(scan_profile(source), scan_profile(target), CloneOptions(copy_core_user=True))

    assert plan.blocked is False
    assert plan.actions[0].fileType == "core_user"
    assert plan.actions[0].sourceId == "1"
    assert plan.actions[0].targetId == "1"
    assert plan.actions[0].wouldOverwrite is True
    assert plan.summary.sourceFileCount == 1
    assert plan.summary.targetFileCount == 1
    assert plan.summary.plannedActionCount == 1
    assert plan.summary.dryRun is True
    assert plan.summary.requiresBackup is True
    assert Path(plan.actions[0].targetFile).read_bytes() == b"target"


def test_clone_planner_blocks_missing_matching_target_identifier(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "core_user_1.dat").write_bytes(b"source")
    (target / "core_user_2.dat").write_bytes(b"target")

    plan = plan_clone(scan_profile(source), scan_profile(target), CloneOptions(copy_core_user=True))

    assert plan.blocked is True
    assert plan.actions == []
    assert plan.summary.missingSourceIds == ["2"]
    assert "identifier '2'" in plan.warnings[0]


def test_clone_planner_copy_first_to_all_is_explicit(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "core_user_1.dat").write_bytes(b"source")
    (target / "core_user_2.dat").write_bytes(b"target")
    (target / "core_user_3.dat").write_bytes(b"target")

    plan = plan_clone(
        scan_profile(source),
        scan_profile(target),
        CloneOptions(copy_core_user=True, copy_first_to_all=True),
    )

    assert plan.blocked is False
    assert len(plan.actions) == 2
    assert {action.targetId for action in plan.actions} == {"2", "3"}
    assert plan.summary.missingTargetIds == ["1"]


def test_clone_planner_blocks_incompatible_missing_target_type(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "core_char_1.dat").write_bytes(b"source")
    (target / "core_user_2.dat").write_bytes(b"target")

    plan = plan_clone(scan_profile(source), scan_profile(target), CloneOptions(copy_core_char=True))

    assert plan.blocked is True
    assert plan.actions == []
    assert plan.summary.missingTargetIds == ["1"]


def test_clone_planner_warns_for_self_clone_plan(tmp_path):
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "core_user_1.dat").write_bytes(b"user")

    plan = plan_clone(scan_profile(profile), scan_profile(profile), CloneOptions(copy_core_user=True))

    assert plan.blocked is False
    assert "self-clone" in plan.warnings[0]


def test_clone_planner_marks_prefs_risk_low(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "prefs.ini").write_text("[prefs]\n", encoding="utf-8")
    (target / "prefs.ini").write_text("[prefs]\n", encoding="utf-8")

    plan = plan_clone(scan_profile(source), scan_profile(target), CloneOptions(copy_prefs=True))

    assert plan.blocked is False
    assert plan.actions[0].fileType == "prefs"
    assert plan.actions[0].risk == "low"


def test_parse_cloneable_file_warns_for_non_numeric_identifier(tmp_path):
    file_path = tmp_path / "core_char_('char', None, 'dat').dat"
    file_path.write_bytes(b"opaque")

    parsed = parse_cloneable_file(file_path)

    assert parsed is not None
    assert parsed.file_type == "core_char"
    assert parsed.identifier == "('char', None, 'dat')"
    assert "non-numeric" in parsed.parse_warning


def test_parse_cloneable_file_marks_empty_placeholder_identifier(tmp_path):
    file_path = tmp_path / "core_user__.dat"
    file_path.write_bytes(b"opaque")

    parsed = parse_cloneable_file(file_path)

    assert parsed is not None
    assert parsed.identifier == "__empty__"
    assert "empty" in parsed.parse_warning


def test_execute_clone_requires_matching_verified_backup(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    backup_root = tmp_path / "backups"
    source.mkdir()
    target.mkdir()
    (source / "core_user_1.dat").write_bytes(b"source")
    target_file = target / "core_user_1.dat"
    target_file.write_bytes(b"target")
    plan = plan_clone(scan_profile(source), scan_profile(target), CloneOptions(copy_core_user=True))
    manifest = create_backup_from_clone_plan(plan, backup_root)

    audit = execute_clone(plan, manifest)

    assert target_file.read_bytes() == b"source"
    assert audit.operationId == plan.operationId
    assert audit.auditManifestPath == str(backup_root / manifest.timestamp / "execution_manifest.json")
    assert Path(audit.auditManifestPath).exists()
    assert len(audit.actionsApplied) == 1
    entry = audit.actionsApplied[0]
    assert len(entry.sourceSha256) == 64
    assert entry.sha256Before is not None
    assert entry.sha256After != entry.sha256Before
    assert entry.sha256After == entry.sourceSha256
    assert entry.bytesCopied == len(b"source")


def test_execute_clone_rejects_mismatched_backup_operation_id(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    backup_root = tmp_path / "backups"
    source.mkdir()
    target.mkdir()
    (source / "core_user_1.dat").write_bytes(b"source")
    (target / "core_user_1.dat").write_bytes(b"target")
    plan = plan_clone(scan_profile(source), scan_profile(target), CloneOptions(copy_core_user=True))
    manifest = create_backup_from_clone_plan(plan, backup_root)
    manifest.operationId = "wrong"

    try:
        execute_clone(plan, manifest)
    except ValueError as error:
        assert "operation ID" in str(error)
    else:
        raise AssertionError("execute_clone should reject mismatched backup operation IDs")


def test_execute_clone_rejects_backup_missing_planned_target(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    backup_root = tmp_path / "backups"
    source.mkdir()
    target.mkdir()
    (source / "core_user_1.dat").write_bytes(b"source")
    (target / "core_user_1.dat").write_bytes(b"target")
    plan = plan_clone(scan_profile(source), scan_profile(target), CloneOptions(copy_core_user=True))
    manifest = create_backup([], backup_root, source_path=source, target_path=target, operation_type="clone-plan-backup", operation_id=plan.operationId)

    try:
        execute_clone(plan, manifest)
    except ValueError as error:
        assert "does not cover" in str(error)
    else:
        raise AssertionError("execute_clone should require backup coverage for planned targets")
