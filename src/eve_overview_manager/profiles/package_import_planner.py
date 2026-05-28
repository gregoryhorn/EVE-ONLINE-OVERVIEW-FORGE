"""Dry-run import planning for portable profile packages."""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple
from uuid import uuid4

from eve_overview_manager.models.profile import CloneAction, ClonePlan, ClonePlanSummary, ProfileScanResult, ProfileTransferManifest
from eve_overview_manager.profiles.clone_planner import parse_cloneable_file
from eve_overview_manager.profiles.package_exporter import inspect_profile_package


def plan_profile_package_import(package_path: str | Path, destination_profile: ProfileScanResult) -> ClonePlan:
    inspection = inspect_profile_package(package_path)
    if not inspection.ok or inspection.manifest is None:
        return ClonePlan(
            operationId=str(uuid4()),
            source=str(Path(package_path)),
            target=destination_profile.profilePath,
            actions=[],
            warnings=inspection.errors or ["Package inspection failed."],
            blocked=True,
            summary=ClonePlanSummary(requiresBackup=True, dryRun=True),
        )
    return plan_profile_package_manifest_import(inspection.manifest, destination_profile)


def plan_profile_package_manifest_import(manifest: ProfileTransferManifest, destination_profile: ProfileScanResult) -> ClonePlan:
    destination_files = _destination_index(destination_profile)
    actions: list[CloneAction] = []
    warnings: list[str] = []
    missing_source_ids: list[str] = []
    missing_target_ids: list[str] = []
    blocked = False

    for entry in manifest.fileList:
        if entry.fileType not in {"core_user", "core_char", "prefs"}:
            warnings.append(f"Skipping unsupported package file type {entry.fileType!r}: {entry.fileName}")
            continue
        key = (entry.fileType, entry.sourceId or "")
        target = destination_files.get(key)
        if target is None:
            warnings.append(f"No destination {entry.fileType} file with identifier {entry.sourceId!r} for package file {entry.fileName}.")
            missing_target_ids.append(entry.sourceId or "")
            blocked = True
            continue
        actions.append(
            CloneAction(
                sourceFile=f"{manifest.packagePath or ''}::{entry.packagePath}",
                targetFile=target.path,
                fileType=entry.fileType,
                sourceId=entry.sourceId,
                targetId=entry.sourceId,
                sourceName=entry.characterName or _display_name(entry.fileType, entry.sourceId),
                targetName=target.display_name,
                risk="low" if entry.fileType == "prefs" else "medium",
                wouldOverwrite=Path(target.path).exists(),
            )
        )

    if not actions:
        warnings.append("No package import actions selected or available.")

    return ClonePlan(
        operationId=manifest.operationId or str(uuid4()),
        source=manifest.packagePath or manifest.sourceProfilePath,
        target=destination_profile.profilePath,
        actions=actions,
        warnings=warnings,
        blocked=blocked,
        summary=ClonePlanSummary(
            sourceFileCount=len(manifest.fileList),
            targetFileCount=len(destination_files),
            plannedActionCount=len(actions),
            missingSourceIds=missing_source_ids,
            missingTargetIds=missing_target_ids,
            requiresBackup=True,
            dryRun=True,
        ),
    )


class _DestinationFile(NamedTuple):
    path: str
    display_name: str | None


def _destination_index(profile: ProfileScanResult) -> dict[tuple[str, str], _DestinationFile]:
    index: dict[tuple[str, str], _DestinationFile] = {}
    character_names = {
        str(character.characterId): character.characterName
        for character in profile.characterFiles
        if character.characterId is not None and character.characterName
    }
    for path in [*profile.coreUserFiles, *profile.coreCharFiles, *profile.prefsFiles]:
        parsed = parse_cloneable_file(path)
        if parsed and parsed.identifier is not None:
            index[(parsed.file_type, parsed.identifier)] = _DestinationFile(
                path=parsed.path,
                display_name=character_names.get(parsed.identifier) or _display_name(parsed.file_type, parsed.identifier),
            )
    return index


def _display_name(file_type: str, identifier: str | None) -> str | None:
    if file_type == "core_char" and identifier:
        return f"Character {identifier}"
    if file_type == "core_user" and identifier:
        return f"Account/Profile {identifier}"
    if file_type == "prefs":
        return "prefs.ini"
    return None
