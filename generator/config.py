"""Generator configuration: ``settings.<service>.cfg`` -> typed options."""

from __future__ import annotations

import os
from configparser import ConfigParser
from dataclasses import dataclass, field
from pathlib import Path


def parse_list(raw: str) -> list[str]:
    """Split a comma/newline separated config value into stripped items."""
    return [item.strip() for item in raw.replace("\n", ",").split(",") if item.strip()]


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
        """Read ``settings.<service>.cfg`` (relative to ``base_dir``)."""
        cfg = ConfigParser()
        cfg.optionxform = str  # type names are case-sensitive
        cfg.read(base_dir / f"settings.{service}.cfg")

        def section(name: str) -> dict[str, str]:
            return dict(cfg.items(name)) if cfg.has_section(name) else {}

        main = section(service)
        filters = section("filters")
        modules = section("modules")
        return cls(
            metadata_path=resolve_path(base_dir, main["metadata_path"]),
            output_path=resolve_path(base_dir, main["output_path"]),
            template_path=resolve_path(base_dir, main["template_path"]),
            context_type=main.get("context_type", "ClientContext"),
            generate_methods=main.get("generate_methods", ""),
            modules=",".join(modules.values()),
            namespace=main.get("namespace", ""),
            ignored_types=parse_list(filters.get("ignored_types", "")),
            ignored_properties=parse_list(filters.get("ignored_properties", "")),
            ignored_methods=parse_list(filters.get("ignored_methods", "")),
            include_base_types=parse_list(main.get("include_base_types", "")),
            start_at=main.get("start_at", ""),
            routing=section("routing"),
            type_routing=section("type_routing"),
            dry_run=dry_run,
        )

    def builder_options(self) -> dict:
        """The plain dict the builders consume (decouples them from config)."""
        options: dict = {
            "template_path": self.template_path,
            "output_path": self.output_path,
            "modules": self.modules,
            "context_type": self.context_type,
            "generate_methods": self.generate_methods,
            "namespace": self.namespace,
            "ignored_properties": self.ignored_properties,
            "ignored_methods": self.ignored_methods,
            "type_routing": self.type_routing,
            "dry_run": self.dry_run,
        }
        for namespace, module in self.routing.items():
            options[f"routing_{namespace}"] = module
        return options
