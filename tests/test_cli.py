import json
from pathlib import Path

import pytest

from eve_overview_manager.cli import main
from eve_overview_manager.profiles.clone_planner import CloneOptions, plan_clone
from eve_overview_manager.profiles.scanner import scan_profile


def test_cli_validate_yaml_outputs_json(capsys):
    exit_code = main(["validate-yaml", "Examples/Real-Overview.yaml", "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["path"] == "Examples/Real-Overview.yaml"
    assert output["importWarnings"] == []
    assert output["validationResults"] == []
    assert output["results"] == []


def test_cli_validate_yaml_with_group_ids_warns_for_unknown_group(tmp_path, capsys):
    group_ids = tmp_path / "groups.json"
    group_ids.write_text("[6]", encoding="utf-8")

    exit_code = main(["validate-yaml", "Examples/Real-Overview.yaml", "--group-ids", str(group_ids), "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert any(result["code"] == "GROUP_ID_KNOWN" for result in output["validationResults"])


def test_cli_build_group_index_from_sde_zip(tmp_path, capsys):
    import zipfile

    archive = tmp_path / "sde.zip"
    output_path = tmp_path / "group_ids.json"
    with zipfile.ZipFile(archive, "w") as file:
        file.writestr("fsd/groups.jsonl", '{"_key": 25}\n{"_key": 26}\n')

    exit_code = main(["build-group-index", str(archive), str(output_path), "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["groupCount"] == 2
    assert output_path.exists()


def test_cli_build_group_name_index_from_sde_zip(tmp_path, capsys):
    import zipfile

    archive = tmp_path / "sde.zip"
    output_path = tmp_path / "group_names.json"
    with zipfile.ZipFile(archive, "w") as file:
        file.writestr("fsd/groups.jsonl", '{"_key": 25, "name": {"en": "Frigate"}}\n{"_key": 26, "name": "Destroyer"}\n')

    exit_code = main(["build-group-name-index", str(archive), str(output_path), "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["groupCount"] == 2
    assert json.loads(output_path.read_text(encoding="utf-8")) == {"25": "Frigate", "26": "Destroyer"}


def test_cli_roundtrip_yaml_writes_output(tmp_path, capsys):
    output_path = tmp_path / "roundtrip.yaml"

    exit_code = main(["roundtrip-yaml", "Examples/sample_overview.yaml", str(output_path), "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["status"] == "ok"
    assert output_path.exists()


def test_cli_export_and_validate_json(tmp_path, capsys):
    json_path = tmp_path / "real.json"

    export_exit = main(["export-json", "Examples/Real-Overview.yaml", str(json_path), "--format", "json"])
    export_output = json.loads(capsys.readouterr().out)
    validate_exit = main(["validate-json", str(json_path), "--format", "json"])
    validate_output = json.loads(capsys.readouterr().out)

    assert export_exit == 0
    assert export_output["status"] == "ok"
    assert json_path.exists()
    assert validate_exit == 0
    assert validate_output["validationResults"] == []


def test_cli_create_and_validate_project(tmp_path, capsys):
    json_path = tmp_path / "real.json"
    project_path = tmp_path / "workspace.eveoverview.json"
    snapshot_root = tmp_path / "snapshots"
    group_index = tmp_path / "group_ids.json"
    snapshot_root.mkdir()
    group_index.write_text("[6, 10, 25, 26, 27, 28]", encoding="utf-8")
    main(["export-json", "Examples/Real-Overview.yaml", str(json_path), "--format", "json"])
    capsys.readouterr()

    create_exit = main(
        [
            "create-project",
            str(project_path),
            "--name",
            "Test Workspace",
            "--overview-json",
            str(json_path),
            "--snapshot-root",
            str(snapshot_root),
            "--group-index",
            str(group_index),
            "--format",
            "json",
        ]
    )
    create_output = json.loads(capsys.readouterr().out)
    validate_exit = main(["validate-project", str(project_path), "--format", "json"])
    validate_output = json.loads(capsys.readouterr().out)

    assert create_exit == 0
    assert create_output["status"] == "ok"
    assert create_output["project"]["paths"]["groupIndex"] == "group_ids.json"
    assert project_path.exists()
    assert validate_exit == 0
    assert validate_output["errors"] == []


def test_cli_export_yaml_from_json(tmp_path, capsys):
    json_path = tmp_path / "real.json"
    yaml_path = tmp_path / "real.yaml"
    main(["export-json", "Examples/Real-Overview.yaml", str(json_path), "--format", "json"])
    capsys.readouterr()

    exit_code = main(["export-yaml-from-json", str(json_path), str(yaml_path), "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["status"] == "ok"
    assert yaml_path.exists()


def test_cli_generate_json_and_yaml_from_generator_spec(tmp_path, capsys):
    json_path = tmp_path / "generated.json"
    yaml_path = tmp_path / "generated.yaml"

    json_exit = main(["generate-json", "Examples/sample_generator.json", str(json_path), "--format", "json"])
    json_output = json.loads(capsys.readouterr().out)
    yaml_exit = main(["generate-yaml", "Examples/sample_generator.json", str(yaml_path), "--format", "json"])
    yaml_output = json.loads(capsys.readouterr().out)

    assert json_exit == 0
    assert json_output["status"] == "ok"
    assert json_path.exists()
    assert yaml_exit == 0
    assert yaml_output["status"] == "ok"
    assert yaml_path.exists()


def test_cli_snapshot_yaml_writes_manifest(tmp_path, capsys):
    snapshot_root = tmp_path / "snapshots"

    exit_code = main(
        [
            "snapshot-yaml",
            "Examples/Real-Overview.yaml",
            "--snapshot-root",
            str(snapshot_root),
            "--operation-type",
            "import-yaml",
            "--notes",
            "cli test",
            "--format",
            "json",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["operationType"] == "import-yaml"
    assert output["notes"] == "cli test"
    assert Path(output["documentPath"]).exists()
    assert Path(output["manifestPath"]).exists()


def test_cli_list_and_restore_snapshot(tmp_path, capsys):
    snapshot_root = tmp_path / "snapshots"
    restore_path = tmp_path / "restored.json"
    main(["snapshot-yaml", "Examples/Real-Overview.yaml", "--snapshot-root", str(snapshot_root), "--format", "json"])
    manifest = json.loads(capsys.readouterr().out)

    list_exit = main(["list-snapshots", "--snapshot-root", str(snapshot_root), "--format", "json"])
    list_output = json.loads(capsys.readouterr().out)
    restore_exit = main(["restore-snapshot", manifest["manifestPath"], str(restore_path), "--format", "json"])
    restore_output = json.loads(capsys.readouterr().out)

    assert list_exit == 0
    assert len(list_output["snapshots"]) == 1
    assert restore_exit == 0
    assert restore_output["status"] == "ok"
    assert restore_path.exists()


def test_cli_restore_snapshot_yaml(tmp_path, capsys):
    snapshot_root = tmp_path / "snapshots"
    restore_path = tmp_path / "restored.yaml"
    main(["snapshot-yaml", "Examples/Real-Overview.yaml", "--snapshot-root", str(snapshot_root), "--format", "json"])
    manifest = json.loads(capsys.readouterr().out)

    exit_code = main(["restore-snapshot-yaml", manifest["manifestPath"], str(restore_path), "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["status"] == "ok"
    assert restore_path.exists()


def test_cli_missing_file_returns_structured_json_error(capsys):
    exit_code = main(["validate-yaml", "missing.yaml", "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["error"]["code"] == "FILE_NOT_FOUND"


def test_cli_invalid_json_returns_structured_json_error(tmp_path, capsys):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text('{"tabs": "not-a-list"}', encoding="utf-8")

    exit_code = main(["validate-json", str(bad_json), "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["error"]["code"] == "VALIDATION_ERROR"


def test_cli_restore_snapshot_refuses_overwrite_with_json_error(tmp_path, capsys):
    snapshot_root = tmp_path / "snapshots"
    restore_path = tmp_path / "restored.json"
    restore_path.write_text("existing", encoding="utf-8")
    main(["snapshot-yaml", "Examples/Real-Overview.yaml", "--snapshot-root", str(snapshot_root), "--format", "json"])
    manifest = json.loads(capsys.readouterr().out)

    exit_code = main(["restore-snapshot", manifest["manifestPath"], str(restore_path), "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["error"]["code"] == "FILE_EXISTS"


def test_cli_restore_snapshot_yaml_refuses_overwrite_with_json_error(tmp_path, capsys):
    snapshot_root = tmp_path / "snapshots"
    restore_path = tmp_path / "restored.yaml"
    restore_path.write_text("existing", encoding="utf-8")
    main(["snapshot-yaml", "Examples/Real-Overview.yaml", "--snapshot-root", str(snapshot_root), "--format", "json"])
    manifest = json.loads(capsys.readouterr().out)

    exit_code = main(["restore-snapshot-yaml", manifest["manifestPath"], str(restore_path), "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["error"]["code"] == "FILE_EXISTS"


def test_cli_argument_error_returns_structured_json(capsys):
    with pytest.raises(SystemExit) as error:
        main(["plan-clone", "--source", "only-source"])

    output = json.loads(capsys.readouterr().out)
    assert error.value.code == 2
    assert output["error"]["code"] == "ARGUMENT_ERROR"


def test_cli_directory_as_json_file_returns_structured_json_error(tmp_path, capsys):
    exit_code = main(["validate-json", str(tmp_path), "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["error"]["code"] == "OS_ERROR"


def test_cli_utf8_decode_error_returns_structured_json_error(tmp_path, capsys):
    bad_text = tmp_path / "bad.yaml"
    bad_text.write_bytes(b"\xff\xfe\x00")

    exit_code = main(["validate-yaml", str(bad_text), "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["error"]["code"] == "DECODE_ERROR"


def test_cli_scan_profiles_outputs_profile_data(tmp_path, capsys):
    profile = tmp_path / "settings_Default"
    profile.mkdir()
    (profile / "core_user_123.dat").write_bytes(b"user")
    (profile / "core_char_456.dat").write_bytes(b"char")

    exit_code = main(["scan-profiles", str(tmp_path), "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["profiles"][0]["profilePath"] == str(profile)
    assert output["profiles"][0]["characterFiles"][0]["characterId"] == 456


def test_cli_profile_report_outputs_file_summary(tmp_path, capsys):
    profile = tmp_path / "settings_Default"
    profile.mkdir()
    (profile / "core_char_456.dat").write_bytes(b"char")
    (profile / "prefs.ini").write_text("[prefs]\n", encoding="utf-8")

    exit_code = main(["profile-report", str(profile), "--no-checksums", "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["profilePath"] == str(profile)
    assert output["counts"]["coreChar"] == 1
    assert output["backupReady"] is True
    assert "sha256" not in output["files"][0]


def test_cli_plan_clone_outputs_dry_run_actions(tmp_path, capsys):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "core_user_1.dat").write_bytes(b"source")
    (target / "core_user_1.dat").write_bytes(b"target")

    exit_code = main(["plan-clone", "--source", str(source), "--target", str(target), "--core-user", "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["actions"][0]["fileType"] == "core_user"
    assert output["actions"][0]["wouldOverwrite"] is True
    assert output["summary"]["dryRun"] is True
    assert Path(output["actions"][0]["targetFile"]).read_bytes() == b"target"


def test_cli_backup_profile_writes_manifest(tmp_path, capsys):
    profile = tmp_path / "settings_Default"
    backup_root = tmp_path / "backups"
    profile.mkdir()
    (profile / "prefs.ini").write_text("[prefs]\n", encoding="utf-8")

    exit_code = main(["backup-profile", str(profile), "--backup-root", str(backup_root), "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert len(output["fileList"]) == 1
    assert (backup_root / output["timestamp"] / "backup_manifest.json").exists()


def test_cli_backup_plan_backs_up_planned_targets(tmp_path, capsys):
    source = tmp_path / "source"
    target = tmp_path / "target"
    backup_root = tmp_path / "backups"
    source.mkdir()
    target.mkdir()
    (source / "core_user_1.dat").write_bytes(b"source")
    (target / "core_user_1.dat").write_bytes(b"target")
    plan = plan_clone(scan_profile(source), scan_profile(target), CloneOptions(copy_core_user=True))
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(plan.model_dump_json(), encoding="utf-8")

    exit_code = main(["backup-plan", str(plan_path), "--backup-root", str(backup_root), "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["operationId"] == plan.operationId
    assert output["operationType"] == "clone-plan-backup"
    assert len(output["fileList"]) == 1


def test_cli_execute_clone_applies_reviewed_plan_with_backup(tmp_path, capsys):
    source = tmp_path / "source"
    target = tmp_path / "target"
    backup_root = tmp_path / "backups"
    source.mkdir()
    target.mkdir()
    (source / "core_user_1.dat").write_bytes(b"source")
    target_file = target / "core_user_1.dat"
    target_file.write_bytes(b"target")
    plan = plan_clone(scan_profile(source), scan_profile(target), CloneOptions(copy_core_user=True))
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(plan.model_dump_json(), encoding="utf-8")
    main(["backup-plan", str(plan_path), "--backup-root", str(backup_root), "--format", "json"])
    manifest = json.loads(capsys.readouterr().out)

    exit_code = main(["execute-clone", str(plan_path), "--backup-manifest", manifest["manifestPath"], "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert len(output["actionsApplied"]) == 1
    assert output["operationId"] == plan.operationId
    assert "auditManifestPath" in output
    assert Path(output["auditManifestPath"]).exists()
    assert output["backupManifestPath"] == manifest["manifestPath"]
    assert output["actionsApplied"][0]["sourceSha256"] == output["actionsApplied"][0]["sha256After"]
    assert output["actionsApplied"][0]["bytesCopied"] == len(b"source")
    assert target_file.read_bytes() == b"source"


def test_cli_execute_clone_rejects_bad_backup_manifest(tmp_path, capsys):
    source = tmp_path / "source"
    target = tmp_path / "target"
    backup_root = tmp_path / "backups"
    source.mkdir()
    target.mkdir()
    (source / "core_user_1.dat").write_bytes(b"source")
    (target / "core_user_1.dat").write_bytes(b"target")
    plan = plan_clone(scan_profile(source), scan_profile(target), CloneOptions(copy_core_user=True))
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(plan.model_dump_json(), encoding="utf-8")
    main(["backup-plan", str(plan_path), "--backup-root", str(backup_root), "--format", "json"])
    manifest = json.loads(capsys.readouterr().out)
    Path(manifest["fileList"][0]["backupPath"]).write_text("changed", encoding="utf-8")

    exit_code = main(["execute-clone", str(plan_path), "--backup-manifest", manifest["manifestPath"], "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["error"]["code"] == "VALUE_ERROR"


def test_cli_execute_profile_package_import_applies_reviewed_plan_with_backup(tmp_path, capsys):
    from eve_overview_manager.profiles.package_exporter import export_profile_package
    from eve_overview_manager.profiles.package_import_planner import plan_profile_package_import

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
    plan_path = tmp_path / "package-plan.json"
    plan_path.write_text(plan.model_dump_json(), encoding="utf-8")
    main(["backup-plan", str(plan_path), "--backup-root", str(backup_root), "--format", "json"])
    manifest = json.loads(capsys.readouterr().out)

    exit_code = main(["execute-profile-package-import", str(plan_path), "--backup-manifest", manifest["manifestPath"], "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert target_file.read_bytes() == b"source-char"
    assert output["actionsApplied"][0]["targetFile"] == str(target_file)


def test_cli_rollback_backup_restores_files(tmp_path, capsys):
    profile = tmp_path / "settings_Default"
    backup_root = tmp_path / "backups"
    profile.mkdir()
    prefs = profile / "prefs.ini"
    prefs.write_text("original", encoding="utf-8")
    main(["backup-profile", str(profile), "--backup-root", str(backup_root), "--format", "json"])
    manifest = json.loads(capsys.readouterr().out)
    prefs.write_text("changed", encoding="utf-8")

    exit_code = main(["rollback-backup", manifest["manifestPath"], "--format", "json"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert prefs.read_text(encoding="utf-8") == "original"
    assert output["backupManifestPath"] == manifest["manifestPath"]
    assert Path(output["auditManifestPath"]).exists()
    assert output["actionsApplied"][0]["sha256After"] == output["actionsApplied"][0]["backupSha256"]


def test_cli_profile_package_export_inspect_and_plan_import(tmp_path, capsys):
    source = tmp_path / "source"
    target = tmp_path / "target"
    package = tmp_path / "profile.zip"
    source.mkdir()
    target.mkdir()
    (source / "core_char_100.dat").write_bytes(b"source")
    target_file = target / "core_char_100.dat"
    target_file.write_bytes(b"target")

    export_code = main(["export-profile-package", str(source), str(package), "--snapshot-name", "Known Good", "--format", "json"])
    export_output = json.loads(capsys.readouterr().out)
    inspect_code = main(["inspect-profile-package", str(package), "--format", "json"])
    inspect_output = json.loads(capsys.readouterr().out)
    plan_code = main(["plan-profile-package-import", str(package), str(target), "--format", "json"])
    plan_output = json.loads(capsys.readouterr().out)

    assert export_code == 0
    assert export_output["snapshotName"] == "Known Good"
    assert inspect_code == 0
    assert inspect_output["ok"] is True
    assert plan_code == 0
    assert plan_output["summary"]["dryRun"] is True
    assert plan_output["actions"][0]["targetFile"] == str(target_file)
    assert target_file.read_bytes() == b"target"
