"""Offline tests for the Graph docs service taxonomy (fetch/parse/cache)."""

from __future__ import annotations

import json
from pathlib import Path

from generator.builders.resolution import TypeRegistry
from generator.documentation import subservices
from generator.filters import TypeFilter
from generator.odata.model import ODataModel
from generator.odata.type_information import TypeInformation
from generator.routing import Router, render_suggestions


def test_write_and_load_service_map(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(subservices, "_CACHE_PATH", tmp_path / "graph_services.json")

    assert subservices.load_service_map() == {}
    subservices.write_service_map({"user": "users", "alert": "security"})

    assert subservices.load_service_map() == {"alert": "security", "user": "users"}


def test_fetch_service_map_parses_resource_links(monkeypatch) -> None:
    def fake_get(url: str) -> str:
        if "/contents/" in url:
            return json.dumps([{"name": "users", "type": "dir"}, {"name": "README.md", "type": "file"}])
        return "- name: User\n  href: ../../resources/user.md\n- name: x\n  href: ../../api/user-get.md\n"

    monkeypatch.setattr(subservices, "_get", fake_get)

    assert subservices.fetch_service_map() == {"user": "users"}


def test_render_suggestions_prefers_the_service_taxonomy() -> None:
    model = ODataModel()
    model.add_type(
        TypeInformation(BaseTypeFullName="EntityType", FullName="microsoft.graph.Widget", IsValueObject=False)
    )

    suggestions = render_suggestions(
        model,
        TypeFilter(include_base_types=set()),
        TypeRegistry([]),
        Router(),
        services={"gadgets": "office365.gadgets"},
        service_map={"widget": "gadgets"},
    )

    assert '"Widget": office365.gadgets   # service: gadgets' in suggestions
