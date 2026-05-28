"""Optional ESI-backed character name resolution for profile reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable
from urllib.request import Request, urlopen

from eve_overview_manager.services.paths import default_cache_dir

ESI_NAMES_URL = "https://esi.evetech.net/latest/universe/names/?datasource=tranquility"


def resolve_character_names(
    character_ids: list[int],
    *,
    url: str = ESI_NAMES_URL,
    timeout: int = 15,
    cache_path: str | Path | None = None,
    fetcher: Callable[[list[int]], dict[int, str]] | None = None,
) -> dict[int, str]:
    ids = sorted(set(character_ids))
    if not ids:
        return {}
    resolved: dict[int, str] = {}
    path = _cache_path(cache_path)
    cache = _load_cache(path)
    for character_id in ids:
        cached_name = cache.get(str(character_id))
        if cached_name:
            resolved[character_id] = cached_name

    missing_ids = [character_id for character_id in ids if character_id not in resolved]
    if not missing_ids:
        return resolved
    fetched = fetcher(missing_ids) if fetcher else fetch_character_names(missing_ids, url=url, timeout=timeout)
    for character_id, name in fetched.items():
        resolved[character_id] = name
        cache[str(character_id)] = name
    _write_cache(path, cache)
    return resolved


def fetch_character_names(character_ids: list[int], *, url: str = ESI_NAMES_URL, timeout: int = 15) -> dict[int, str]:
    ids = sorted(set(character_ids))
    if not ids:
        return {}
    request = Request(
        url,
        data=json.dumps(ids).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "eve-overview-manager"},
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return {
        int(entry["id"]): str(entry["name"])
        for entry in payload
        if entry.get("category") == "character" and "id" in entry and "name" in entry
    }


def _cache_path(cache_path: str | Path | None) -> Path:
    if cache_path is not None:
        return Path(cache_path)
    return default_cache_dir() / "character_names.json"


def _load_cache(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    return {str(key): str(value) for key, value in data.items() if str(value)}


def _write_cache(path: Path, cache: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")
