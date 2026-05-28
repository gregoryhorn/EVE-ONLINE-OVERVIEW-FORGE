"""Workspace/project file models for GUI and CLI workflows."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectMeta(BaseModel):
    name: str
    createdAt: str
    appVersion: str


class ProjectPaths(BaseModel):
    overviewDocument: str
    snapshotRoot: str | None = None
    sdeArchive: str | None = None
    groupIndex: str | None = None
    profileRoots: list[str] = Field(default_factory=list)


class WorkspaceProject(BaseModel):
    schemaVersion: str = "codex-project/v1"
    meta: ProjectMeta
    paths: ProjectPaths
    notes: str | None = None
