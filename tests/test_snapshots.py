from pathlib import Path

from eve_overview_manager.models.snapshot import SnapshotManifest
from eve_overview_manager.json_io.parser import load_overview_json
from eve_overview_manager.services.snapshots import create_overview_snapshot, list_snapshots, restore_snapshot, restore_snapshot_to_yaml, verify_snapshot
from eve_overview_manager.yaml_io.parser import load_overview_yaml


def test_create_overview_snapshot_writes_document_and_manifest(tmp_path):
    document = load_overview_yaml("Examples/Real-Overview.yaml")

    manifest = create_overview_snapshot(
        document,
        tmp_path,
        operation_type="import-yaml",
        source_path="Examples/Real-Overview.yaml",
        notes="test snapshot",
    )

    assert Path(manifest.documentPath).exists()
    assert Path(manifest.manifestPath).exists()
    assert len(manifest.sha256) == 64
    assert manifest.operationType == "import-yaml"
    assert manifest.sourcePath == "Examples/Real-Overview.yaml"
    assert manifest.notes == "test snapshot"


def test_verify_snapshot_passes_for_unchanged_document(tmp_path):
    manifest = create_overview_snapshot(load_overview_yaml("Examples/Real-Overview.yaml"), tmp_path, operation_type="import-yaml")

    assert verify_snapshot(manifest).ok is True


def test_verify_snapshot_fails_when_document_changes(tmp_path):
    manifest = create_overview_snapshot(load_overview_yaml("Examples/Real-Overview.yaml"), tmp_path, operation_type="import-yaml")
    Path(manifest.documentPath).write_text("changed", encoding="utf-8")

    result = verify_snapshot(manifest)

    assert result.ok is False
    assert "Checksum mismatch" in result.errors[0]


def test_snapshot_manifest_can_reload_from_disk(tmp_path):
    manifest = create_overview_snapshot(load_overview_yaml("Examples/Real-Overview.yaml"), tmp_path, operation_type="import-yaml")

    reloaded = SnapshotManifest.model_validate_json(Path(manifest.manifestPath).read_text(encoding="utf-8"))

    assert reloaded.snapshotId == manifest.snapshotId
    assert reloaded.sha256 == manifest.sha256


def test_list_snapshots_returns_newest_first(tmp_path):
    first = create_overview_snapshot(load_overview_yaml("Examples/Real-Overview.yaml"), tmp_path, operation_type="first")
    second = create_overview_snapshot(load_overview_yaml("Examples/Real-Overview.yaml"), tmp_path, operation_type="second")

    snapshots = list_snapshots(tmp_path)

    assert [snapshot.snapshotId for snapshot in snapshots] == [second.snapshotId, first.snapshotId]


def test_restore_snapshot_writes_canonical_json(tmp_path):
    manifest = create_overview_snapshot(load_overview_yaml("Examples/Real-Overview.yaml"), tmp_path / "snapshots", operation_type="import-yaml")
    output_path = tmp_path / "restored.json"

    restore_snapshot(manifest, output_path)

    restored = load_overview_json(output_path)
    assert len(restored.tabs) == 9


def test_restore_snapshot_refuses_overwrite_by_default(tmp_path):
    manifest = create_overview_snapshot(load_overview_yaml("Examples/Real-Overview.yaml"), tmp_path / "snapshots", operation_type="import-yaml")
    output_path = tmp_path / "restored.json"
    output_path.write_text("existing", encoding="utf-8")

    try:
        restore_snapshot(manifest, output_path)
    except FileExistsError:
        pass
    else:
        raise AssertionError("restore_snapshot should refuse overwrite by default")


def test_restore_snapshot_fails_when_checksum_changed(tmp_path):
    manifest = create_overview_snapshot(load_overview_yaml("Examples/Real-Overview.yaml"), tmp_path / "snapshots", operation_type="import-yaml")
    Path(manifest.documentPath).write_text("changed", encoding="utf-8")

    try:
        restore_snapshot(manifest, tmp_path / "restored.json")
    except ValueError as error:
        assert "Checksum mismatch" in str(error)
    else:
        raise AssertionError("restore_snapshot should fail when checksum verification fails")


def test_restore_snapshot_to_yaml_writes_valid_yaml(tmp_path):
    manifest = create_overview_snapshot(load_overview_yaml("Examples/Real-Overview.yaml"), tmp_path / "snapshots", operation_type="import-yaml")
    output_path = tmp_path / "restored.yaml"

    restore_snapshot_to_yaml(manifest, output_path)
    restored = load_overview_yaml(output_path)

    assert restored.meta.importWarnings == []
    assert len(restored.tabs) == 9


def test_restore_snapshot_to_yaml_refuses_overwrite_by_default(tmp_path):
    manifest = create_overview_snapshot(load_overview_yaml("Examples/Real-Overview.yaml"), tmp_path / "snapshots", operation_type="import-yaml")
    output_path = tmp_path / "restored.yaml"
    output_path.write_text("existing", encoding="utf-8")

    try:
        restore_snapshot_to_yaml(manifest, output_path)
    except FileExistsError:
        pass
    else:
        raise AssertionError("restore_snapshot_to_yaml should refuse overwrite by default")
