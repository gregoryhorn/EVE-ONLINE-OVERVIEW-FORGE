"""Build canonical overview documents from simple generator specs."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from eve_overview_manager.models.generator import OverviewGeneratorSpec
from eve_overview_manager.models.overview import OverviewDocument, OverviewMeta, Preset, TabBinding


def load_generator_spec(path: str | Path) -> OverviewGeneratorSpec:
    return OverviewGeneratorSpec.model_validate_json(Path(path).read_text(encoding="utf-8"))


def build_overview_document(spec: OverviewGeneratorSpec) -> OverviewDocument:
    document = OverviewDocument(
        meta=OverviewMeta(
            sourceFormat="codex-generator",
            generatedAt=datetime.now(UTC).isoformat(),
            topLevelKeyOrder=[
                "tabSetup",
                "presets",
                "columnOrder",
                "overviewColumns",
                "stateBlinks",
                "stateColorsNameList",
                "shipLabels",
                "userSettings",
            ],
        ),
        tabs=[
            TabBinding(
                slot=tab.slot,
                label=tab.label,
                overviewPresetRef=tab.overviewPresetRef,
                bracketPresetRef=tab.bracketPresetRef,
                colorARGB=tab.colorARGB,
            )
            for tab in spec.tabs
        ],
        presets=[
            Preset(
                id=preset.id,
                name=preset.name or preset.id,
                groups=preset.groups,
                alwaysShownStates=preset.alwaysShownStates,
                filteredStates=preset.filteredStates,
            )
            for preset in spec.presets
        ],
        appearance=spec.appearance,
        columns=spec.columns,
        labels=spec.labels,
        misc=spec.misc,
        unknown=spec.unknown,
    )
    return document
