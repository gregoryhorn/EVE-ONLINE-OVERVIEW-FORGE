from pathlib import Path

from eve_overview_manager.profiles.scanner import scan_profile, scan_profiles


def test_profile_scanner_finds_mock_core_files(tmp_path):
    (tmp_path / "core_user_123.dat").write_bytes(b"user")
    (tmp_path / "core_char_456.dat").write_bytes(b"char")
    (tmp_path / "prefs.ini").write_text("[prefs]\n", encoding="utf-8")

    result = scan_profile(tmp_path)

    assert len(result.coreUserFiles) == 1
    assert len(result.coreCharFiles) == 1
    assert result.characterFiles[0].characterId == 456
    assert result.characterFiles[0].characterName is None
    assert len(result.prefsFiles) == 1


def test_profile_scanner_ignores_dat_backup_files(tmp_path):
    (tmp_path / "core_user_123.dat").write_bytes(b"user")
    (tmp_path / "core_user_123.dat.bak").write_bytes(b"backup")
    (tmp_path / "core_char_456.dat").write_bytes(b"char")
    (tmp_path / "core_char_456.dat.bak").write_bytes(b"backup")

    result = scan_profile(tmp_path)

    assert result.coreUserFiles == [str(tmp_path / "core_user_123.dat")]
    assert result.coreCharFiles == [str(tmp_path / "core_char_456.dat")]


def test_scan_profiles_finds_settings_directories_under_eve_root(tmp_path):
    eve_root = tmp_path / "c_ccp_eve_tq_tranquility"
    settings_default = eve_root / "settings_Default"
    settings_backup = eve_root / "settings_Default.bak_20260221_102953"
    cache = eve_root / "cache"
    settings_default.mkdir(parents=True)
    settings_backup.mkdir()
    cache.mkdir()
    (settings_default / "core_user_123.dat").write_bytes(b"user")
    (settings_default / "prefs.ini").write_text("[prefs]\n", encoding="utf-8")
    (settings_backup / "core_user_456.dat").write_bytes(b"backup")
    (cache / "core_user_999.dat").write_bytes(b"ignored")

    profiles = scan_profiles(eve_root)

    assert [Path(profile.profilePath).name for profile in profiles] == ["settings_Default"]


def test_profile_scanner_resolves_character_names_when_resolver_is_provided(tmp_path):
    (tmp_path / "core_char_456.dat").write_bytes(b"char")
    (tmp_path / "core_char__.dat").write_bytes(b"placeholder")

    result = scan_profile(tmp_path, name_resolver=lambda ids: {456: "Pilot Name"})

    assert result.characterFiles[0].characterId == 456
    assert result.characterFiles[0].characterName == "Pilot Name"
    assert result.characterFiles[1].characterId is None
    assert result.characterFiles[1].characterName is None
