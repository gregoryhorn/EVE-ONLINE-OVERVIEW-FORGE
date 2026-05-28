"""Guarded execution for portable profile package imports."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path
from zipfile import ZipFile

from eve_overview_manager import __version__
from eve_overview_manager.models.profile import BackupManifest, ClonePlan, ExecutionAuditEntry, ExecutionAuditManifest
from eve_overview_manager.profiles.backup import verify_backup
from eve_overview_manager.profiles.package_exporter import inspect_profile_package
from eve_overview_manager.services.checksums import sha256_file


def execute_profile_package_import(
    plan: ClonePlan,
    backup_manifest: BackupManifest,
    *,
    package_path: str | Path | None = None,
    plan_path: str | None = None,
    audit_path: str | Path | None = None,
) -> ExecutionAuditManifest:
    resolved_package = Path(package_path or plan.source)
    manifest = _validate_package_import_execution(plan, backup_manifest, resolved_package)
    entries_by_package_path = {entry.packagePath: entry for entry in manifest.fileList}
    audit_entries: list[ExecutionAuditEntry] = []

    with ZipFile(resolved_package) as archive:
        for action in plan.actions:
            _, archive_path = _split_package_source(action.sourceFile)
            entry = entries_by_package_path[archive_path]
            target = Path(action.targetFile)
            sha256_before = sha256_file(target) if target.exists() else None
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(archive_path) as source, target.open("wb") as destination:
                shutil.copyfileobj(source, destination)
            audit_entries.append(
                ExecutionAuditEntry(
                    action=action.action,
                    sourceFile=action.sourceFile,
                    targetFile=action.targetFile,
                    sourceSha256=entry.sha256,
                    sha256Before=sha256_before,
                    sha256After=sha256_file(target),
                    bytesCopied=entry.size,
                )
            )

    resolved_audit_path = _default_audit_path(backup_manifest) if audit_path is None else Path(audit_path)
    audit = ExecutionAuditManifest(
        operationId=plan.operationId,
        timestamp=datetime.now(UTC).isoformat(),
        planPath=plan_path,
        backupManifestPath=backup_manifest.manifestPath,
        auditManifestPath=str(resolved_audit_path),
        actionsApplied=audit_entries,
        appVersion=__version__,
    )
    resolved_audit_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_audit_path.write_text(audit.model_dump_json(indent=2), encoding="utf-8")
    return audit


def _validate_package_import_execution(plan: ClonePlan, backup_manifest: BackupManifest, package_path: Path):
    if plan.blocked:
        raise ValueError("Blocked package import plans cannot be executed.")
    if plan.summary.dryRun is not True:
        raise ValueError("Package import execution requires a reviewed dry-run plan.")
    if backup_manifest.operationId != plan.operationId:
        raise ValueError("Backup manifest operation ID does not match package import plan operation ID.")
    verification = verify_backup(backup_manifest)
    if not verification.ok:
        raise ValueError("; ".join(verification.errors))

    backed_up_targets = {entry.sourcePath for entry in backup_manifest.fileList}
    planned_targets = {action.targetFile for action in plan.actions}
    missing_backups = sorted(planned_targets - backed_up_targets)
    if missing_backups:
        raise ValueError(f"Backup manifest does not cover planned target files: {', '.join(missing_backups)}")

    inspection = inspect_profile_package(package_path)
    if not inspection.ok or inspection.manifest is None:
        raise ValueError("; ".join(inspection.errors or ["Package inspection failed."]))
    entries_by_package_path = {entry.packagePath: entry for entry in inspection.manifest.fileList}

    for action in plan.actions:
        if action.action != "copy":
            raise ValueError(f"Unsupported package import action: {action.action}")
        source_package, archive_path = _split_package_source(action.sourceFile)
        if source_package and Path(source_package) != package_path:
            raise ValueError(f"Plan action references a different package: {source_package}")
        if archive_path not in entries_by_package_path:
            raise ValueError(f"Plan action references a file not present in package manifest: {archive_path}")
        entry = entries_by_package_path[archive_path]
        if entry.fileType != action.fileType:
            raise ValueError(f"Plan action file type does not match package manifest for {archive_path}.")
        if entry.sourceId != action.sourceId:
            raise ValueError(f"Plan action source ID does not match package manifest for {archive_path}.")
    return inspection.manifest


def _split_package_source(source_file: str) -> tuple[str, str]:
    if "::" not in source_file:
        raise ValueError(f"Package import source must use package::path format: {source_file}")
    package, archive_path = source_file.split("::", 1)
    if not archive_path:
        raise ValueError(f"Package import source is missing archive path: {source_file}")
    return package, archive_path


def _default_audit_path(backup_manifest: BackupManifest) -> Path:
    if backup_manifest.manifestPath:
        return Path(backup_manifest.manifestPath).parent / "package_import_execution_manifest.json"
    if backup_manifest.backupRoot and backup_manifest.timestamp:
        return Path(backup_manifest.backupRoot) / backup_manifest.timestamp / "package_import_execution_manifest.json"
    raise ValueError("Backup manifest must include manifestPath or backupRoot to write an execution audit manifest.")
