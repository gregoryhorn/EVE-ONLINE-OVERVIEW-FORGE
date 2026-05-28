from eve_overview_manager.profiles.report import build_profile_report


def test_profile_report_summarizes_cloneable_files(tmp_path):
    (tmp_path / "core_user_123.dat").write_bytes(b"user")
    (tmp_path / "core_char_456.dat").write_bytes(b"char")
    (tmp_path / "prefs.ini").write_bytes(b"[prefs]\n")

    report = build_profile_report(tmp_path, name_resolver=lambda ids: {456: "Pilot Name"})

    assert report["profilePath"] == str(tmp_path)
    assert report["counts"] == {"coreUser": 1, "coreChar": 1, "prefs": 1, "totalFiles": 3}
    assert report["totalBytes"] == len(b"user") + len(b"char") + len("[prefs]\n")
    assert report["backupReady"] is True
    assert {file["fileType"] for file in report["files"]} == {"core_user", "core_char", "prefs"}
    character_file = next(file for file in report["files"] if file["fileType"] == "core_char")
    assert character_file["characterId"] == 456
    assert character_file["characterName"] == "Pilot Name"
    assert len(character_file["sha256"]) == 64


def test_profile_report_can_skip_checksums(tmp_path):
    (tmp_path / "prefs.ini").write_text("[prefs]\n", encoding="utf-8")

    report = build_profile_report(tmp_path, include_checksums=False)

    assert "sha256" not in report["files"][0]
