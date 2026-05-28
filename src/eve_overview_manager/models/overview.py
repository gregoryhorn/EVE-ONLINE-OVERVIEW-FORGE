"""Canonical overview document models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from eve_overview_manager.models.validation import ValidationResult


class OverviewMeta(BaseModel):
    sourceFormat: str = "eve-yaml"
    sourcePath: str | None = None
    generatedAt: str | None = None
    clientTabCap: int = 20
    compatibilityMode: Literal["current", "legacy"] = "current"
    topLevelKeyOrder: list[str] = Field(default_factory=list)
    importWarnings: list[ValidationResult] = Field(default_factory=list)


class TabBinding(BaseModel):
    slot: int
    label: str
    overviewPresetRef: str | None = None
    bracketPresetRef: str | None = None
    colorARGB: str | None = None
    unknown: dict[str, Any] = Field(default_factory=dict)
    fieldOrder: list[str] = Field(default_factory=list)


class Preset(BaseModel):
    id: str
    name: str
    groups: list[int | Any] = Field(default_factory=list)
    alwaysShownStates: list[int | Any] = Field(default_factory=list)
    filteredStates: list[int | Any] = Field(default_factory=list)
    fieldOrder: list[str] = Field(default_factory=list)


class AppearanceConfig(BaseModel):
    flagOrder: list[int | Any] = Field(default_factory=list)
    flagStates: list[int | Any] = Field(default_factory=list)
    backgroundOrder: list[int | Any] = Field(default_factory=list)
    backgroundStates: list[int | Any] = Field(default_factory=list)
    stateBlinks: dict[str, Any] = Field(default_factory=dict)
    stateColors: dict[str, Any] = Field(default_factory=dict)
    stateBlinksOrder: list[str] = Field(default_factory=list)
    stateColorsOrder: list[str] = Field(default_factory=list)
    unknown: dict[str, Any] = Field(default_factory=dict)


class ColumnsConfig(BaseModel):
    columnOrder: list[str] = Field(default_factory=list)
    enabled: list[str] = Field(default_factory=list)
    unknown: dict[str, Any] = Field(default_factory=dict)


class LabelsConfig(BaseModel):
    shipLabelOrder: list[Any] = Field(default_factory=list)
    shipLabels: dict[Any, Any] = Field(default_factory=dict)
    shipLabelsOrder: list[Any] = Field(default_factory=list)
    unknown: dict[str, Any] = Field(default_factory=dict)


class MiscConfig(BaseModel):
    userSettings: dict[str, Any] = Field(default_factory=dict)
    userSettingsOrder: list[str] = Field(default_factory=list)
    unknown: dict[str, Any] = Field(default_factory=dict)


class OverviewDocument(BaseModel):
    schemaVersion: str = "codex-overview/v1"
    meta: OverviewMeta = Field(default_factory=OverviewMeta)
    tabs: list[TabBinding] = Field(default_factory=list)
    presets: list[Preset] = Field(default_factory=list)
    appearance: AppearanceConfig = Field(default_factory=AppearanceConfig)
    columns: ColumnsConfig = Field(default_factory=ColumnsConfig)
    labels: LabelsConfig = Field(default_factory=LabelsConfig)
    misc: MiscConfig = Field(default_factory=MiscConfig)
    unknown: dict[str, Any] = Field(default_factory=dict)
