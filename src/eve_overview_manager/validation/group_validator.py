"""Group validation interfaces for future SDE-backed checks."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from typing import Protocol


class GroupValidator(Protocol):
    def is_known_group_id(self, group_id: int) -> bool:
        """Return whether an EVE group ID is known."""


class NoopGroupValidator:
    """Default validator used when no SDE data is configured."""

    def is_known_group_id(self, group_id: int) -> bool:
        return True


class InMemoryGroupValidator:
    def __init__(self, known_group_ids: set[int]) -> None:
        self.known_group_ids = known_group_ids

    def is_known_group_id(self, group_id: int) -> bool:
        return group_id in self.known_group_ids


def load_group_ids(path: str | Path) -> set[int]:
    text = Path(path).read_text(encoding="utf-8")
    stripped = text.lstrip()
    if not stripped:
        return set()
    if stripped.startswith("[") or stripped.startswith("{"):
        try:
            return _extract_group_ids_from_json(json.loads(text))
        except json.JSONDecodeError:
            return _extract_group_ids_from_lines(text)
    return _extract_group_ids_from_lines(text)


def load_group_validator(path: str | Path) -> InMemoryGroupValidator:
    return InMemoryGroupValidator(load_group_ids(path))


def _extract_group_ids_from_json(data: Any) -> set[int]:
    if isinstance(data, list):
        return {int(item) for item in data if isinstance(item, int) or (isinstance(item, str) and item.isdigit())}
    if isinstance(data, dict):
        if "groupIds" in data:
            return _extract_group_ids_from_json(data["groupIds"])
        if "groups" in data:
            return _extract_group_ids_from_json(data["groups"])
        return {int(key) for key in data if str(key).isdigit()}
    return set()


def _extract_group_ids_from_lines(text: str) -> set[int]:
    group_ids: set[int] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("{"):
            group_ids.update(_extract_group_ids_from_json(json.loads(line)))
            continue
        match = re.search(r"\d+", line)
        if match:
            group_ids.add(int(match.group(0)))
    return group_ids
