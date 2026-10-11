"""Invariant tests for the placement contract (see generator/PLACEMENT.md).

These run against the real metadata for both services, so a violation (an
un-importable module, a file outside the output tree, a silently unrouted type)
fails fast.
"""

from __future__ import annotations

import keyword
from functools import lru_cache
from pathlib import Path

import pytest
from generator.builders.placement import Placement, TypePlanner
from generator.builders.resolution import TypeRegistry
from generator.config import GeneratorOptions
from generator.filters import TypeFilter
from generator.routing import Router, planned_module
from generator.services import get_service

_GENERATOR = Path(__file__).resolve().parents[2] / "generator"
_SERVICES = ["graph", "sharepoint"]


@lru_cache(maxsize=None)
def _placements(service: str) -> tuple[Path, tuple[tuple[str, str, Placement], ...]]:
    options = GeneratorOptions.load(service, _GENERATOR)
    model = get_service(service).reader(options.metadata_path).read()
    schema_filter = TypeFilter.from_options(options)
    registry = TypeRegistry(options.modules.split(","), namespace=options.namespace)
    router = Router.from_options(options.builder_context())
    planner = TypePlanner(options.builder_context(), registry)

    entries = []
    for name, schema in model.types.items():
        if not schema_filter.in_scope(name, schema):
            continue
        module = planned_module(name, schema, registry, router, options.output_path)
        placement = planner.plan(name, schema.BaseTypeFullName)
        entries.append((name, module or "", placement))
    return Path(options.output_path).resolve(), tuple(entries)


@pytest.mark.parametrize("service", _SERVICES)
def test_every_in_scope_type_is_placed(service: str) -> None:
    _root, entries = _placements(service)

    assert [name for name, module, _ in entries if not module] == []


@pytest.mark.parametrize("service", _SERVICES)
def test_planned_modules_are_importable(service: str) -> None:
    _root, entries = _placements(service)

    for name, module, _ in entries:
        segments = module.split(".")
        assert all(segment.isidentifier() and not keyword.iskeyword(segment) for segment in segments), (
            f"{name}: {module}"
        )


@pytest.mark.parametrize("service", _SERVICES)
def test_planned_files_are_within_the_output_root(service: str) -> None:
    root, entries = _placements(service)

    for name, _module, placement in entries:
        try:
            Path(placement.file).resolve().relative_to(root)
        except ValueError:  # pragma: no cover - only on a contract violation
            pytest.fail(f"{name}: {placement.file} is outside {root}")


@pytest.mark.parametrize("service", _SERVICES)
def test_attached_types_keep_an_existing_file(service: str) -> None:
    """Stickiness: an attached type is never a brand-new file."""
    _root, entries = _placements(service)

    for name, _module, placement in entries:
        if placement.is_attached:
            assert Path(placement.file).is_file(), name


def test_same_named_type_of_a_different_kind_is_not_resolved() -> None:
    """microsoft.graph.Endpoint (Entity) must not resolve to the callRecords Endpoint
    (ComplexType) - only the kind-matched one resolves."""
    options = GeneratorOptions.load("graph", _GENERATOR)
    registry = TypeRegistry(options.modules.split(","), namespace=options.namespace)

    assert registry.strict_module_for("microsoft.graph.Endpoint", "EntityType") is None
    assert registry.strict_module_for("microsoft.graph.callRecords.Endpoint", "ComplexType")
