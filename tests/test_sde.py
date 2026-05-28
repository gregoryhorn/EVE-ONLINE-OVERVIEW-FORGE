import json
import zipfile

from eve_overview_manager.validation.sde import (
    build_group_id_index,
    build_group_name_index,
    extract_group_ids_from_sde,
    extract_group_names_from_sde,
    load_group_names,
)


def test_extract_group_ids_from_jsonl_zip(tmp_path):
    archive = tmp_path / "sde.zip"
    with zipfile.ZipFile(archive, "w") as file:
        file.writestr("fsd/groups.jsonl", '{"_key": 25, "name": "Frigate"}\n{"groupID": 26}\n')

    assert extract_group_ids_from_sde(archive) == {25, 26}


def test_extract_group_ids_from_yaml_zip(tmp_path):
    archive = tmp_path / "sde.zip"
    with zipfile.ZipFile(archive, "w") as file:
        file.writestr("fsd/groupIDs.yaml", "25:\n  name: Frigate\n26:\n  name: Cruiser\n")

    assert extract_group_ids_from_sde(archive) == {25, 26}


def test_build_group_id_index_writes_json_array(tmp_path):
    archive = tmp_path / "sde.zip"
    output = tmp_path / "group_ids.json"
    with zipfile.ZipFile(archive, "w") as file:
        file.writestr("groups.jsonl", '{"id": 26}\n{"id": 25}\n')

    group_ids = build_group_id_index(archive, output)

    assert group_ids == {25, 26}
    assert json.loads(output.read_text(encoding="utf-8")) == [25, 26]


def test_extract_group_names_from_jsonl_zip(tmp_path):
    archive = tmp_path / "sde.zip"
    with zipfile.ZipFile(archive, "w") as file:
        file.writestr("fsd/groups.jsonl", '{"groupID": 25, "name": {"en": "Frigate"}}\n{"groupID": 26, "name": "Destroyer"}\n')

    assert extract_group_names_from_sde(archive) == {25: "Frigate", 26: "Destroyer"}


def test_build_group_name_index_writes_json_object(tmp_path):
    archive = tmp_path / "sde.zip"
    output = tmp_path / "group_names.json"
    with zipfile.ZipFile(archive, "w") as file:
        file.writestr("fsd/groupIDs.yaml", "25:\n  name:\n    en: Frigate\n26:\n  groupName: Destroyer\n")

    group_names = build_group_name_index(archive, output)

    assert group_names == {25: "Frigate", 26: "Destroyer"}
    assert json.loads(output.read_text(encoding="utf-8")) == {"25": "Frigate", "26": "Destroyer"}


def test_load_group_names_reads_json_object(tmp_path):
    path = tmp_path / "group_names.json"
    path.write_text('{"25": "Frigate", "bad": "Ignored", "26": 123}', encoding="utf-8")

    assert load_group_names(path) == {25: "Frigate"}
