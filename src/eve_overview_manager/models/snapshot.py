"""Models for immutable overview document snapshots."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SnapshotManifest(BaseModel):
    snapshotId: str
    createdAt: str
    operationType: str
    sourcePath: str | None = None
    documentPath: str
    manifestPath: str
    sha256: str
    appVersion: str
    notes: str | None = None
    createdBy: str = "eve-overview-manager"


class SnapshotVerificationResult(BaseModel):
    ok: bool
    errors: list[str] = Field(default_factory=list)
