"""Namespace/type routing: map OData types to Python packages.

Two rule sets, first match wins:

* ``routing`` — a **namespace** prefix maps to a module; the remaining
  namespace segments are appended, lowercased.
* ``type_routing`` — an **exact** OData type name, or a ``Prefix*`` on the
  type's short name, maps directly to a module.

A type that matches no rule is *unrouted* and is skipped (reported) rather than
dumped at the package root.
"""

from __future__ import annotations

import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Optional

from generator.builders.naming import to_snake_case
from generator.builders.type_registry import python_name


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
        # Short-name exact rule (used for bare ``microsoft.graph.*`` types, where
        # no namespace route applies). Checked after the namespace so it never
        # overrides a namespace-scoped type.
        exact = self.types.get(short)
        if exact:
            return exact
        for pattern, target in self.types.items():
            if pattern.endswith("*") and short.startswith(pattern[:-1]):
                return target
        return None


def module_directory(module_path: str, output_base: str) -> str:
    """The filesystem directory a routed module maps to."""
    relative = module_path[len("office365.") :] if module_path.startswith("office365.") else module_path
    sub_dir = relative.replace(".", "/")
    parts = [output_base]
    if sub_dir not in ("", "."):
        suffix = output_base.rstrip("/").rsplit("/", 1)[-1]
        if sub_dir != suffix:
            parts.append(sub_dir)
    return os.path.join(*parts)


def descend_module(module_path: str, class_name: str, output_base: str) -> tuple[str, str]:
    """Descend into a matching subsystem package, stripping the class-name prefix.

    E.g. ``...identitygovernance`` + ``AccessReviewContextDataBase`` ->
    ``...identitygovernance.accessreview`` + ``context_data_base`` when an
    ``accessreview/`` package exists under the routed directory. Only new files
    descend (placed types stay put: placement is sticky).
    """
    file_stem = to_snake_case(class_name, avoid_keywords=False)
    if not module_path or not output_base:
        return module_path, file_stem
    base = module_directory(module_path, output_base)
    if not os.path.isdir(base):
        return module_path, file_stem
    words = file_stem.split("_")
    best: tuple[int, int, str] | None = None
    for entry in sorted(os.listdir(base)):
        subdir = os.path.join(base, entry)
        if entry.startswith("__") or not os.path.isdir(subdir):
            continue
        if not os.path.isfile(os.path.join(subdir, "__init__.py")):
            continue
        prefix = entry.lower().replace("_", "")
        consumed = 0
        acc = ""
        for index, word in enumerate(words):
            acc += word.lower().replace("_", "")
            if acc == prefix:
                consumed = index + 1
                break
            if not prefix.startswith(acc):
                break
        if consumed and (best is None or len(prefix) > best[0]):
            best = (len(prefix), consumed, entry)
    if best is None:
        return module_path, file_stem
    _, consumed, dirname = best
    remaining = "_".join(words[consumed:]) or file_stem
    return f"{module_path}.{dirname}", remaining


def planned_module(type_name: str, schema, registry, router: Router, output_base: str = "") -> Optional[str]:
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
    directory, file_stem = descend_module(directory, class_name, output_base)
    return f"{directory}.{file_stem}"


def _majority(values: Iterable[str]) -> Optional[str]:
    """The most common value, or ``None`` when there are none."""
    counts = Counter(values)
    return counts.most_common(1)[0][0] if counts else None


def render_suggestions(model, type_filter, registry, router: Router) -> str:
    """Paste-ready routing proposals for unrouted types.

    Suggestions are inferred from the routing already in effect: an unrouted
    namespace/prefix is proposed the module that the majority of its
    **already-routed** siblings use, so no hint tables need maintaining.
    """
    routed: dict[str, str] = {}
    unrouted: dict[str, list[str]] = defaultdict(list)
    for name, schema in model.types.items():
        if not type_filter.in_scope(name, schema):
            continue
        module = registry.strict_module_for(name) or router.module_for(name)
        if module:
            routed[name] = module
        else:
            unrouted[name.rsplit(".", 1)[0]].append(name)

    namespace_lines: list[str] = []
    for namespace, names in sorted(unrouted.items()):
        if namespace == "microsoft.graph":
            continue
        siblings = [module for name, module in routed.items() if name.rsplit(".", 1)[0] == namespace]
        suggested = _majority(siblings) or f"office365.{namespace.rsplit('.', 1)[-1].lower()}"
        namespace_lines.append(f"  {namespace}: {suggested}   # {len(names)} type(s)")

    # Bare ``microsoft.graph.*`` types: propose by first word using routed peers.
    prefix_modules: dict[str, Counter] = defaultdict(Counter)
    for name, module in routed.items():
        if name.rsplit(".", 1)[0] == "microsoft.graph":
            prefix_modules[_first_word(name.rsplit(".", 1)[-1])][module] += 1

    by_prefix: dict[str, list[str]] = defaultdict(list)
    for name in unrouted.get("microsoft.graph", []):
        by_prefix[_first_word(name.rsplit(".", 1)[-1])].append(name)

    type_lines: list[str] = []
    for prefix, names in sorted(by_prefix.items(), key=lambda item: -len(item[1])):
        hint = _majority(prefix_modules.get(prefix, {})) or "<choose>"
        sample = ", ".join(n.rsplit(".", 1)[-1] for n in names[:3])
        type_lines.append(f'  "{prefix}*": {hint}   # {len(names)}: {sample}...')

    return "\n".join(["routing:", *namespace_lines, "type_routing:", *type_lines])
