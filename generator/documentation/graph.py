"""
Microsoft Graph documentation: injects descriptions from the OpenAPI spec.

The spec (``graphopenapi.yaml``, ~34 MB) is expensive to parse, so only the
descriptions generation needs are extracted once and cached as a small JSON
sidecar (``graphopenapi.cache.json``). Subsequent runs load the cache instead
of re-parsing the whole document.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from generator.builders.type import TypeBuilder
from generator.documentation.base import DocumentationProvider

_YAML_PATH = Path(__file__).parent / "graphopenapi.yaml"
_CACHE_PATH = _YAML_PATH.with_suffix(".cache.json")


class GraphDocumentation(DocumentationProvider):
    """Injects property and member descriptions from the Graph OpenAPI YAML.

    Descriptions become docstrings on generated types, properties and enum
    members.
    """

    def __init__(self) -> None:
        self._schemas = _load_schemas()

    def build_documentation(self, type_builder: TypeBuilder) -> None:
        """Inject descriptions from the OpenAPI spec into the type builder."""
        info = self._schemas.get(type_builder.entity_type_name)
        if info is None:
            return

        description = info.get("description")
        if description:
            type_builder._docstring = description

        props = info.get("properties", {})
        for prop in type_builder.properties:
            prop_schema = props.get(prop.schema.Name)
            if prop_schema and prop_schema.get("description"):
                prop.docstring = prop_schema["description"]


def _load_schemas() -> dict[str, Any]:
    """The ``{type: {description, properties}}`` map, from cache when fresh."""
    if not _YAML_PATH.is_file():
        print(f"  Graph docs: {_YAML_PATH.name} not found; skipping docstrings")
        return {}

    stat = _YAML_PATH.stat()
    cached = _read_cache(stat.st_size, stat.st_mtime)
    if cached is not None:
        return cached

    schemas = _extract(_parse_yaml())
    _write_cache(stat.st_size, stat.st_mtime, schemas)
    return schemas


def _parse_yaml() -> dict[str, Any]:
    """Parse the OpenAPI document, preferring the libyaml C loader."""
    try:
        import yaml
    except ImportError:
        print("  Graph docs: pyyaml is not installed; skipping docstrings")
        return {}

    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    try:
        with open(_YAML_PATH, encoding="utf-8") as f:
            data = yaml.load(f, Loader=loader)
    except Exception as e:  # malformed or unreadable spec
        print(f"  Graph docs: failed to parse {_YAML_PATH.name}: {e}")
        return {}
    return data if isinstance(data, dict) else {}


def _extract(data: dict[str, Any]) -> dict[str, Any]:
    """Reduce the full document to the descriptions generation consumes."""
    components = data.get("components", {})
    schemas = components.get("schemas", {}) if isinstance(components, dict) else {}
    if not isinstance(schemas, dict):
        return {}

    slim: dict[str, Any] = {}
    for name, schema in schemas.items():
        info = _type_info(schema)
        if info is None:
            continue
        description = info.get("description") or schema.get("description")
        properties = {
            prop: {"description": spec["description"]}
            for prop, spec in (info.get("properties") or {}).items()
            if isinstance(spec, dict) and "description" in spec
        }
        if description or properties:
            slim[name] = {"description": description, "properties": properties}
    return slim


def _type_info(schema: dict[str, Any]) -> dict[str, Any] | None:
    """The part of a schema holding this type's own description and properties.

    Handles both flat schemas and the ``allOf`` pattern used by Graph:
    ``allOf: [$ref parent, {title, properties}]`` — the second entry holds
    this type's own properties.
    """
    all_of = schema.get("allOf")
    if all_of and len(all_of) > 1:
        return all_of[1]
    if all_of and len(all_of) == 1:
        return all_of[0]
    if "properties" in schema:
        return schema
    return None


def _read_cache(source_size: int, source_mtime: float) -> dict[str, Any] | None:
    """The cached map, or ``None`` when missing or stale."""
    try:
        payload = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    if payload.get("source_size") != source_size or payload.get("source_mtime") != source_mtime:
        return None
    schemas = payload.get("schemas")
    return schemas if isinstance(schemas, dict) else None


def _write_cache(source_size: int, source_mtime: float, schemas: dict[str, Any]) -> None:
    """Persist the slim map; a failed write just means the next run re-parses."""
    try:
        payload = {"source_size": source_size, "source_mtime": source_mtime, "schemas": schemas}
        _CACHE_PATH.write_text(json.dumps(payload), encoding="utf-8")
    except OSError:
        pass
