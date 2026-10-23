"""Offline tests for the migration map layer (:mod:`office365.migration.map`)."""

from __future__ import annotations

from office365.migration.map import ContentTypeMap


class _ContentType:
    def __init__(self, name, string_id):
        self.name = name
        self.string_id = string_id


def test_build_maps_differing_ids_by_name():
    source = [_ContentType("Item", "0x0100SOURCE"), _ContentType("Folder", "0x012000SAME")]
    target = [_ContentType("Item", "0x0100TARGET"), _ContentType("Folder", "0x012000SAME")]

    mapping = ContentTypeMap.build(source, target)

    # only the identifier that actually changed is stored
    assert mapping.entries == {"0x0100SOURCE": "0x0100TARGET"}


def test_resolve_passes_through_unmapped_identifiers():
    mapping = ContentTypeMap({"0x0100SOURCE": "0x0100TARGET"})

    assert mapping.resolve("0x0100SOURCE") == "0x0100TARGET"
    assert mapping.resolve("0x01") == "0x01"
    assert mapping.resolve(None) is None


def test_to_dict_round_trips():
    mapping = ContentTypeMap({"0x0100A": "0x0100B"})

    restored = ContentTypeMap.from_dict(mapping.to_dict())

    assert restored.entries == mapping.entries
    assert ContentTypeMap.from_dict({}).entries == {}
