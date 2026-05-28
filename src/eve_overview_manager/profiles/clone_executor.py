"""Guarded clone executor for opaque EVE profile files."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from eve_overview_manager import __version__
from eve_overview_manager.models.profile import (
    BackupManifest,
    ClonePlan,
    ExecutionAuditEntry,
    ExecutionAuditManifest,
)
from eve_overview_manager.profiles.backup import verify_backup
from eve_overview_manager.services.checksums import sha256_file


def execute_clone(
    plan: ClonePlan,
    backup_manifest: BackupManifest,
    *,
    plan_path: str | None = None,
    audit_path: str | Path | None = None,
) -> ExecutionAuditManifest:
    _validate_clone_execution(plan, backup_manifest)
    audit_entries: list[ExecutionAuditEntry] = []
    for action in plan.actions:
        source = Path(action.sourceFile)
        target = Path(action.targetFile)
        source_sha256 = sha256_file(source)
        sha256_before = sha256_file(target) if target.exists() else None
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        audit_entries.append(
            ExecutionAuditEntry(
                action=action.action,
                sourceFile=action.sourceFile,
                targetFile=action.targetFile,
                sourceSha256=source_sha256,
                sha256Before=sha256_before,
                sha256After=sha256_file(target),
                bytesCopied=source.stat().st_size,
            )
        )
    resolved_audit_path = _default_audit_path(backup_manifest) if audit_path is None else Path(audit_path)
    manifest = ExecutionAuditManifest(
        operationId=plan.operationId,
        timestamp=datetime.now(timezone.utc).isoformat(),
        planPath=plan_path,
        backupManifestPath=backup_manifest.manifestPath,
        auditManifestPath=str(resolved_audit_path),
        actionsApplied=audit_entries,
        appVersion=__version__,
    )
    resolved_audit_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_audit_path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return manifest


def _validate_clone_execution(plan: ClonePlan, backup_manifest: BackupManifest) -> None:
    if plan.blocked:
        raise ValueError("Blocked clone plans cannot be executed.")
    if plan.summary.dryRun is not True:
        raise ValueError("Clone execution requires a reviewed dry-run plan.")
    if backup_manifest.operationId != plan.operationId:
        raise ValueError("Backup manifest operation ID does not match clone plan operation ID.")
    verification = verify_backup(backup_manifest)
    if not verification.ok:
        raise ValueError("; ".join(verification.errors))

    backed_up_targets = {entry.sourcePath for entry in backup_manifest.fileList}
    planned_targets = {action.targetFile for action in plan.actions}
    missing_backups = sorted(planned_targets - backed_up_targets)
    if missing_backups:
        raise ValueError(f"Backup manifest does not cover planned target files: {', '.join(missing_backups)}")

    for action in plan.actions:
        if action.action != "copy":
            raise ValueError(f"Unsupported clone action: {action.action}")
        if not Path(action.sourceFile).is_file():
            raise ValueError(f"Missing source file: {action.sourceFile}")


def _default_audit_path(backup_manifest: BackupManifest) -> Path:
    if backup_manifest.manifestPath:
        return Path(backup_manifest.manifestPath).parent / "execution_manifest.json"
    if backup_manifest.backupRoot and backup_manifest.timestamp:
        return Path(backup_manifest.backupRoot) / backup_manifest.timestamp / "execution_manifest.json"
    raise ValueError("Backup manifest must include manifestPath or backupRoot to write an execution audit manifest.")
