"""Input models for the optional modular overview generator."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from eve_overview_manager.models.overview import AppearanceConfig, ColumnsConfig, LabelsConfig, MiscConfig


class GeneratedPresetSpec(BaseModel):
    id: str
    name: str | None = None
    groups: list[int] = Field(default_factory=list)
    alwaysShownStates: list[int] = Field(default_factory=list)
    filteredStates: list[int] = Field(default_factory=list)


class GeneratedTabSpec(BaseModel):
    slot: int
    label: str
    overviewPresetRef: str | None = None
    bracketPresetRef: str | None = "_BracketFilterShowAll"
    colorARGB: str | None = None


class OverviewGeneratorSpec(BaseModel):
    schemaVersion: str = "codex-generator/v1"
    name: str | None = None
    tabs: list[GeneratedTabSpec] = Field(default_factory=list)
    presets: list[GeneratedPresetSpec] = Field(default_factory=list)
    appearance: AppearanceConfig = Field(default_factory=AppearanceConfig)
    columns: ColumnsConfig = Field(default_factory=ColumnsConfig)
    labels: LabelsConfig = Field(default_factory=LabelsConfig)
    misc: MiscConfig = Field(default_factory=MiscConfig)
    unknown: dict[str, Any] = Field(default_factory=dict)
