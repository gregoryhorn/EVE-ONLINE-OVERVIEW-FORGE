"""Workspace project file helpers."""

from __future__ import annotations

from pathlib import Path

from eve_overview_manager import __version__
from eve_overview_manager.json_io.parser import load_overview_json
from eve_overview_manager.models.project import ProjectMeta, ProjectPaths, WorkspaceProject
from eve_overview_manager.services.snapshots import utc_timestamp
from eve_overview_manager.validation.engine import validate_overview
from eve_overview_manager.validation.group_validator import load_group_validator


def _relative_path(path: str | Path, base_dir: Path) -> str:
    path = Path(path)
    try:
        return str(path.resolve().relative_to(base_dir.resolve()))
    except ValueError:
        return str(path)


def create_project(
    project_path: str | Path,
    *,
    name: str,
    overview_document: str | Path,
    snapshot_root: str | Path | None = None,
    sde_archive: str | Path | None = None,
    group_index: str | Path | None = None,
    profile_roots: list[str | Path] | None = None,
    notes: str | None = None,
) -> WorkspaceProject:
    output_path = Path(project_path)
    project_dir = output_path.parent
    project = WorkspaceProject(
        meta=ProjectMeta(name=name, createdAt=utc_timestamp(), appVersion=__version__),
        paths=ProjectPaths(
            overviewDocument=_relative_path(overview_document, project_dir),
            snapshotRoot=_relative_path(snapshot_root, project_dir) if snapshot_root is not None else None,
            sdeArchive=_relative_path(sde_archive, project_dir) if sde_archive is not None else None,
            groupIndex=_relative_path(group_index, project_dir) if group_index is not None else None,
            profileRoots=[_relative_path(path, project_dir) for path in profile_roots or []],
        ),
        notes=notes,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(project.model_dump_json(indent=2), encoding="utf-8")
    return project


def load_project(project_path: str | Path) -> WorkspaceProject:
    return WorkspaceProject.model_validate_json(Path(project_path).read_text(encoding="utf-8"))


def resolve_project_path(project_path: str | Path, referenced_path: str) -> Path:
    path = Path(referenced_path)
    if path.is_absolute():
        return path
    return Path(project_path).parent / path


def validate_project(project_path: str | Path) -> list[str]:
    project = load_project(project_path)
    errors: list[str] = []
    overview_path = resolve_project_path(project_path, project.paths.overviewDocument)
    overview_exists = False
    if not overview_path.exists():
        errors.append(f"Missing overview document: {overview_path}")
    else:
        load_overview_json(overview_path)
        overview_exists = True

    if project.paths.snapshotRoot is not None:
        snapshot_root = resolve_project_path(project_path, project.paths.snapshotRoot)
        if not snapshot_root.exists():
            errors.append(f"Missing snapshot root: {snapshot_root}")

    if project.paths.sdeArchive is not None:
        sde_archive = resolve_project_path(project_path, project.paths.sdeArchive)
        if not sde_archive.exists():
            errors.append(f"Missing SDE archive: {sde_archive}")

    if project.paths.groupIndex is not None:
        group_index = resolve_project_path(project_path, project.paths.groupIndex)
        if not group_index.exists():
            errors.append(f"Missing group index: {group_index}")
        elif overview_exists:
            group_validator = load_group_validator(group_index)
            validation_results = validate_overview(load_overview_json(overview_path), group_validator=group_validator)
            errors.extend(
                f"{result.code}: {result.message} ({result.path})"
                for result in validation_results
                if result.severity == "error"
            )

    for profile_root in project.paths.profileRoots:
        resolved = resolve_project_path(project_path, profile_root)
        if not resolved.exists():
            errors.append(f"Missing profile root: {resolved}")
    return errors
