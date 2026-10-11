"""Typed, immutable configuration passed to the builders.

Replaces the free-form ``dict`` (string keys, no validation) that used to be
threaded through every builder. ``from_options`` still accepts the legacy dict
so tests and the config adapter keep working.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class BuilderContext:
    """Everything a :class:`~generator.builders.type.TypeBuilder` needs."""

    template_path: str
    output_path: str
    modules: str = ""
    namespace: str = ""
    context_type: str = "ClientContext"
    generate_methods: str = ""
    ignored_properties: tuple[str, ...] = ()
    ignored_methods: tuple[str, ...] = ()
    routing: Mapping[str, str] = field(default_factory=dict)
    type_routing: Mapping[str, str] = field(default_factory=dict)
    known_types: frozenset[str] = frozenset()
    type_modules: Mapping[str, str] = field(default_factory=dict)
    cyclic_types: frozenset[str] = frozenset()
    enum_defaults: Mapping[str, str] = field(default_factory=dict)
    entity_types: frozenset[str] = frozenset()
    inherited_members: Mapping[str, frozenset[str]] = field(default_factory=dict)
    dry_run: bool = False

    @property
    def methods_enabled(self) -> bool:
        """Whether operation method generation is enabled."""
        return str(self.generate_methods).strip().lower() in {"true", "1", "yes"}

    @classmethod
    def from_options(cls, options: Optional[Any]) -> "BuilderContext":
        """Normalize a legacy options dict (or an existing context) to a context."""
        if isinstance(options, BuilderContext):
            return options
        options = options or {}
        return cls(
            template_path=options.get("template_path", options.get("templatepath", "")),
            output_path=options.get("output_path", options.get("outputpath", "")),
            modules=options.get("modules", ""),
            namespace=options.get("namespace", ""),
            context_type=options.get("context_type", "ClientContext"),
            generate_methods=options.get("generate_methods", ""),
            ignored_properties=tuple(options.get("ignored_properties") or ()),
            ignored_methods=tuple(options.get("ignored_methods") or ()),
            routing={key[len("routing_") :]: value for key, value in options.items() if key.startswith("routing_")},
            type_routing=dict(options.get("type_routing") or {}),
            known_types=frozenset(options.get("known_types") or ()),
            type_modules=dict(options.get("type_modules") or {}),
            cyclic_types=frozenset(options.get("cyclic_types") or ()),
            enum_defaults=dict(options.get("enum_defaults") or {}),
            entity_types=frozenset(options.get("entity_types") or ()),
            inherited_members={
                name: frozenset(members) for name, members in (options.get("inherited_members") or {}).items()
            },
            dry_run=bool(options.get("dry_run", False)),
        )

    def with_plan(
        self,
        *,
        known_types: frozenset[str],
        type_modules: Mapping[str, str],
        cyclic_types: frozenset[str],
        enum_defaults: Mapping[str, str],
        inherited_members: Mapping[str, frozenset[str]],
        entity_types: frozenset[str] = frozenset(),
    ) -> "BuilderContext":
        """Return a copy enriched with the run plan (known types, modules, cycles)."""
        return replace(
            self,
            known_types=known_types,
            type_modules=dict(type_modules),
            cyclic_types=cyclic_types,
            enum_defaults=dict(enum_defaults),
            entity_types=frozenset(entity_types),
            inherited_members={name: frozenset(members) for name, members in inherited_members.items()},
        )
