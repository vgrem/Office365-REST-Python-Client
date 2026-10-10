"""Namespace/type routing: map OData types to Python packages.

Two rule sets, first match wins:

* ``[routing]`` — a **namespace** prefix maps to a module; the remaining
  namespace segments are appended, lowercased.
* ``[type_routing]`` — an **exact** OData type name, or a ``Prefix*`` on the
  type's short name, maps directly to a module.

A type that matches no rule is *unrouted* and is skipped (reported) rather than
dumped at the package root.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from generator.builders.naming import to_snake_case
from generator.builders.type_registry import python_name

#: Namespace -> module hints (used by ``--suggest-routing``).
NAMESPACE_HINTS: dict[str, str] = {
    "microsoft.graph.callRecords": "office365.communications.callrecords",
    "microsoft.graph.customDataProvidedResourcePayloads": "office365.directory.identitygovernance",
    "microsoft.graph.entraRecoveryServices": "office365.directory",
    "microsoft.graph.teamsAdministration": "office365.teams",
    "microsoft.graph.termStore": "office365.directory.termstore",
}

#: Prefix -> product-module hints for bare ``microsoft.graph.*`` types.
PREFIX_HINTS: dict[str, str] = {
    "Education": "office365.education",
    "Rubric": "office365.education",
    "Challenging": "office365.education",
    "Windows": "office365.intune",
    "Win32": "office365.intune",
    "Ios": "office365.intune",
    "Android": "office365.intune",
    "Oma": "office365.intune",
    "Printer": "office365.intune",
    "Print": "office365.intune",
    "Device": "office365.intune",
    "Mobile": "office365.intune",
    "Mac": "office365.intune",
    "Planner": "office365.planner",
    "Booking": "office365.booking",
    "Call": "office365.communications",
    "Media": "office365.communications",
    "Chat": "office365.communications",
    "Communications": "office365.communications",
    "Teleconference": "office365.communications",
    "Virtual": "office365.communications",
    "Search": "office365.search",
    "Attack": "office365.directory.security",
    "Simulation": "office365.directory.security",
    "Cloud": "office365.directory.security",
    "Access": "office365.directory.identitygovernance",
    "Copilot": "office365.copilot",
}


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


def _first_word(class_name: str) -> str:
    match = re.match(r"[A-Z][a-z0-9]*|[A-Z]+(?=[A-Z][a-z]|$)", class_name)
    return match.group(0) if match else class_name


@dataclass
class Router:
    """Applies the namespace and type routing tables."""

    namespace: dict[str, str] = field(default_factory=dict)
    types: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_options(cls, options: dict) -> "Router":
        namespace = {
            key[len("routing_") :]: value.strip() for key, value in options.items() if key.startswith("routing_")
        }
        types = {name: module.strip() for name, module in (options.get("type_routing") or {}).items()}
        return cls(namespace, types)

    def module_for(self, type_name: str) -> Optional[str]:
        """The routed module for a type: exact name, then namespace, then prefix."""
        if not type_name:
            return None
        exact = self.types.get(type_name)
        if exact:
            return exact
        namespace = type_name.rsplit(".", 1)[0] if "." in type_name else ""
        module = route_namespace(namespace, self.namespace)
        if module:
            return module
        short = type_name.rsplit(".", 1)[-1]
        for pattern, target in self.types.items():
            if pattern.endswith("*") and short.startswith(pattern[:-1]):
                return target
        return None


def planned_module(type_name: str, schema, registry, router: Router) -> Optional[str]:
    """The **file** module a type will live in (attached), or ``None`` if unrouted.

    For a routed new type this is ``<target module>.<snake_class_name>`` — the
    module of the file the generator will create (not the package), so imports
    point at the file rather than the package ``__init__``.
    """
    module = registry.strict_module_for(type_name)
    if module:
        return module
    directory = router.module_for(type_name)
    if not directory:
        return None
    class_name = python_name(type_name, bool(schema.IsValueObject))
    return f"{directory}.{to_snake_case(class_name, avoid_keywords=False)}"


def render_suggestions(model, type_filter, registry, router: Router) -> str:
    """A paste-ready ``[routing]``/``[type_routing]`` block for unrouted types."""
    unrouted: dict[str, list[str]] = defaultdict(list)
    for name, schema in model.types.items():
        if not type_filter.in_scope(name, schema):
            continue
        if registry.strict_module_for(name) or router.module_for(name):
            continue
        unrouted[name.rsplit(".", 1)[0]].append(name)

    namespace_lines: list[str] = []
    for namespace, names in sorted(unrouted.items()):
        if namespace != "microsoft.graph":
            suggested = NAMESPACE_HINTS.get(namespace, f"office365.{namespace.rsplit('.', 1)[-1].lower()}")
            namespace_lines.append(f"{namespace} = {suggested}   # {len(names)} type(s)")

    by_prefix: dict[str, list[str]] = defaultdict(list)
    for name in unrouted.get("microsoft.graph", []):
        by_prefix[_first_word(name.rsplit(".", 1)[-1])].append(name)

    type_lines: list[str] = []
    for prefix, names in sorted(by_prefix.items(), key=lambda item: -len(item[1])):
        hint = PREFIX_HINTS.get(prefix, "<choose>")
        sample = ", ".join(n.rsplit(".", 1)[-1] for n in names[:3])
        type_lines.append(f"{prefix}* = {hint}   # {len(names)}: {sample}...")

    return "\n".join(["[routing]", *namespace_lines, "", "[type_routing]", *type_lines])
