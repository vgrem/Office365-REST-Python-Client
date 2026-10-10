"""Offline tests for the typed, immutable BuilderContext."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest
from generator.builders.context import BuilderContext


def test_from_options_normalizes_legacy_dict() -> None:
    options = {
        "template_path": "/t",
        "output_path": "/o",
        "modules": "office365",
        "namespace": "SP",
        "generate_methods": "true",
        "ignored_properties": ["A"],
        "ignored_methods": ["B"],
        "routing_SP": "office365.sharepoint",
        "type_routing": {"Edu*": "office365.education"},
        "known_types": ["SP.Foo"],
        "type_modules": {"SP.Foo": "office365.foo"},
        "cyclic_types": ["SP.Bar"],
        "enum_defaults": {"SP.E": "a"},
    }

    context = BuilderContext.from_options(options)

    assert context.template_path == "/t"
    assert context.output_path == "/o"
    assert context.routing == {"SP": "office365.sharepoint"}
    assert context.type_routing == {"Edu*": "office365.education"}
    assert context.known_types == frozenset({"SP.Foo"})
    assert context.type_modules == {"SP.Foo": "office365.foo"}
    assert context.cyclic_types == frozenset({"SP.Bar"})
    assert context.enum_defaults == {"SP.E": "a"}
    assert context.methods_enabled is True


def test_from_options_is_idempotent() -> None:
    context = BuilderContext(template_path="/t", output_path="/o")
    assert BuilderContext.from_options(context) is context


def test_methods_enabled_variants() -> None:
    assert BuilderContext("/t", "/o", generate_methods="YES").methods_enabled
    assert not BuilderContext("/t", "/o", generate_methods="false").methods_enabled
    assert not BuilderContext("/t", "/o").methods_enabled


def test_with_plan_returns_an_enriched_copy() -> None:
    context = BuilderContext(template_path="/t", output_path="/o")

    planned = context.with_plan(
        known_types=frozenset({"SP.Foo"}),
        type_modules={"SP.Foo": "office365.foo"},
        cyclic_types=frozenset(),
        enum_defaults={},
    )

    assert planned.known_types == frozenset({"SP.Foo"})
    assert context.known_types == frozenset()  # original untouched


def test_context_is_immutable() -> None:
    context = BuilderContext(template_path="/t", output_path="/o")
    with pytest.raises(FrozenInstanceError):
        context.namespace = "X"  # type: ignore[misc]
