import json
from zipfile import ZIP_DEFLATED, ZipFile

from eve_overview_manager.profiles.package_exporter import export_profile_package, inspect_profile_package
from eve_overview_manager.profiles.scanner import scan_profile


def test_export_profile_package_contains_manifest_and_checksums(tmp_path):
    profile = tmp_path / "settings_Default"
    profile.mkdir()
    (profile / "core_char_100.dat").write_bytes(b"char-100")
    package = tmp_path / "profile.zip"

    manifest = export_profile_package(scan_profile(profile), package, snapshot_name="Known Good", notes="baseline")

    assert package.exists()
    assert manifest.snapshotName == "Known Good"
    assert manifest.notes == "baseline"
    assert len(manifest.fileList) == 1
    assert manifest.fileList[0].sha256
    with ZipFile(package) as archive:
        assert "manifest.json" in archive.namelist()
        assert "files/core_char_100.dat" in archive.namelist()


def test_inspect_profile_package_reports_checksum_mismatch(tmp_path):
    profile = tmp_path / "settings_Default"
    profile.mkdir()
    (profile / "core_char_100.dat").write_bytes(b"char-100")
    package = tmp_path / "profile.zip"
    export_profile_package(scan_profile(profile), package)
    corrupt_package = tmp_path / "corrupt.zip"

    with ZipFile(package) as source_archive, ZipFile(corrupt_package, "w", compression=ZIP_DEFLATED) as target_archive:
        manifest = json.loads(source_archive.read("manifest.json").decode("utf-8"))
        manifest["fileList"][0]["sha256"] = "0" * 64
        target_archive.writestr("manifest.json", json.dumps(manifest))
        target_archive.writestr("files/core_char_100.dat", source_archive.read("files/core_char_100.dat"))

    inspection = inspect_profile_package(corrupt_package)

    assert inspection.ok is False
    assert any("Checksum mismatch" in error for error in inspection.errors)
