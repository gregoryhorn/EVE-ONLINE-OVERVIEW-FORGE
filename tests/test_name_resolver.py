import json

from eve_overview_manager.profiles.name_resolver import resolve_character_names


def test_resolve_character_names_uses_cache_for_known_ids(tmp_path):
    cache_path = tmp_path / "names.json"
    cache_path.write_text(json.dumps({"456": "Cached Pilot"}), encoding="utf-8")

    names = resolve_character_names(
        [456],
        cache_path=cache_path,
        fetcher=lambda ids: (_ for _ in ()).throw(AssertionError("fetcher should not be called")),
    )

    assert names == {456: "Cached Pilot"}


def test_resolve_character_names_fetches_missing_ids_and_updates_cache(tmp_path):
    cache_path = tmp_path / "names.json"

    names = resolve_character_names(
        [456, 789],
        cache_path=cache_path,
        fetcher=lambda ids: {character_id: f"Pilot {character_id}" for character_id in ids},
    )

    assert names == {456: "Pilot 456", 789: "Pilot 789"}
    assert json.loads(cache_path.read_text(encoding="utf-8")) == {
        "456": "Pilot 456",
        "789": "Pilot 789",
    }


def test_resolve_character_names_fetches_only_cache_misses(tmp_path):
    cache_path = tmp_path / "names.json"
    cache_path.write_text(json.dumps({"456": "Cached Pilot"}), encoding="utf-8")
    fetched_ids = []

    names = resolve_character_names(
        [456, 789],
        cache_path=cache_path,
        fetcher=lambda ids: fetched_ids.extend(ids) or {789: "Fetched Pilot"},
    )

    assert fetched_ids == [789]
    assert names == {456: "Cached Pilot", 789: "Fetched Pilot"}
