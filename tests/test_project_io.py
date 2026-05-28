from pathlib import Path

from eve_overview_manager.json_io.exporter import export_overview_json
from eve_overview_manager.project_io.project import create_project, load_project, validate_project
from eve_overview_manager.yaml_io.parser import load_overview_yaml


def test_create_project_writes_workspace_file_with_relative_paths(tmp_path):
    overview_path = tmp_path / "overview.json"
    snapshot_root = tmp_path / "snapshots"
    profile_root = tmp_path / "settings_Default"
    snapshot_root.mkdir()
    profile_root.mkdir()
    export_overview_json(load_overview_yaml("Examples/Real-Overview.yaml"), overview_path)

    project = create_project(
        tmp_path / "workspace.eveoverview.json",
        name="Test Workspace",
        overview_document=overview_path,
        snapshot_root=snapshot_root,
        profile_roots=[profile_root],
        notes="test",
    )

    assert project.schemaVersion == "codex-project/v1"
    assert project.paths.overviewDocument == "overview.json"
    assert project.paths.snapshotRoot == "snapshots"
    assert project.paths.sdeArchive is None
    assert project.paths.groupIndex is None
    assert project.paths.profileRoots == ["settings_Default"]
    assert load_project(tmp_path / "workspace.eveoverview.json").meta.name == "Test Workspace"


def test_validate_project_passes_for_existing_references(tmp_path):
    overview_path = tmp_path / "overview.json"
    snapshot_root = tmp_path / "snapshots"
    snapshot_root.mkdir()
    export_overview_json(load_overview_yaml("Examples/Real-Overview.yaml"), overview_path)
    project_path = tmp_path / "workspace.eveoverview.json"
    create_project(project_path, name="Test", overview_document=overview_path, snapshot_root=snapshot_root)

    assert validate_project(project_path) == []


def test_validate_project_reports_missing_overview_document(tmp_path):
    project_path = tmp_path / "workspace.eveoverview.json"
    create_project(project_path, name="Test", overview_document=tmp_path / "missing.json")

    errors = validate_project(project_path)

    assert len(errors) == 1
    assert "Missing overview document" in errors[0]


def test_create_project_can_reference_sde_archive_and_group_index(tmp_path):
    overview_path = tmp_path / "overview.json"
    sde_archive = tmp_path / "sde.zip"
    group_index = tmp_path / "group_ids.json"
    export_overview_json(load_overview_yaml("Examples/Real-Overview.yaml"), overview_path)
    sde_archive.write_bytes(b"placeholder")
    group_index.write_text("[6, 10, 25, 26, 27, 28]", encoding="utf-8")

    project = create_project(
        tmp_path / "workspace.eveoverview.json",
        name="Test",
        overview_document=overview_path,
        sde_archive=sde_archive,
        group_index=group_index,
    )

    assert project.paths.sdeArchive == "sde.zip"
    assert project.paths.groupIndex == "group_ids.json"


def test_validate_project_reports_missing_sde_paths(tmp_path):
    overview_path = tmp_path / "overview.json"
    project_path = tmp_path / "workspace.eveoverview.json"
    export_overview_json(load_overview_yaml("Examples/Real-Overview.yaml"), overview_path)
    create_project(
        project_path,
        name="Test",
        overview_document=overview_path,
        sde_archive=tmp_path / "missing-sde.zip",
        group_index=tmp_path / "missing-groups.json",
    )

    errors = validate_project(project_path)

    assert any("Missing SDE archive" in error for error in errors)
    assert any("Missing group index" in error for error in errors)
