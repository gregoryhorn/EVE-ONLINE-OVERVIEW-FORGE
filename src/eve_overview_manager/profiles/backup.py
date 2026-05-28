"""Backup creation and verification for opaque profile files."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

from eve_overview_manager import __version__
from eve_overview_manager.models.profile import (
    BackupFileEntry,
    BackupManifest,
    ClonePlan,
    RollbackAuditEntry,
    RollbackAuditManifest,
    VerificationResult,
)
from eve_overview_manager.services.checksums import sha256_file


def create_backup(
    files: list[str | Path],
    backup_root: str | Path,
    *,
    source_path: str | Path,
    target_path: str | Path,
    operation_type: str = "backup-profile",
    operation_id: str | None = None,
) -> BackupManifest:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = Path(backup_root) / timestamp
    backup_dir.mkdir(parents=True, exist_ok=False)

    entries: list[BackupFileEntry] = []
    for file in files:
        source_file = Path(file)
        backup_file = backup_dir / source_file.name
        shutil.copy2(source_file, backup_file)
        entries.append(
            BackupFileEntry(
                sourcePath=str(source_file),
                backupPath=str(backup_file),
                sha256=sha256_file(backup_file),
                size=backup_file.stat().st_size,
            )
        )

    manifest = BackupManifest(
        sourcePath=str(source_path),
        targetPath=str(target_path),
        operationType=operation_type,
        timestamp=timestamp,
        fileList=entries,
        appVersion=__version__,
        backupRoot=str(backup_root),
        manifestPath=str(backup_dir / "backup_manifest.json"),
        operationId=operation_id,
    )
    manifest_path = Path(manifest.manifestPath)
    manifest_path.write_text(json.dumps(manifest.model_dump(), indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def create_backup_from_clone_plan(plan: ClonePlan, backup_root: str | Path) -> BackupManifest:
    target_files = list(dict.fromkeys(action.targetFile for action in plan.actions))
    return create_backup(
        target_files,
        backup_root,
        source_path=plan.source,
        target_path=plan.target,
        operation_type="clone-plan-backup",
        operation_id=plan.operationId,
    )


def verify_backup(manifest: BackupManifest) -> VerificationResult:
    errors: list[str] = []
    for entry in manifest.fileList:
        backup_file = Path(entry.backupPath)
        if not backup_file.exists():
            errors.append(f"Missing backup file: {backup_file}")
            continue
        if sha256_file(backup_file) != entry.sha256:
            errors.append(f"Checksum mismatch: {backup_file}")
    return VerificationResult(ok=not errors, errors=errors)


def rollback_backup(manifest: BackupManifest, *, audit_path: str | Path | None = None) -> RollbackAuditManifest:
    verification = verify_backup(manifest)
    if not verification.ok:
        raise ValueError("; ".join(verification.errors))

    resolved_audit_path = _default_rollback_audit_path(manifest) if audit_path is None else Path(audit_path)
    entries: list[RollbackAuditEntry] = []
    for file_entry in manifest.fileList:
        backup_file = Path(file_entry.backupPath)
        restored_file = Path(file_entry.sourcePath)
        sha256_before = sha256_file(restored_file) if restored_file.exists() else None
        restored_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup_file, restored_file)
        entries.append(
            RollbackAuditEntry(
                backupPath=file_entry.backupPath,
                restoredPath=file_entry.sourcePath,
                backupSha256=file_entry.sha256,
                sha256Before=sha256_before,
                sha256After=sha256_file(restored_file),
                bytesRestored=backup_file.stat().st_size,
            )
        )

    audit = RollbackAuditManifest(
        operationId=manifest.operationId,
        timestamp=datetime.now(UTC).isoformat(),
        backupManifestPath=manifest.manifestPath,
        auditManifestPath=str(resolved_audit_path),
        actionsApplied=entries,
        appVersion=__version__,
    )
    resolved_audit_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_audit_path.write_text(audit.model_dump_json(indent=2), encoding="utf-8")
    return audit


def _default_rollback_audit_path(manifest: BackupManifest) -> Path:
    if manifest.manifestPath:
        return Path(manifest.manifestPath).parent / "rollback_manifest.json"
    if manifest.backupRoot and manifest.timestamp:
        return Path(manifest.backupRoot) / manifest.timestamp / "rollback_manifest.json"
    raise ValueError("Backup manifest must include manifestPath or backupRoot to write a rollback audit manifest.")
