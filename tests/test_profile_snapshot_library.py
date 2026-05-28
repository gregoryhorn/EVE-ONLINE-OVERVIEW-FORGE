from eve_overview_manager.profiles.profile_snapshot_library import create_profile_snapshot_package, list_profile_snapshots
from eve_overview_manager.profiles.scanner import scan_profile


def test_profile_snapshot_library_saves_and_lists_verified_packages(tmp_path):
    profile = tmp_path / "settings_Default"
    library = tmp_path / "library"
    profile.mkdir()
    (profile / "core_char_100.dat").write_bytes(b"char-100")

    manifest = create_profile_snapshot_package(
        scan_profile(profile),
        library,
        snapshot_name="Known Good",
        notes="before testing",
    )
    entries = list_profile_snapshots(library)

    assert len(entries) == 1
    assert entries[0].packagePath == manifest.packagePath
    assert entries[0].ok is True
    assert entries[0].snapshotName == "Known Good"
    assert entries[0].notes == "before testing"
    assert entries[0].fileCount == 1


def test_profile_snapshot_library_reports_corrupt_packages(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    (library / "broken.zip").write_text("not a zip", encoding="utf-8")

    entries = list_profile_snapshots(library)

    assert len(entries) == 1
    assert entries[0].ok is False
    assert entries[0].errors
