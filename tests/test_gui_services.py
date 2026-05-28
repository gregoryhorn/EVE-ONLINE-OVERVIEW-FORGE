from pathlib import Path

from eve_overview_manager.services.filenames import unique_output_path
from eve_overview_manager.services.preferences import load_gui_preferences, remember_group_names_path, remember_import_export_folder


def test_gui_preferences_default_to_user_documents_overview(monkeypatch, tmp_path):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    preferences = load_gui_preferences(tmp_path / "missing.json")

    assert preferences.importExportFolder == str(tmp_path / "Documents" / "EVE" / "Overview")


def test_gui_preferences_remember_import_export_folder(tmp_path):
    preferences_path = tmp_path / "preferences.json"
    selected_folder = tmp_path / "Custom Overview Folder"

    remember_import_export_folder(selected_folder, path=preferences_path)
    preferences = load_gui_preferences(preferences_path)

    assert preferences.importExportFolder == str(selected_folder)


def test_gui_preferences_remember_group_names_path_preserves_folder(tmp_path):
    preferences_path = tmp_path / "preferences.json"
    selected_folder = tmp_path / "Custom Overview Folder"
    group_names = tmp_path / "group_names.json"

    remember_import_export_folder(selected_folder, path=preferences_path)
    remember_group_names_path(group_names, path=preferences_path)
    preferences = load_gui_preferences(preferences_path)

    assert preferences.importExportFolder == str(selected_folder)
    assert preferences.groupNamesPath == str(group_names)


def test_unique_output_path_returns_original_when_missing(tmp_path):
    output = tmp_path / "overview.yaml"

    assert unique_output_path(output) == output


def test_unique_output_path_adds_increment_when_file_exists(tmp_path):
    (tmp_path / "overview.yaml").write_text("existing", encoding="utf-8")
    (tmp_path / "overview_2.yaml").write_text("existing", encoding="utf-8")

    assert unique_output_path(tmp_path / "overview.yaml") == tmp_path / "overview_3.yaml"


def test_unique_output_path_handles_files_without_suffix(tmp_path):
    (tmp_path / "overview").write_text("existing", encoding="utf-8")

    assert unique_output_path(tmp_path / "overview") == tmp_path / "overview_2"
