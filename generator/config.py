"""Generator configuration: ``settings.<service>.yaml`` -> typed options."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from generator.builders.context import BuilderContext


class ConfigError(Exception):
    """Raised when a generator config file is missing, malformed or inconsistent."""


#: Recognised top-level keys (anything else is almost certainly a typo).
_KNOWN_KEYS = {
    "metadata_path",
    "output_path",
    "template_path",
    "context_type",
    "generate_methods",
    "modules",
    "namespace",
    "include_base_types",
    "start_at",
    "filters",
    "routing",
    "type_routing",
}
_KNOWN_FILTER_KEYS = {"ignored_types", "ignored_properties", "ignored_methods"}


def parse_list(value: Any) -> list[str]:
    """Normalize a config value (list, comma/newline string, or ``None``) to a list."""
    if value is None:
        return []
    items = value if isinstance(value, (list, tuple)) else str(value).replace("\n", ",").split(",")
    return [str(item).strip() for item in items if str(item).strip()]


def split_ignored(patterns: list[str]) -> tuple[list[str], list[str]]:
    """Split ignored-type patterns into exact names and ``prefix*`` patterns."""
    exact: list[str] = []
    prefix: list[str] = []
    for pattern in patterns:
        if pattern.endswith("*"):
            prefix.append(pattern[:-1])
        else:
            exact.append(pattern)
    return exact, prefix


def resolve_path(base_dir: Path, value: str) -> str:
    """Resolve a config path relative to the generator directory (not the CWD)."""
    return value if os.path.isabs(value) else str((base_dir / value).resolve())


def _mapping(value: Any, where: str) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"{where} must be a mapping, got {type(value).__name__}")
    return {str(key): str(item) for key, item in value.items()}


def _validate_modules(modules: list[str], output_root: str, where: str) -> None:
    """Every scanned module must map to an existing package directory."""
    package = Path(output_root).name
    for module in modules:
        parts = module.split(".")
        if parts[0] != package:
            continue
        directory = Path(output_root, *parts[1:]) if len(parts) > 1 else Path(output_root)
        if not directory.is_dir():
            raise ConfigError(f"{where}: module '{module}' has no directory ({directory})")


@dataclass
class GeneratorOptions:
    """Everything the pipeline and builders need for one service run."""

    metadata_path: str
    output_path: str
    template_path: str
    context_type: str = "ClientContext"
    generate_methods: str = ""
    modules: str = ""
    namespace: str = ""
    ignored_types: list[str] = field(default_factory=list)
    ignored_properties: list[str] = field(default_factory=list)
    ignored_methods: list[str] = field(default_factory=list)
    include_base_types: list[str] = field(default_factory=list)
    start_at: str = ""
    routing: dict[str, str] = field(default_factory=dict)
    type_routing: dict[str, str] = field(default_factory=dict)
    dry_run: bool = False

    @classmethod
    def load(cls, service: str, base_dir: Path, *, dry_run: bool = False) -> "GeneratorOptions":
        """Read and validate ``settings.<service>.yaml`` (relative to ``base_dir``)."""
        path = base_dir / f"settings.{service}.yaml"
        if not path.is_file():
            raise ConfigError(f"missing config: {path}")
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            raise ConfigError(f"{path}: invalid YAML: {e}") from e
        if not isinstance(data, dict):
            raise ConfigError(f"{path}: top level must be a mapping")

        unknown = set(data) - _KNOWN_KEYS
        if unknown:
            raise ConfigError(f"{path}: unknown key(s): {', '.join(sorted(unknown))}")
        for required in ("metadata_path", "output_path", "template_path"):
            if required not in data:
                raise ConfigError(f"{path}: missing required key '{required}'")

        filters = data.get("filters") or {}
        if not isinstance(filters, dict):
            raise ConfigError(f"{path}: 'filters' must be a mapping")
        unknown_filters = set(filters) - _KNOWN_FILTER_KEYS
        if unknown_filters:
            raise ConfigError(f"{path}: unknown filter key(s): {', '.join(sorted(unknown_filters))}")

        output_path = resolve_path(base_dir, data["output_path"])
        template_path = resolve_path(base_dir, data["template_path"])
        if not Path(template_path).is_dir():
            raise ConfigError(f"{path}: template_path is not a directory ({template_path})")
        modules = parse_list(data.get("modules"))
        _validate_modules(modules, output_path, str(path))

        return cls(
            metadata_path=resolve_path(base_dir, data["metadata_path"]),
            output_path=output_path,
            template_path=template_path,
            context_type=str(data.get("context_type", "ClientContext")),
            generate_methods=str(data.get("generate_methods", "")).strip().lower(),
            modules=",".join(modules),
            namespace=str(data.get("namespace", "") or ""),
            ignored_types=parse_list(filters.get("ignored_types")),
            ignored_properties=parse_list(filters.get("ignored_properties")),
            ignored_methods=parse_list(filters.get("ignored_methods")),
            include_base_types=parse_list(data.get("include_base_types")),
            start_at=str(data.get("start_at", "") or ""),
            routing=_mapping(data.get("routing"), f"{path}: 'routing'"),
            type_routing=_mapping(data.get("type_routing"), f"{path}: 'type_routing'"),
            dry_run=dry_run,
        )

    def builder_context(self) -> BuilderContext:
        """The typed, immutable context the builders consume."""
        return BuilderContext(
            template_path=self.template_path,
            output_path=self.output_path,
            modules=self.modules,
            namespace=self.namespace,
            context_type=self.context_type,
            generate_methods=self.generate_methods,
            ignored_properties=tuple(self.ignored_properties),
            ignored_methods=tuple(self.ignored_methods),
            routing=dict(self.routing),
            type_routing=dict(self.type_routing),
            dry_run=self.dry_run,
        )
