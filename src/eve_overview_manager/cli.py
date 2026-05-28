"""Command line interface for smoke-testing core workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from ruamel.yaml.error import YAMLError


def _json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True, default=str)


def _error(code: str, message: str, details: str | None = None) -> str:
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details
    return _json(payload)


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        print(_error("ARGUMENT_ERROR", "Invalid command arguments.", message))
        raise SystemExit(2)


def main(argv: list[str] | None = None) -> int:
    parser = JsonArgumentParser(prog="eve-overview")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_yaml = subparsers.add_parser("validate-yaml")
    validate_yaml.add_argument("path")
    validate_yaml.add_argument("--group-ids")
    validate_yaml.add_argument("--format", choices=["json"], default="json")

    roundtrip_yaml = subparsers.add_parser("roundtrip-yaml")
    roundtrip_yaml.add_argument("input")
    roundtrip_yaml.add_argument("output")
    roundtrip_yaml.add_argument("--format", choices=["json"], default="json")

    validate_json = subparsers.add_parser("validate-json")
    validate_json.add_argument("path")
    validate_json.add_argument("--group-ids")
    validate_json.add_argument("--format", choices=["json"], default="json")

    export_json = subparsers.add_parser("export-json")
    export_json.add_argument("yaml_path")
    export_json.add_argument("json_output")
    export_json.add_argument("--format", choices=["json"], default="json")

    export_yaml_from_json = subparsers.add_parser("export-yaml-from-json")
    export_yaml_from_json.add_argument("json_path")
    export_yaml_from_json.add_argument("yaml_output")
    export_yaml_from_json.add_argument("--format", choices=["json"], default="json")

    generate_json = subparsers.add_parser("generate-json")
    generate_json.add_argument("spec_path")
    generate_json.add_argument("json_output")
    generate_json.add_argument("--format", choices=["json"], default="json")

    generate_yaml = subparsers.add_parser("generate-yaml")
    generate_yaml.add_argument("spec_path")
    generate_yaml.add_argument("yaml_output")
    generate_yaml.add_argument("--format", choices=["json"], default="json")

    create_project = subparsers.add_parser("create-project")
    create_project.add_argument("project_path")
    create_project.add_argument("--name", required=True)
    create_project.add_argument("--overview-json", required=True)
    create_project.add_argument("--snapshot-root")
    create_project.add_argument("--sde-archive")
    create_project.add_argument("--group-index")
    create_project.add_argument("--profile-root", action="append", default=[])
    create_project.add_argument("--notes")
    create_project.add_argument("--format", choices=["json"], default="json")

    validate_project = subparsers.add_parser("validate-project")
    validate_project.add_argument("project_path")
    validate_project.add_argument("--format", choices=["json"], default="json")

    download_sde = subparsers.add_parser("download-sde")
    download_sde.add_argument("output_zip")
    download_sde.add_argument("--format-kind", choices=["jsonl", "yaml"], default="jsonl")
    download_sde.add_argument("--url")
    download_sde.add_argument("--format", choices=["json"], default="json")

    build_group_index = subparsers.add_parser("build-group-index")
    build_group_index.add_argument("sde_path")
    build_group_index.add_argument("output_json")
    build_group_index.add_argument("--format", choices=["json"], default="json")

    build_group_name_index = subparsers.add_parser("build-group-name-index")
    build_group_name_index.add_argument("sde_path")
    build_group_name_index.add_argument("output_json")
    build_group_name_index.add_argument("--format", choices=["json"], default="json")

    snapshot_yaml = subparsers.add_parser("snapshot-yaml")
    snapshot_yaml.add_argument("yaml_path")
    snapshot_yaml.add_argument("--snapshot-root", required=True)
    snapshot_yaml.add_argument("--operation-type", default="import-yaml")
    snapshot_yaml.add_argument("--notes")
    snapshot_yaml.add_argument("--format", choices=["json"], default="json")

    list_snapshots = subparsers.add_parser("list-snapshots")
    list_snapshots.add_argument("--snapshot-root", required=True)
    list_snapshots.add_argument("--format", choices=["json"], default="json")

    restore_snapshot = subparsers.add_parser("restore-snapshot")
    restore_snapshot.add_argument("manifest_path")
    restore_snapshot.add_argument("output_json")
    restore_snapshot.add_argument("--overwrite", action="store_true")
    restore_snapshot.add_argument("--format", choices=["json"], default="json")

    restore_snapshot_yaml = subparsers.add_parser("restore-snapshot-yaml")
    restore_snapshot_yaml.add_argument("manifest_path")
    restore_snapshot_yaml.add_argument("output_yaml")
    restore_snapshot_yaml.add_argument("--overwrite", action="store_true")
    restore_snapshot_yaml.add_argument("--format", choices=["json"], default="json")

    scan_profiles = subparsers.add_parser("scan-profiles")
    scan_profiles.add_argument("root")
    scan_profiles.add_argument("--resolve-names", action="store_true")
    scan_profiles.add_argument("--name-cache")
    scan_profiles.add_argument("--format", choices=["json"], default="json")

    profile_report = subparsers.add_parser("profile-report")
    profile_report.add_argument("profile_path")
    profile_report.add_argument("--resolve-names", action="store_true")
    profile_report.add_argument("--name-cache")
    profile_report.add_argument("--no-checksums", action="store_true")
    profile_report.add_argument("--format", choices=["json"], default="json")

    plan_clone = subparsers.add_parser("plan-clone")
    plan_clone.add_argument("--source", required=True)
    plan_clone.add_argument("--target", required=True)
    plan_clone.add_argument("--core-user", action="store_true")
    plan_clone.add_argument("--core-char", action="store_true")
    plan_clone.add_argument("--prefs", action="store_true")
    plan_clone.add_argument("--copy-first-to-all", action="store_true")
    plan_clone.add_argument("--format", choices=["json"], default="json")

    backup_profile = subparsers.add_parser("backup-profile")
    backup_profile.add_argument("profile_path")
    backup_profile.add_argument("--backup-root", required=True)
    backup_profile.add_argument("--format", choices=["json"], default="json")

    backup_plan = subparsers.add_parser("backup-plan")
    backup_plan.add_argument("plan_json")
    backup_plan.add_argument("--backup-root", required=True)
    backup_plan.add_argument("--format", choices=["json"], default="json")

    execute_clone = subparsers.add_parser("execute-clone")
    execute_clone.add_argument("plan_json")
    execute_clone.add_argument("--backup-manifest", required=True)
    execute_clone.add_argument("--format", choices=["json"], default="json")

    rollback_backup = subparsers.add_parser("rollback-backup")
    rollback_backup.add_argument("backup_manifest")
    rollback_backup.add_argument("--format", choices=["json"], default="json")

    export_profile_package = subparsers.add_parser("export-profile-package")
    export_profile_package.add_argument("profile_path")
    export_profile_package.add_argument("package_path")
    export_profile_package.add_argument("--core-user", action="store_true")
    export_profile_package.add_argument("--core-char", action="store_true", default=True)
    export_profile_package.add_argument("--no-core-char", action="store_false", dest="core_char")
    export_profile_package.add_argument("--prefs", action="store_true")
    export_profile_package.add_argument("--snapshot-name")
    export_profile_package.add_argument("--notes")
    export_profile_package.add_argument("--format", choices=["json"], default="json")

    inspect_profile_package = subparsers.add_parser("inspect-profile-package")
    inspect_profile_package.add_argument("package_path")
    inspect_profile_package.add_argument("--format", choices=["json"], default="json")

    plan_profile_package_import = subparsers.add_parser("plan-profile-package-import")
    plan_profile_package_import.add_argument("package_path")
    plan_profile_package_import.add_argument("destination_profile")
    plan_profile_package_import.add_argument("--format", choices=["json"], default="json")

    execute_profile_package_import = subparsers.add_parser("execute-profile-package-import")
    execute_profile_package_import.add_argument("plan_json")
    execute_profile_package_import.add_argument("--backup-manifest", required=True)
    execute_profile_package_import.add_argument("--package-path")
    execute_profile_package_import.add_argument("--format", choices=["json"], default="json")

    gui_cmd = subparsers.add_parser("gui")
    gui_cmd.add_argument("--port", type=int, default=7477)
    gui_cmd.add_argument("--no-browser", action="store_true")

    args = parser.parse_args(argv)

    try:
        return _run_command(args)
    except FileNotFoundError as error:
        print(_error("FILE_NOT_FOUND", "A required file or directory was not found.", str(error)))
        return 1
    except FileExistsError as error:
        print(_error("FILE_EXISTS", "Refusing to overwrite an existing file.", str(error)))
        return 1
    except OSError as error:
        print(_error("OS_ERROR", "The filesystem operation could not be completed.", str(error)))
        return 1
    except UnicodeDecodeError as error:
        print(_error("DECODE_ERROR", "A text file could not be decoded as UTF-8.", str(error)))
        return 1
    except ValidationError as error:
        print(_error("VALIDATION_ERROR", "Input did not match the expected schema.", str(error)))
        return 1
    except YAMLError as error:
        print(_error("YAML_PARSE_ERROR", "YAML could not be parsed.", str(error)))
        return 1
    except ValueError as error:
        print(_error("VALUE_ERROR", "The requested operation could not be completed.", str(error)))
        return 1


def _run_command(args: argparse.Namespace) -> int:

    if args.command == "validate-yaml":
        from eve_overview_manager.validation.engine import validate_overview
        from eve_overview_manager.validation.group_validator import load_group_validator
        from eve_overview_manager.yaml_io.parser import load_overview_yaml

        document = load_overview_yaml(Path(args.path))
        group_validator = load_group_validator(args.group_ids) if args.group_ids else None
        results = [result.model_dump() for result in validate_overview(document, group_validator=group_validator)]
        import_warnings = [warning.model_dump() for warning in document.meta.importWarnings]
        print(_json({"path": args.path, "importWarnings": import_warnings, "validationResults": results, "results": [*import_warnings, *results]}))
        return 1 if any(result["severity"] == "error" for result in results) else 0

    if args.command == "roundtrip-yaml":
        from eve_overview_manager.yaml_io.roundtrip import roundtrip_overview_yaml

        roundtrip_overview_yaml(Path(args.input), Path(args.output))
        print(_json({"input": args.input, "output": args.output, "status": "ok"}))
        return 0

    if args.command == "validate-json":
        from eve_overview_manager.json_io.parser import load_overview_json
        from eve_overview_manager.validation.engine import validate_overview
        from eve_overview_manager.validation.group_validator import load_group_validator

        document = load_overview_json(Path(args.path))
        group_validator = load_group_validator(args.group_ids) if args.group_ids else None
        results = [result.model_dump() for result in validate_overview(document, group_validator=group_validator)]
        print(_json({"path": args.path, "validationResults": results, "results": results}))
        return 1 if any(result["severity"] == "error" for result in results) else 0

    if args.command == "export-json":
        from eve_overview_manager.json_io.exporter import export_overview_json
        from eve_overview_manager.yaml_io.parser import load_overview_yaml

        export_overview_json(load_overview_yaml(Path(args.yaml_path)), Path(args.json_output))
        print(_json({"input": args.yaml_path, "output": args.json_output, "status": "ok"}))
        return 0

    if args.command == "export-yaml-from-json":
        from eve_overview_manager.json_io.parser import load_overview_json
        from eve_overview_manager.yaml_io.exporter import export_overview_yaml

        export_overview_yaml(load_overview_json(Path(args.json_path)), Path(args.yaml_output))
        print(_json({"input": args.json_path, "output": args.yaml_output, "status": "ok"}))
        return 0

    if args.command == "generate-json":
        from eve_overview_manager.generator.builder import build_overview_document, load_generator_spec
        from eve_overview_manager.json_io.exporter import export_overview_json

        document = build_overview_document(load_generator_spec(Path(args.spec_path)))
        export_overview_json(document, Path(args.json_output))
        print(_json({"input": args.spec_path, "output": args.json_output, "status": "ok"}))
        return 0

    if args.command == "generate-yaml":
        from eve_overview_manager.generator.builder import build_overview_document, load_generator_spec
        from eve_overview_manager.yaml_io.exporter import export_overview_yaml

        document = build_overview_document(load_generator_spec(Path(args.spec_path)))
        export_overview_yaml(document, Path(args.yaml_output))
        print(_json({"input": args.spec_path, "output": args.yaml_output, "status": "ok"}))
        return 0

    if args.command == "create-project":
        from eve_overview_manager.project_io.project import create_project

        project = create_project(
            Path(args.project_path),
            name=args.name,
            overview_document=Path(args.overview_json),
            snapshot_root=Path(args.snapshot_root) if args.snapshot_root else None,
            sde_archive=Path(args.sde_archive) if args.sde_archive else None,
            group_index=Path(args.group_index) if args.group_index else None,
            profile_roots=[Path(path) for path in args.profile_root],
            notes=args.notes,
        )
        print(_json({"projectPath": args.project_path, "project": project.model_dump(), "status": "ok"}))
        return 0

    if args.command == "validate-project":
        from eve_overview_manager.project_io.project import load_project, validate_project

        project = load_project(Path(args.project_path))
        errors = validate_project(Path(args.project_path))
        print(_json({"projectPath": args.project_path, "project": project.model_dump(), "errors": errors}))
        return 1 if errors else 0

    if args.command == "download-sde":
        from eve_overview_manager.services.downloads import SDE_JSONL_LATEST_URL, SDE_YAML_LATEST_URL, download_file

        default_url = SDE_JSONL_LATEST_URL if args.format_kind == "jsonl" else SDE_YAML_LATEST_URL
        output = download_file(args.url or default_url, Path(args.output_zip))
        print(_json({"output": str(output), "url": args.url or default_url, "status": "ok"}))
        return 0

    if args.command == "build-group-index":
        from eve_overview_manager.validation.sde import build_group_id_index

        group_ids = build_group_id_index(Path(args.sde_path), Path(args.output_json))
        print(_json({"input": args.sde_path, "output": args.output_json, "groupCount": len(group_ids), "status": "ok"}))
        return 0

    if args.command == "build-group-name-index":
        from eve_overview_manager.validation.sde import build_group_name_index

        group_names = build_group_name_index(Path(args.sde_path), Path(args.output_json))
        print(_json({"input": args.sde_path, "output": args.output_json, "groupCount": len(group_names), "status": "ok"}))
        return 0

    if args.command == "snapshot-yaml":
        from eve_overview_manager.services.snapshots import create_overview_snapshot
        from eve_overview_manager.yaml_io.parser import load_overview_yaml

        manifest = create_overview_snapshot(
            load_overview_yaml(Path(args.yaml_path)),
            Path(args.snapshot_root),
            operation_type=args.operation_type,
            source_path=Path(args.yaml_path),
            notes=args.notes,
        )
        print(_json(manifest.model_dump()))
        return 0

    if args.command == "list-snapshots":
        from eve_overview_manager.services.snapshots import list_snapshots

        manifests = [manifest.model_dump() for manifest in list_snapshots(Path(args.snapshot_root))]
        print(_json({"snapshotRoot": args.snapshot_root, "snapshots": manifests}))
        return 0

    if args.command == "restore-snapshot":
        from eve_overview_manager.models.snapshot import SnapshotManifest
        from eve_overview_manager.services.snapshots import restore_snapshot

        manifest = SnapshotManifest.model_validate_json(Path(args.manifest_path).read_text(encoding="utf-8"))
        output = restore_snapshot(manifest, Path(args.output_json), overwrite=args.overwrite)
        print(_json({"manifestPath": args.manifest_path, "output": str(output), "status": "ok"}))
        return 0

    if args.command == "restore-snapshot-yaml":
        from eve_overview_manager.models.snapshot import SnapshotManifest
        from eve_overview_manager.services.snapshots import restore_snapshot_to_yaml

        manifest = SnapshotManifest.model_validate_json(Path(args.manifest_path).read_text(encoding="utf-8"))
        output = restore_snapshot_to_yaml(manifest, Path(args.output_yaml), overwrite=args.overwrite)
        print(_json({"manifestPath": args.manifest_path, "output": str(output), "status": "ok"}))
        return 0

    if args.command == "scan-profiles":
        from eve_overview_manager.profiles.name_resolver import resolve_character_names
        from eve_overview_manager.profiles.scanner import scan_profiles

        name_resolver = (lambda ids: resolve_character_names(ids, cache_path=args.name_cache)) if args.resolve_names else None
        profiles = [
            profile.model_dump()
            for profile in scan_profiles(
                Path(args.root),
                name_resolver=name_resolver,
            )
        ]
        print(_json({"root": args.root, "profiles": profiles}))
        return 0

    if args.command == "profile-report":
        from eve_overview_manager.profiles.name_resolver import resolve_character_names
        from eve_overview_manager.profiles.report import build_profile_report

        name_resolver = (lambda ids: resolve_character_names(ids, cache_path=args.name_cache)) if args.resolve_names else None
        report = build_profile_report(
            Path(args.profile_path),
            name_resolver=name_resolver,
            include_checksums=not args.no_checksums,
        )
        print(_json(report))
        return 0

    if args.command == "plan-clone":
        from eve_overview_manager.profiles.clone_planner import CloneOptions, plan_clone
        from eve_overview_manager.profiles.scanner import scan_profile

        plan = plan_clone(
            scan_profile(Path(args.source)),
            scan_profile(Path(args.target)),
            CloneOptions(
                copy_core_user=args.core_user,
                copy_core_char=args.core_char,
                copy_prefs=args.prefs,
                copy_first_to_all=args.copy_first_to_all,
            ),
        )
        print(_json(plan.model_dump()))
        return 1 if plan.blocked else 0

    if args.command == "backup-profile":
        from eve_overview_manager.profiles.backup import create_backup

        profile_path = Path(args.profile_path)
        files = [path for path in profile_path.iterdir() if path.is_file()]
        manifest = create_backup(files, Path(args.backup_root), source_path=profile_path, target_path=profile_path)
        print(_json(manifest.model_dump()))
        return 0

    if args.command == "backup-plan":
        from eve_overview_manager.models.profile import ClonePlan
        from eve_overview_manager.profiles.backup import create_backup_from_clone_plan

        plan = ClonePlan.model_validate_json(Path(args.plan_json).read_text(encoding="utf-8"))
        manifest = create_backup_from_clone_plan(plan, Path(args.backup_root))
        print(_json(manifest.model_dump()))
        return 0

    if args.command == "execute-clone":
        from eve_overview_manager.models.profile import BackupManifest, ClonePlan
        from eve_overview_manager.profiles.clone_executor import execute_clone

        plan_path = Path(args.plan_json)
        plan = ClonePlan.model_validate_json(plan_path.read_text(encoding="utf-8"))
        backup_manifest_path = Path(args.backup_manifest)
        backup_manifest = BackupManifest.model_validate_json(backup_manifest_path.read_text(encoding="utf-8"))
        audit = execute_clone(plan, backup_manifest, plan_path=str(plan_path))
        print(_json(audit.model_dump()))
        return 0

    if args.command == "rollback-backup":
        from eve_overview_manager.models.profile import BackupManifest
        from eve_overview_manager.profiles.backup import rollback_backup

        backup_manifest_path = Path(args.backup_manifest)
        backup_manifest = BackupManifest.model_validate_json(backup_manifest_path.read_text(encoding="utf-8"))
        audit = rollback_backup(backup_manifest)
        print(_json(audit.model_dump()))
        return 0

    if args.command == "export-profile-package":
        from eve_overview_manager.profiles.package_exporter import export_profile_package
        from eve_overview_manager.profiles.scanner import scan_profile

        manifest = export_profile_package(
            scan_profile(Path(args.profile_path)),
            Path(args.package_path),
            include_core_user=args.core_user,
            include_core_char=args.core_char,
            include_prefs=args.prefs,
            snapshot_name=args.snapshot_name,
            notes=args.notes,
        )
        print(_json(manifest.model_dump()))
        return 0

    if args.command == "inspect-profile-package":
        from eve_overview_manager.profiles.package_exporter import inspect_profile_package

        inspection = inspect_profile_package(Path(args.package_path))
        print(_json(inspection.model_dump()))
        return 0 if inspection.ok else 1

    if args.command == "plan-profile-package-import":
        from eve_overview_manager.profiles.package_import_planner import plan_profile_package_import
        from eve_overview_manager.profiles.scanner import scan_profile

        plan = plan_profile_package_import(Path(args.package_path), scan_profile(Path(args.destination_profile)))
        print(_json(plan.model_dump()))
        return 1 if plan.blocked else 0

    if args.command == "execute-profile-package-import":
        from eve_overview_manager.models.profile import BackupManifest, ClonePlan
        from eve_overview_manager.profiles.package_import_executor import execute_profile_package_import

        plan_path = Path(args.plan_json)
        plan = ClonePlan.model_validate_json(plan_path.read_text(encoding="utf-8"))
        backup_manifest_path = Path(args.backup_manifest)
        backup_manifest = BackupManifest.model_validate_json(backup_manifest_path.read_text(encoding="utf-8"))
        audit = execute_profile_package_import(
            plan,
            backup_manifest,
            package_path=Path(args.package_path) if args.package_path else None,
            plan_path=str(plan_path),
        )
        print(_json(audit.model_dump()))
        return 0

    if args.command == "gui":
        from eve_overview_manager.gui.server import run_gui
        run_gui(port=args.port, open_browser=not args.no_browser)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
