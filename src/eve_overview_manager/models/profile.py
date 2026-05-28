"""Models for local EVE profile scanning, backup, and clone plans."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProfileScanResult(BaseModel):
    profilePath: str
    coreUserFiles: list[str] = Field(default_factory=list)
    coreCharFiles: list[str] = Field(default_factory=list)
    characterFiles: list["CharacterProfileFile"] = Field(default_factory=list)
    prefsFiles: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class CharacterProfileFile(BaseModel):
    path: str
    characterId: int | None = None
    characterName: str | None = None


class BackupFileEntry(BaseModel):
    sourcePath: str
    backupPath: str
    sha256: str
    size: int


class BackupManifest(BaseModel):
    sourcePath: str
    targetPath: str
    operationType: str
    timestamp: str
    fileList: list[BackupFileEntry] = Field(default_factory=list)
    appVersion: str
    backupRoot: str | None = None
    manifestPath: str | None = None
    operationId: str | None = None
    createdBy: str = "eve-overview-manager"


class VerificationResult(BaseModel):
    ok: bool
    errors: list[str] = Field(default_factory=list)


class ProfilePackageFileEntry(BaseModel):
    packagePath: str
    sourcePath: str
    fileName: str
    fileType: str
    sourceId: str | None = None
    characterId: int | None = None
    characterName: str | None = None
    sha256: str
    size: int


class ProfileTransferManifest(BaseModel):
    schemaVersion: str = "eve-profile-transfer/v1"
    operationId: str
    operationType: str = "profile-package-export"
    timestamp: str
    sourceProfilePath: str
    fileList: list[ProfilePackageFileEntry] = Field(default_factory=list)
    appVersion: str
    packagePath: str | None = None
    snapshotName: str | None = None
    notes: str | None = None
    createdBy: str = "eve-overview-manager"


class ProfilePackageInspection(BaseModel):
    ok: bool
    manifest: ProfileTransferManifest | None = None
    errors: list[str] = Field(default_factory=list)


class ProfileSnapshotLibraryEntry(BaseModel):
    packagePath: str
    ok: bool
    snapshotName: str | None = None
    notes: str | None = None
    timestamp: str | None = None
    fileCount: int = 0
    appVersion: str | None = None
    errors: list[str] = Field(default_factory=list)


class CloneAction(BaseModel):
    action: str = "copy"
    sourceFile: str
    targetFile: str
    fileType: str
    sourceId: str | None = None
    targetId: str | None = None
    sourceName: str | None = None
    targetName: str | None = None
    risk: str = "medium"
    wouldOverwrite: bool = True


class ClonePlanSummary(BaseModel):
    sourceFileCount: int = 0
    targetFileCount: int = 0
    plannedActionCount: int = 0
    missingSourceIds: list[str] = Field(default_factory=list)
    missingTargetIds: list[str] = Field(default_factory=list)
    requiresBackup: bool = True
    dryRun: bool = True


class ClonePlan(BaseModel):
    operationId: str
    source: str
    target: str
    actions: list[CloneAction] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocked: bool = False
    summary: ClonePlanSummary = Field(default_factory=ClonePlanSummary)


class ExecutionAuditEntry(BaseModel):
    action: str
    sourceFile: str
    targetFile: str
    sourceSha256: str
    sha256Before: str | None = None
    sha256After: str
    bytesCopied: int


class ExecutionAuditManifest(BaseModel):
    operationId: str
    timestamp: str
    planPath: str | None = None
    backupManifestPath: str | None = None
    auditManifestPath: str | None = None
    actionsApplied: list[ExecutionAuditEntry] = Field(default_factory=list)
    appVersion: str
    createdBy: str = "eve-overview-manager"


class RollbackAuditEntry(BaseModel):
    backupPath: str
    restoredPath: str
    backupSha256: str
    sha256Before: str | None = None
    sha256After: str
    bytesRestored: int


class RollbackAuditManifest(BaseModel):
    operationId: str | None = None
    timestamp: str
    backupManifestPath: str | None = None
    auditManifestPath: str | None = None
    actionsApplied: list[RollbackAuditEntry] = Field(default_factory=list)
    appVersion: str
    createdBy: str = "eve-overview-manager"
