"""Namespace/type routing: map OData namespaces to Python packages.

The routing table maps a namespace prefix to a target module (e.g.
``SP = office365.sharepoint``). The longest matching prefix wins and the
remaining namespace segments are appended, lowercased:

    ``SP.Directory.Provider`` + ``SP = office365.sharepoint``
        -> ``office365.sharepoint.directory.provider``

A mapped entry whose remainder is empty targets the module itself.
"""

from __future__ import annotations

from typing import Optional


def route_namespace(namespace: str, routing: dict[str, str]) -> str:
    """The target module for an OData namespace, or ``""`` when unrouted."""
    if not routing:
        return ""
    entries = sorted(routing.items(), key=lambda item: len(item[0]), reverse=True)
    namespace_lower = namespace.lower()
    for prefix, module in entries:
        prefix_lower = prefix.lower()
        if namespace_lower == prefix_lower or namespace_lower.startswith(prefix_lower + "."):
            remainder = namespace[len(prefix) :].lstrip(".")
            if remainder:
                return f"{module}.{remainder.lower()}"
            return module
    return ""


def routing_from_options(options: dict) -> dict[str, str]:
    """Collect ``routing_<prefix>`` builder options into a routing table."""
    return {key[len("routing_") :]: value.strip() for key, value in options.items() if key.startswith("routing_")}


def planned_module(type_name: str, registry, routing: dict[str, str]) -> Optional[str]:
    """The module a type will live in: its existing module or a routed one.

    Returns ``None`` when the type is neither attached nor routable. This is the
    single source of truth for "will this type be generated, and where", used to
    decide which imports/annotations are resolvable.
    """
    module = registry.strict_module_for(type_name)
    if module:
        return module
    namespace = type_name.rsplit(".", 1)[0] if "." in type_name else ""
    return route_namespace(namespace, routing) or None
