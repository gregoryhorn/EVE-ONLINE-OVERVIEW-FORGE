"""Overview document snapshot helpers."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from eve_overview_manager import __version__
from eve_overview_manager.json_io.exporter import export_overview_json
from eve_overview_manager.json_io.parser import load_overview_json
from eve_overview_manager.models.overview import OverviewDocument
from eve_overview_manager.models.snapshot import SnapshotManifest, SnapshotVerificationResult
from eve_overview_manager.services.checksums import sha256_file
from eve_overview_manager.yaml_io.exporter import export_overview_yaml


def utc_timestamp() -> str:
    return datetime.now(UTC).isoformat()


def snapshot_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")


def create_overview_snapshot(
    document: OverviewDocument,
    snapshot_root: str | Path,
    *,
    operation_type: str,
    source_path: str | Path | None = None,
    notes: str | None = None,
) -> SnapshotManifest:
    snapshot_id = str(uuid4())
    timestamp = snapshot_timestamp()
    snapshot_dir = Path(snapshot_root) / f"{timestamp}_{snapshot_id}"
    snapshot_dir.mkdir(parents=True, exist_ok=False)

    document_path = snapshot_dir / "overview.json"
    manifest_path = snapshot_dir / "snapshot_manifest.json"
    export_overview_json(document, document_path)

    manifest = SnapshotManifest(
        snapshotId=snapshot_id,
        createdAt=timestamp,
        operationType=operation_type,
        sourcePath=str(source_path) if source_path is not None else None,
        documentPath=str(document_path),
        manifestPath=str(manifest_path),
        sha256=sha256_file(document_path),
        appVersion=__version__,
        notes=notes,
    )
    manifest_path.write_text(json.dumps(manifest.model_dump(), indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def verify_snapshot(manifest: SnapshotManifest) -> SnapshotVerificationResult:
    errors: list[str] = []
    document_path = Path(manifest.documentPath)
    if not document_path.exists():
        errors.append(f"Missing snapshot document: {document_path}")
    elif sha256_file(document_path) != manifest.sha256:
        errors.append(f"Checksum mismatch: {document_path}")
    return SnapshotVerificationResult(ok=not errors, errors=errors)


def list_snapshots(snapshot_root: str | Path) -> list[SnapshotManifest]:
    root = Path(snapshot_root)
    if not root.is_dir():
        return []
    manifests: list[tuple[str, SnapshotManifest]] = []
    for manifest_path in root.glob("*/snapshot_manifest.json"):
        try:
            manifests.append((manifest_path.parent.name, SnapshotManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))))
        except ValueError:
            continue
    return [manifest for _, manifest in sorted(manifests, key=lambda item: (item[1].createdAt, item[0]), reverse=True)]


def restore_snapshot(manifest: SnapshotManifest, output_path: str | Path, *, overwrite: bool = False) -> Path:
    verification = verify_snapshot(manifest)
    if not verification.ok:
        raise ValueError("; ".join(verification.errors))

    output = Path(output_path)
    if output.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(manifest.documentPath, output)
    return output


def restore_snapshot_to_yaml(manifest: SnapshotManifest, output_path: str | Path, *, overwrite: bool = False) -> Path:
    verification = verify_snapshot(manifest)
    if not verification.ok:
        raise ValueError("; ".join(verification.errors))

    output = Path(output_path)
    if output.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {output}")
    export_overview_yaml(load_overview_json(manifest.documentPath), output)
    return output
