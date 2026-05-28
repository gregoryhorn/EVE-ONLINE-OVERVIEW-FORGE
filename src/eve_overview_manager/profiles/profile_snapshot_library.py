"""Profile package snapshot library helpers."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

from eve_overview_manager.models.profile import ProfileScanResult, ProfileSnapshotLibraryEntry, ProfileTransferManifest
from eve_overview_manager.profiles.package_exporter import export_profile_package, inspect_profile_package


def create_profile_snapshot_package(
    profile: ProfileScanResult,
    library_root: str | Path,
    *,
    snapshot_name: str,
    notes: str | None = None,
    include_core_user: bool = False,
    include_core_char: bool = True,
    include_prefs: bool = False,
) -> ProfileTransferManifest:
    root = Path(library_root)
    root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    package_path = _unique_package_path(root / f"{_slug(snapshot_name)}-{timestamp}.zip")
    return export_profile_package(
        profile,
        package_path,
        include_core_user=include_core_user,
        include_core_char=include_core_char,
        include_prefs=include_prefs,
        snapshot_name=snapshot_name,
        notes=notes,
    )


def list_profile_snapshots(library_root: str | Path) -> list[ProfileSnapshotLibraryEntry]:
    root = Path(library_root)
    if not root.exists():
        return []
    entries: list[ProfileSnapshotLibraryEntry] = []
    for package_path in sorted(root.glob("*.zip"), key=lambda path: path.stat().st_mtime, reverse=True):
        inspection = inspect_profile_package(package_path)
        manifest = inspection.manifest
        entries.append(
            ProfileSnapshotLibraryEntry(
                packagePath=str(package_path),
                ok=inspection.ok,
                snapshotName=manifest.snapshotName if manifest else None,
                notes=manifest.notes if manifest else None,
                timestamp=manifest.timestamp if manifest else None,
                fileCount=len(manifest.fileList) if manifest else 0,
                appVersion=manifest.appVersion if manifest else None,
                errors=inspection.errors,
            )
        )
    return entries


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-").lower()
    return slug or "profile-snapshot"


def _unique_package_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem}-{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(path)
