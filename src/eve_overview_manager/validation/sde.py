"""Offline SDE group index builders."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from eve_overview_manager.validation.group_validator import load_group_ids


def build_group_id_index(sde_path: str | Path, output_path: str | Path) -> set[int]:
    group_ids = extract_group_ids_from_sde(sde_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(sorted(group_ids), indent=2), encoding="utf-8")
    return group_ids


def build_group_name_index(sde_path: str | Path, output_path: str | Path) -> dict[int, str]:
    group_names = extract_group_names_from_sde(sde_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({str(key): value for key, value in sorted(group_names.items())}, indent=2), encoding="utf-8")
    return group_names


def load_group_names(path: str | Path) -> dict[int, str]:
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        return {}
    return {int(key): value for key, value in data.items() if str(key).isdigit() and isinstance(value, str)}


def extract_group_names_from_sde(sde_path: str | Path) -> dict[int, str]:
    path = Path(sde_path)
    if path.is_dir():
        return _extract_group_names_from_directory(path)
    if path.suffix.lower() == ".zip":
        return _extract_group_names_from_zip(path)
    if path.suffix.lower() in {".json", ".jsonl"}:
        return _extract_group_names_from_json_text(path.read_text(encoding="utf-8-sig"))
    if path.suffix.lower() in {".yaml", ".yml"}:
        return _extract_group_names_from_yaml_text(path.read_text(encoding="utf-8-sig"))
    raise ValueError(f"Unsupported SDE input path: {path}")


def extract_group_ids_from_sde(sde_path: str | Path) -> set[int]:
    path = Path(sde_path)
    if path.is_dir():
        return _extract_group_ids_from_directory(path)
    if path.suffix.lower() == ".zip":
        return _extract_group_ids_from_zip(path)
    if path.suffix.lower() in {".json", ".jsonl", ".txt", ".csv"}:
        return load_group_ids(path)
    if path.suffix.lower() in {".yaml", ".yml"}:
        return _extract_group_ids_from_yaml(path)
    raise ValueError(f"Unsupported SDE input path: {path}")


def _extract_group_ids_from_directory(path: Path) -> set[int]:
    candidates = [
        *path.rglob("groups.jsonl"),
        *path.rglob("groupIDs.yaml"),
        *path.rglob("groupIDs.yml"),
        *path.rglob("invGroups.yaml"),
        *path.rglob("invGroups.yml"),
    ]
    if not candidates:
        raise ValueError(f"No supported group files found under: {path}")
    return extract_group_ids_from_sde(candidates[0])


def _extract_group_names_from_directory(path: Path) -> dict[int, str]:
    candidates = [
        *path.rglob("groups.jsonl"),
        *path.rglob("groupIDs.yaml"),
        *path.rglob("groupIDs.yml"),
        *path.rglob("invGroups.yaml"),
        *path.rglob("invGroups.yml"),
    ]
    if not candidates:
        raise ValueError(f"No supported group files found under: {path}")
    return extract_group_names_from_sde(candidates[0])


def _extract_group_ids_from_zip(path: Path) -> set[int]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        candidates = [
            name
            for name in names
            if name.endswith(("groups.jsonl", "groupIDs.yaml", "groupIDs.yml", "invGroups.yaml", "invGroups.yml"))
        ]
        if not candidates:
            raise ValueError(f"No supported group files found in SDE archive: {path}")
        name = candidates[0]
        with archive.open(name) as file:
            content = file.read().decode("utf-8-sig")
    if name.endswith(".jsonl"):
        return _extract_group_ids_from_jsonl_text(content)
    return _extract_group_ids_from_yaml_text(content)


def _extract_group_names_from_zip(path: Path) -> dict[int, str]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        candidates = [
            name
            for name in names
            if name.endswith(("groups.jsonl", "groupIDs.yaml", "groupIDs.yml", "invGroups.yaml", "invGroups.yml"))
        ]
        if not candidates:
            raise ValueError(f"No supported group files found in SDE archive: {path}")
        name = candidates[0]
        with archive.open(name) as file:
            content = file.read().decode("utf-8-sig")
    if name.endswith(".jsonl"):
        return _extract_group_names_from_json_text(content)
    return _extract_group_names_from_yaml_text(content)


def _extract_group_ids_from_jsonl_text(text: str) -> set[int]:
    group_ids: set[int] = set()
    for line in text.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        group_id = _group_id_from_json_record(record)
        if group_id is not None:
            group_ids.add(group_id)
    return group_ids


def _group_id_from_json_record(record: Any) -> int | None:
    if isinstance(record, int):
        return record
    if isinstance(record, dict):
        for key in ("groupID", "groupId", "id", "_key"):
            value = record.get(key)
            if isinstance(value, int):
                return value
            if isinstance(value, str) and value.isdigit():
                return int(value)
    return None


def _group_name_from_json_record(record: Any) -> str | None:
    if not isinstance(record, dict):
        return None
    for key in ("name", "groupName"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, dict):
            for language in ("en", "en-us", "en_US"):
                localized = value.get(language)
                if isinstance(localized, str) and localized.strip():
                    return localized.strip()
    return None


def _extract_group_names_from_json_text(text: str) -> dict[int, str]:
    stripped = text.lstrip()
    if not stripped:
        return {}
    if stripped.startswith("{"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
        if isinstance(data, dict):
            group_id = _group_id_from_json_record(data)
            name = _group_name_from_json_record(data)
            if group_id is not None and name:
                return {group_id: name}
            group_names: dict[int, str] = {}
            for key, value in data.items():
                if not str(key).isdigit():
                    continue
                if isinstance(value, str):
                    group_names[int(key)] = value
                else:
                    name = _group_name_from_json_record(value)
                    if name:
                        group_names[int(key)] = name
            return group_names
    records = []
    if stripped.startswith("["):
        records = json.loads(text)
    else:
        records = [json.loads(line) for line in text.splitlines() if line.strip()]
    group_names = {}
    for record in records:
        group_id = _group_id_from_json_record(record)
        name = _group_name_from_json_record(record)
        if group_id is not None and name:
            group_names[group_id] = name
    return group_names


def _extract_group_ids_from_yaml(path: Path) -> set[int]:
    return _extract_group_ids_from_yaml_text(path.read_text(encoding="utf-8-sig"))


def _extract_group_ids_from_yaml_text(text: str) -> set[int]:
    data = YAML(typ="safe").load(text) or {}
    if isinstance(data, dict):
        return {int(key) for key in data.keys() if isinstance(key, int) or str(key).isdigit()}
    if isinstance(data, list):
        group_ids: set[int] = set()
        for item in data:
            group_id = _group_id_from_json_record(item)
            if group_id is not None:
                group_ids.add(group_id)
        return group_ids
    return set()


def _extract_group_names_from_yaml_text(text: str) -> dict[int, str]:
    data = YAML(typ="safe").load(text) or {}
    if isinstance(data, dict):
        group_names: dict[int, str] = {}
        for key, value in data.items():
            if not (isinstance(key, int) or str(key).isdigit()):
                continue
            if isinstance(value, str):
                group_names[int(key)] = value
                continue
            name = _group_name_from_json_record(value)
            if name:
                group_names[int(key)] = name
        return group_names
    if isinstance(data, list):
        group_names = {}
        for item in data:
            group_id = _group_id_from_json_record(item)
            name = _group_name_from_json_record(item)
            if group_id is not None and name:
                group_names[group_id] = name
        return group_names
    return {}
