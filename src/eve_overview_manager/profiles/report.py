"""Read-only profile reporting for UI and CLI display."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Any

from eve_overview_manager.profiles.scanner import scan_profile
from eve_overview_manager.services.checksums import sha256_file


def build_profile_report(
    profile_path: str | Path,
    *,
    name_resolver: Callable[[list[int]], dict[int, str]] | None = None,
    include_checksums: bool = True,
) -> dict[str, Any]:
    profile = scan_profile(profile_path, name_resolver=name_resolver)
    files = []
    for path in profile.coreUserFiles:
        files.append(_file_report(Path(path), file_type="core_user", include_checksum=include_checksums))
    character_by_path = {character.path: character for character in profile.characterFiles}
    for path in profile.coreCharFiles:
        character = character_by_path.get(path)
        files.append(
            _file_report(
                Path(path),
                file_type="core_char",
                include_checksum=include_checksums,
                character_id=character.characterId if character else None,
                character_name=character.characterName if character else None,
            )
        )
    for path in profile.prefsFiles:
        files.append(_file_report(Path(path), file_type="prefs", include_checksum=include_checksums))

    return {
        "profilePath": profile.profilePath,
        "counts": {
            "coreUser": len(profile.coreUserFiles),
            "coreChar": len(profile.coreCharFiles),
            "prefs": len(profile.prefsFiles),
            "totalFiles": len(files),
        },
        "totalBytes": sum(file["size"] for file in files),
        "backupReady": bool(files) and not profile.warnings,
        "files": files,
        "warnings": profile.warnings,
    }


def _file_report(
    path: Path,
    *,
    file_type: str,
    include_checksum: bool,
    character_id: int | None = None,
    character_name: str | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "path": str(path),
        "name": path.name,
        "fileType": file_type,
        "size": path.stat().st_size,
        "lastModified": path.stat().st_mtime,
    }
    if character_id is not None:
        data["characterId"] = character_id
    if character_name is not None:
        data["characterName"] = character_name
    if include_checksum:
        data["sha256"] = sha256_file(path)
    return data
