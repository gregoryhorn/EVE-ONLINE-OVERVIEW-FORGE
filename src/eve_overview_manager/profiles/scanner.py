"""Profile scanner for local EVE settings folders."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from eve_overview_manager.models.profile import CharacterProfileFile, ProfileScanResult


def scan_profile(profile_path: str | Path, *, name_resolver: Callable[[list[int]], dict[int, str]] | None = None) -> ProfileScanResult:
    path = Path(profile_path)
    warnings: list[str] = []
    if not path.exists():
        warnings.append("Profile path does not exist.")
    if not path.is_dir():
        warnings.append("Profile path is not a directory.")
    files = list(path.iterdir()) if path.is_dir() else []
    core_char_files = [str(file) for file in files if file.is_file() and file.name.startswith("core_char_") and file.name.endswith(".dat")]
    character_files = _character_files(core_char_files, name_resolver=name_resolver)
    return ProfileScanResult(
        profilePath=str(path),
        coreUserFiles=[str(file) for file in files if file.is_file() and file.name.startswith("core_user_") and file.name.endswith(".dat")],
        coreCharFiles=core_char_files,
        characterFiles=character_files,
        prefsFiles=[str(file) for file in files if file.is_file() and file.name == "prefs.ini"],
        warnings=warnings,
    )


def scan_profiles(root_path: str | Path, *, name_resolver: Callable[[list[int]], dict[int, str]] | None = None) -> list[ProfileScanResult]:
    root = Path(root_path)
    if not root.is_dir():
        return [scan_profile(root, name_resolver=name_resolver)]
    profiles: list[ProfileScanResult] = []
    candidate_dirs = [
        root,
        *[
            child
            for child in root.iterdir()
            if child.is_dir() and child.name.startswith("settings_") and ".bak_" not in child.name
        ],
    ]
    for path in candidate_dirs:
        result = scan_profile(path, name_resolver=name_resolver)
        if result.coreUserFiles or result.coreCharFiles or result.prefsFiles or result.warnings:
            profiles.append(result)
    return profiles


def _character_files(core_char_files: list[str], *, name_resolver: Callable[[list[int]], dict[int, str]] | None) -> list[CharacterProfileFile]:
    ids = [_parse_character_id(file_path) for file_path in core_char_files]
    resolvable_ids = [character_id for character_id in ids if character_id is not None]
    names = name_resolver(resolvable_ids) if name_resolver and resolvable_ids else {}
    return [
        CharacterProfileFile(
            path=file_path,
            characterId=character_id,
            characterName=names.get(character_id) if character_id is not None else None,
        )
        for file_path, character_id in zip(core_char_files, ids, strict=True)
    ]


def _parse_character_id(file_path: str | Path) -> int | None:
    name = Path(file_path).name
    prefix = "core_char_"
    suffix = ".dat"
    if not name.startswith(prefix) or not name.endswith(suffix):
        return None
    value = name.removeprefix(prefix).removesuffix(suffix)
    return int(value) if value.isdecimal() else None
