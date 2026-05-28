"""Profile scan/report/clone workflow routes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from eve_overview_manager.models.profile import BackupManifest, ClonePlan
from eve_overview_manager.profiles.name_resolver import resolve_character_names

router = APIRouter()


class ProfileScanRequest(BaseModel):
    rootPath: str
    resolveNames: bool = True


class ProfileReportRequest(BaseModel):
    profilePath: str
    resolveNames: bool = True
    includeChecksums: bool = False


class PlanCloneRequest(BaseModel):
    sourcePath: str
    targetPath: str
    copyCoreUser: bool = False
    copyCoreChar: bool = False
    copyPrefs: bool = False
    copyFirstToAll: bool = False
    resolveNames: bool = True


class PlanCharacterCloneRequest(BaseModel):
    profilePath: str
    sourceCharacterId: int
    targetCharacterIds: list[int]
    resolveNames: bool = True


class BackupPlanRequest(BaseModel):
    plan: dict[str, Any]
    backupRoot: str


class ExecuteCloneRequest(BaseModel):
    plan: dict[str, Any]
    backupManifest: dict[str, Any]


class RollbackBackupRequest(BaseModel):
    backupManifest: dict[str, Any]


class ExportPackageRequest(BaseModel):
    profilePath: str
    packagePath: str
    includeCoreUser: bool = False
    includeCoreChar: bool = True
    includePrefs: bool = False
    snapshotName: str | None = None
    notes: str | None = None


class InspectPackageRequest(BaseModel):
    packagePath: str


class PlanPackageImportRequest(BaseModel):
    packagePath: str
    destinationProfilePath: str
    resolveNames: bool = True


class ExecutePackageImportRequest(BaseModel):
    plan: dict[str, Any]
    backupManifest: dict[str, Any]
    packagePath: str | None = None


class SaveProfileSnapshotRequest(BaseModel):
    profilePath: str
    libraryRoot: str
    snapshotName: str
    notes: str | None = None
    includeCoreUser: bool = False
    includeCoreChar: bool = True
    includePrefs: bool = False


class ListProfileSnapshotsRequest(BaseModel):
    libraryRoot: str


@router.post("/profiles/scan")
def scan_profiles_route(request: ProfileScanRequest):
    from eve_overview_manager.profiles.scanner import scan_profiles

    name_resolver = resolve_character_names if request.resolveNames else None
    profiles = [profile.model_dump() for profile in scan_profiles(Path(request.rootPath), name_resolver=name_resolver)]
    return JSONResponse({"rootPath": request.rootPath, "profiles": profiles})


@router.get("/profiles/default-root")
def default_profile_root_route():
    from eve_overview_manager.services.paths import default_profile_root

    path = default_profile_root()
    return JSONResponse({"profileRoot": str(path) if path else ""})


@router.post("/profiles/report")
def profile_report_route(request: ProfileReportRequest):
    from eve_overview_manager.profiles.report import build_profile_report

    name_resolver = resolve_character_names if request.resolveNames else None
    report = build_profile_report(
        Path(request.profilePath),
        name_resolver=name_resolver,
        include_checksums=request.includeChecksums,
    )
    return JSONResponse({"report": report})


@router.post("/profiles/plan-clone")
def plan_clone_route(request: PlanCloneRequest):
    from eve_overview_manager.profiles.clone_planner import CloneOptions, plan_clone
    from eve_overview_manager.profiles.scanner import scan_profile

    name_resolver = resolve_character_names if request.resolveNames else None
    plan = plan_clone(
        scan_profile(Path(request.sourcePath), name_resolver=name_resolver),
        scan_profile(Path(request.targetPath), name_resolver=name_resolver),
        CloneOptions(
            copy_core_user=request.copyCoreUser,
            copy_core_char=request.copyCoreChar,
            copy_prefs=request.copyPrefs,
            copy_first_to_all=request.copyFirstToAll,
        ),
    )
    return JSONResponse({"plan": plan.model_dump()})


@router.post("/profiles/plan-character-clone")
def plan_character_clone_route(request: PlanCharacterCloneRequest):
    from eve_overview_manager.profiles.clone_planner import plan_character_clone
    from eve_overview_manager.profiles.scanner import scan_profile

    name_resolver = resolve_character_names if request.resolveNames else None
    plan = plan_character_clone(
        scan_profile(Path(request.profilePath), name_resolver=name_resolver),
        source_character_id=request.sourceCharacterId,
        target_character_ids=request.targetCharacterIds,
    )
    return JSONResponse({"plan": plan.model_dump()})


@router.post("/profiles/backup-plan")
def backup_plan_route(request: BackupPlanRequest):
    from eve_overview_manager.profiles.backup import create_backup_from_clone_plan

    plan = ClonePlan.model_validate(request.plan)
    manifest = create_backup_from_clone_plan(plan, Path(request.backupRoot))
    return JSONResponse({"backupManifest": manifest.model_dump()})


@router.post("/profiles/execute-clone")
def execute_clone_route(request: ExecuteCloneRequest):
    from eve_overview_manager.profiles.clone_executor import execute_clone

    try:
        audit = execute_clone(
            ClonePlan.model_validate(request.plan),
            BackupManifest.model_validate(request.backupManifest),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return JSONResponse({"executionAudit": audit.model_dump()})


@router.post("/profiles/rollback-backup")
def rollback_backup_route(request: RollbackBackupRequest):
    from eve_overview_manager.profiles.backup import rollback_backup

    try:
        audit = rollback_backup(BackupManifest.model_validate(request.backupManifest))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return JSONResponse({"rollbackAudit": audit.model_dump()})


@router.post("/profiles/package/export")
def export_profile_package_route(request: ExportPackageRequest):
    from eve_overview_manager.profiles.package_exporter import export_profile_package
    from eve_overview_manager.profiles.scanner import scan_profile

    manifest = export_profile_package(
        scan_profile(Path(request.profilePath)),
        Path(request.packagePath),
        include_core_user=request.includeCoreUser,
        include_core_char=request.includeCoreChar,
        include_prefs=request.includePrefs,
        snapshot_name=request.snapshotName,
        notes=request.notes,
    )
    return JSONResponse({"manifest": manifest.model_dump()})


@router.post("/profiles/package/inspect")
def inspect_profile_package_route(request: InspectPackageRequest):
    from eve_overview_manager.profiles.package_exporter import inspect_profile_package

    inspection = inspect_profile_package(Path(request.packagePath))
    return JSONResponse({"inspection": inspection.model_dump()})


@router.post("/profiles/package/plan-import")
def plan_profile_package_import_route(request: PlanPackageImportRequest):
    from eve_overview_manager.profiles.package_import_planner import plan_profile_package_import
    from eve_overview_manager.profiles.scanner import scan_profile

    name_resolver = resolve_character_names if request.resolveNames else None
    plan = plan_profile_package_import(
        Path(request.packagePath),
        scan_profile(Path(request.destinationProfilePath), name_resolver=name_resolver),
    )
    return JSONResponse({"plan": plan.model_dump()})


@router.post("/profiles/package/execute-import")
def execute_profile_package_import_route(request: ExecutePackageImportRequest):
    from eve_overview_manager.profiles.package_import_executor import execute_profile_package_import

    try:
        audit = execute_profile_package_import(
            ClonePlan.model_validate(request.plan),
            BackupManifest.model_validate(request.backupManifest),
            package_path=Path(request.packagePath) if request.packagePath else None,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return JSONResponse({"executionAudit": audit.model_dump()})


@router.post("/profiles/snapshots/save")
def save_profile_snapshot_route(request: SaveProfileSnapshotRequest):
    from eve_overview_manager.profiles.profile_snapshot_library import create_profile_snapshot_package
    from eve_overview_manager.profiles.scanner import scan_profile

    manifest = create_profile_snapshot_package(
        scan_profile(Path(request.profilePath)),
        Path(request.libraryRoot),
        snapshot_name=request.snapshotName,
        notes=request.notes,
        include_core_user=request.includeCoreUser,
        include_core_char=request.includeCoreChar,
        include_prefs=request.includePrefs,
    )
    return JSONResponse({"manifest": manifest.model_dump()})


@router.post("/profiles/snapshots/list")
def list_profile_snapshots_route(request: ListProfileSnapshotsRequest):
    from eve_overview_manager.profiles.profile_snapshot_library import list_profile_snapshots

    entries = [entry.model_dump() for entry in list_profile_snapshots(Path(request.libraryRoot))]
    return JSONResponse({"libraryRoot": request.libraryRoot, "snapshots": entries})
