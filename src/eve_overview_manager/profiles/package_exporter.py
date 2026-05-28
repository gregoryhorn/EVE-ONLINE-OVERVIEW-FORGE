"""Portable profile package export and inspection."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile

from eve_overview_manager import __version__
from eve_overview_manager.models.profile import (
    ProfilePackageFileEntry,
    ProfilePackageInspection,
    ProfileScanResult,
    ProfileTransferManifest,
)
from eve_overview_manager.profiles.clone_planner import parse_cloneable_file
from eve_overview_manager.services.checksums import sha256_file


def export_profile_package(
    profile: ProfileScanResult,
    package_path: str | Path,
    *,
    include_core_user: bool = False,
    include_core_char: bool = True,
    include_prefs: bool = False,
    snapshot_name: str | None = None,
    notes: str | None = None,
) -> ProfileTransferManifest:
    output_path = Path(package_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        raise FileExistsError(output_path)

    files = _selected_files(profile, include_core_user=include_core_user, include_core_char=include_core_char, include_prefs=include_prefs)
    character_by_path = {character.path: character for character in profile.characterFiles}
    entries = [_entry_for_file(path, profile=profile, character_by_path=character_by_path) for path in files]
    manifest = ProfileTransferManifest(
        operationId=str(uuid4()),
        timestamp=datetime.now(UTC).isoformat(),
        sourceProfilePath=profile.profilePath,
        fileList=entries,
        appVersion=__version__,
        packagePath=str(output_path),
        snapshotName=snapshot_name,
        notes=notes,
    )

    with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", manifest.model_dump_json(indent=2))
        for entry in entries:
            archive.write(Path(entry.sourcePath), entry.packagePath)
    return manifest


def inspect_profile_package(package_path: str | Path) -> ProfilePackageInspection:
    path = Path(package_path)
    errors: list[str] = []
    try:
        with ZipFile(path) as archive:
            if "manifest.json" not in archive.namelist():
                return ProfilePackageInspection(ok=False, errors=["Package is missing manifest.json."])
            manifest = ProfileTransferManifest.model_validate_json(archive.read("manifest.json").decode("utf-8"))
            manifest.packagePath = str(path)
            names = set(archive.namelist())
            for entry in manifest.fileList:
                if entry.packagePath not in names:
                    errors.append(f"Package is missing file: {entry.packagePath}")
                    continue
                with archive.open(entry.packagePath) as file:
                    import hashlib

                    digest = hashlib.sha256()
                    for chunk in iter(lambda: file.read(1024 * 1024), b""):
                        digest.update(chunk)
                if digest.hexdigest() != entry.sha256:
                    errors.append(f"Checksum mismatch: {entry.packagePath}")
            return ProfilePackageInspection(ok=not errors, manifest=manifest, errors=errors)
    except (OSError, BadZipFile, json.JSONDecodeError, ValueError) as error:
        return ProfilePackageInspection(ok=False, errors=[str(error)])


def _selected_files(
    profile: ProfileScanResult,
    *,
    include_core_user: bool,
    include_core_char: bool,
    include_prefs: bool,
) -> list[str]:
    files: list[str] = []
    if include_core_user:
        files.extend(profile.coreUserFiles)
    if include_core_char:
        files.extend(profile.coreCharFiles)
    if include_prefs:
        files.extend(profile.prefsFiles)
    return list(dict.fromkeys(files))


def _entry_for_file(
    path: str,
    *,
    profile: ProfileScanResult,
    character_by_path: dict[str, object],
) -> ProfilePackageFileEntry:
    file_path = Path(path)
    parsed = parse_cloneable_file(file_path)
    file_type = parsed.file_type if parsed else "unknown"
    source_id = parsed.identifier if parsed else None
    character = character_by_path.get(str(file_path))
    character_id = getattr(character, "characterId", None)
    character_name = getattr(character, "characterName", None)
    return ProfilePackageFileEntry(
        packagePath=f"files/{file_path.name}",
        sourcePath=str(file_path),
        fileName=file_path.name,
        fileType=file_type,
        sourceId=source_id,
        characterId=character_id,
        characterName=character_name,
        sha256=sha256_file(file_path),
        size=file_path.stat().st_size,
    )
