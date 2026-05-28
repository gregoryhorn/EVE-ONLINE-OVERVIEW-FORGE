"""Dry-run clone planning for opaque EVE profile files."""

from __future__ import annotations

from pathlib import Path
import re
from uuid import uuid4

from pydantic import BaseModel

from eve_overview_manager.models.profile import CloneAction, ClonePlan, ClonePlanSummary, ProfileScanResult

CORE_FILE_RE = re.compile(r"^(core_(?:user|char))_(.*)\.dat$")


class CloneOptions(BaseModel):
    copy_core_user: bool = False
    copy_core_char: bool = False
    copy_prefs: bool = False
    backup_required: bool = True
    overwrite_allowed: bool = False
    copy_first_to_all: bool = False


class CloneableFile(BaseModel):
    path: str
    file_type: str
    identifier: str | None
    parse_warning: str | None = None


def parse_cloneable_file(path: str | Path) -> CloneableFile | None:
    file_path = Path(path)
    if file_path.name == "prefs.ini":
        return CloneableFile(path=str(file_path), file_type="prefs", identifier="prefs")
    match = CORE_FILE_RE.match(file_path.name)
    if not match:
        return None
    file_type = match.group(1)
    identifier = match.group(2)
    warning = None
    if not identifier or set(identifier) == {"_"}:
        identifier = "__empty__"
        warning = f"{file_path.name} has an empty {file_type} identifier."
    elif not identifier.isdigit():
        warning = f"{file_path.name} has a non-numeric {file_type} identifier."
    return CloneableFile(path=str(file_path), file_type=file_type, identifier=identifier, parse_warning=warning)


def _parse_files(paths: list[str], file_type: str) -> tuple[list[CloneableFile], list[str]]:
    files: list[CloneableFile] = []
    warnings: list[str] = []
    for path in paths:
        parsed = parse_cloneable_file(path)
        if parsed is None:
            warnings.append(f"Skipping unrecognized {file_type} file: {path}")
            continue
        if parsed.file_type != file_type:
            warnings.append(f"Skipping incompatible file type for {file_type}: {path}")
            continue
        if parsed.parse_warning:
            warnings.append(parsed.parse_warning)
        files.append(parsed)
    return files, warnings


def _pair_actions(
    source_paths: list[str],
    target_paths: list[str],
    file_type: str,
    *,
    copy_first_to_all: bool,
) -> tuple[list[CloneAction], list[str], bool, list[str], list[str], int, int]:
    actions: list[CloneAction] = []
    warnings: list[str] = []
    missing_source_ids: list[str] = []
    missing_target_ids: list[str] = []
    blocked = False
    source_files, source_warnings = _parse_files(source_paths, file_type)
    target_files, target_warnings = _parse_files(target_paths, file_type)
    source_count = len(source_files)
    target_count = len(target_files)
    warnings.extend(source_warnings)
    warnings.extend(target_warnings)
    if not source_files:
        warnings.append(f"No source {file_type} files found.")
        missing_target_ids.extend([target.identifier or "" for target in target_files])
        return actions, warnings, blocked, missing_source_ids, missing_target_ids, source_count, target_count
    if not target_files:
        warnings.append(f"No target {file_type} files found.")
        missing_source_ids.extend([source.identifier or "" for source in source_files])
        missing_target_ids.extend([source.identifier or "" for source in source_files])
        return actions, warnings, True, missing_source_ids, missing_target_ids, source_count, target_count

    if copy_first_to_all:
        source = source_files[0]
        for target in target_files:
            actions.append(
                CloneAction(
                    sourceFile=source.path,
                    targetFile=target.path,
                    fileType=file_type,
                    sourceId=source.identifier,
                    targetId=target.identifier,
                    risk="low" if file_type == "prefs" else "medium",
                    wouldOverwrite=Path(target.path).exists(),
                )
            )
        unmatched_sources = source_files[1:]
        missing_source_ids.extend([source.identifier or "" for source in unmatched_sources])
        target_ids = {target.identifier for target in target_files}
        missing_target_ids.extend([source.identifier or "" for source in source_files if source.identifier not in target_ids])
        return actions, warnings, blocked, missing_source_ids, missing_target_ids, source_count, target_count

    source_by_id = {source.identifier: source for source in source_files}
    target_ids = {target.identifier for target in target_files}
    for target in target_files:
        source = source_by_id.get(target.identifier)
        if source is None:
            warnings.append(f"No source {file_type} file with identifier {target.identifier!r} for target {target.path}.")
            missing_source_ids.append(target.identifier or "")
            blocked = True
            continue
        actions.append(
            CloneAction(
                sourceFile=source.path,
                targetFile=target.path,
                fileType=file_type,
                sourceId=source.identifier,
                targetId=target.identifier,
                risk="low" if file_type == "prefs" else "medium",
                wouldOverwrite=Path(target.path).exists(),
            )
        )
    missing_target_ids.extend([source.identifier or "" for source in source_files if source.identifier not in target_ids])
    return actions, warnings, blocked, missing_source_ids, missing_target_ids, source_count, target_count


def plan_clone(source_profile: ProfileScanResult, target_profile: ProfileScanResult, options: CloneOptions) -> ClonePlan:
    actions: list[CloneAction] = []
    warnings: list[str] = []
    missing_source_ids: list[str] = []
    missing_target_ids: list[str] = []
    source_file_count = 0
    target_file_count = 0
    blocked = False
    if Path(source_profile.profilePath).resolve() == Path(target_profile.profilePath).resolve():
        warnings.append("Source and target profile paths are the same; this is a no-op self-clone plan.")

    if options.copy_core_user:
        new_actions, new_warnings, new_blocked, new_missing_source_ids, new_missing_target_ids, new_source_count, new_target_count = _pair_actions(
            source_profile.coreUserFiles,
            target_profile.coreUserFiles,
            "core_user",
            copy_first_to_all=options.copy_first_to_all,
        )
        actions.extend(new_actions)
        warnings.extend(new_warnings)
        missing_source_ids.extend(new_missing_source_ids)
        missing_target_ids.extend(new_missing_target_ids)
        source_file_count += new_source_count
        target_file_count += new_target_count
        blocked = blocked or new_blocked
    if options.copy_core_char:
        new_actions, new_warnings, new_blocked, new_missing_source_ids, new_missing_target_ids, new_source_count, new_target_count = _pair_actions(
            source_profile.coreCharFiles,
            target_profile.coreCharFiles,
            "core_char",
            copy_first_to_all=options.copy_first_to_all,
        )
        actions.extend(new_actions)
        warnings.extend(new_warnings)
        missing_source_ids.extend(new_missing_source_ids)
        missing_target_ids.extend(new_missing_target_ids)
        source_file_count += new_source_count
        target_file_count += new_target_count
        blocked = blocked or new_blocked
    if options.copy_prefs:
        new_actions, new_warnings, new_blocked, new_missing_source_ids, new_missing_target_ids, new_source_count, new_target_count = _pair_actions(
            source_profile.prefsFiles,
            target_profile.prefsFiles,
            "prefs",
            copy_first_to_all=False,
        )
        actions.extend(new_actions)
        warnings.extend(new_warnings)
        missing_source_ids.extend(new_missing_source_ids)
        missing_target_ids.extend(new_missing_target_ids)
        source_file_count += new_source_count
        target_file_count += new_target_count
        blocked = blocked or new_blocked

    if not actions:
        warnings.append("No clone actions selected or available.")

    return ClonePlan(
        operationId=str(uuid4()),
        source=str(Path(source_profile.profilePath)),
        target=str(Path(target_profile.profilePath)),
        actions=actions,
        warnings=warnings,
        blocked=blocked,
        summary=ClonePlanSummary(
            sourceFileCount=source_file_count,
            targetFileCount=target_file_count,
            plannedActionCount=len(actions),
            missingSourceIds=missing_source_ids,
            missingTargetIds=missing_target_ids,
            requiresBackup=options.backup_required,
            dryRun=True,
        ),
    )


def plan_character_clone(
    profile: ProfileScanResult,
    *,
    source_character_id: int,
    target_character_ids: list[int],
) -> ClonePlan:
    source_file = next((file for file in profile.characterFiles if file.characterId == source_character_id), None)
    target_files = [file for file in profile.characterFiles if file.characterId in set(target_character_ids)]
    missing_targets = [str(character_id) for character_id in target_character_ids if character_id not in {file.characterId for file in target_files}]
    warnings: list[str] = []
    blocked = False
    actions: list[CloneAction] = []

    if source_file is None:
        warnings.append(f"Source character file was not found: {source_character_id}")
        blocked = True
    if not target_character_ids:
        warnings.append("No destination characters selected.")
        blocked = True
    if source_character_id in target_character_ids:
        warnings.append("Source character was also selected as a destination; self-copy is skipped.")
    warnings.extend([f"Destination character file was not found: {character_id}" for character_id in missing_targets])
    blocked = blocked or bool(missing_targets)

    if source_file is not None:
        for target_file in target_files:
            if target_file.characterId == source_character_id:
                continue
            actions.append(
                CloneAction(
                    sourceFile=source_file.path,
                    targetFile=target_file.path,
                    fileType="core_char",
                    sourceId=str(source_character_id),
                    targetId=str(target_file.characterId) if target_file.characterId is not None else None,
                    risk="medium",
                    wouldOverwrite=Path(target_file.path).exists(),
                )
            )

    if not actions:
        warnings.append("No character clone actions selected or available.")

    return ClonePlan(
        operationId=str(uuid4()),
        source=str(Path(profile.profilePath)),
        target=str(Path(profile.profilePath)),
        actions=actions,
        warnings=warnings,
        blocked=blocked,
        summary=ClonePlanSummary(
            sourceFileCount=1 if source_file else 0,
            targetFileCount=len(target_files),
            plannedActionCount=len(actions),
            missingSourceIds=[] if source_file else [str(source_character_id)],
            missingTargetIds=missing_targets,
            requiresBackup=True,
            dryRun=True,
        ),
    )
