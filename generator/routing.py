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

import ast
import keyword
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Optional

from generator.builders.naming import python_name, to_snake_case
from generator.odata.type_system import strip_collection


def _module_segment(segment: str) -> str:
    """A valid Python package name for one namespace segment.

    Namespace segments may be numbers or keywords (``...Windows.10...``,
    ``...class...``), which cannot appear in an ``import``; prefix a ``_``.
    """
    text = segment.lower()
    if not text.isidentifier() or keyword.iskeyword(text):
        text = f"_{text}"
    return text


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
                parts = [_module_segment(part) for part in remainder.split(".")]
                return f"{module}.{'.'.join(parts)}"
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
    def from_options(cls, options) -> "Router":
        if isinstance(options, dict):
            namespace = {
                key[len("routing_") :]: value.strip() for key, value in options.items() if key.startswith("routing_")
            }
            types = {name: module.strip() for name, module in (options.get("type_routing") or {}).items()}
        else:  # BuilderContext
            namespace = {name: str(module).strip() for name, module in options.routing.items()}
            types = {name: str(module).strip() for name, module in options.type_routing.items()}
        return cls(namespace, types)

    @property
    def fallback(self) -> str:
        """The catch-all (``*``) module, if the table defines one."""
        return self.types.get("*", "").strip()

    def module_for(self, type_name: str, *, allow_fallback: bool = True) -> Optional[str]:
        """The routed module for a type: exact name, then namespace, then prefix.

        ``allow_fallback=False`` ignores the catch-all ``*`` rule, so callers can
        tell a *specific* placement from the fallback bucket.
        """
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
            if pattern == "*" and not allow_fallback:
                continue
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


def _plural(word: str) -> str:
    """A naive English plural, enough to match OData collection package names."""
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    if word.endswith("y") and word[-2:-1] not in "aeiou":
        return word[:-1] + "ies"
    return word + "s"


def _singular(word: str) -> str:
    """A naive English singular, the inverse of :func:`_plural`."""
    if word.endswith("ies") and len(word) > len("ies"):
        return word[:-3] + "y"
    if word.endswith(("ses", "xes", "zes", "ches", "shes")):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _path_words(module_path: str) -> set[str]:
    """Singularized package segments of a module path (drops the ``office365`` root)."""
    return {_singular(seg.lower()) for seg in module_path.split(".") if seg and seg != "office365"}


def _strip_path_prefix(words: list[str], module_path: str) -> list[str]:
    """Strip leading ``words`` that merely repeat a segment of ``module_path``.

    ``WorkbookChartAxisFormat`` routed to ``...workbooks.charts`` -> ``[axis, format]``;
    ``X509Certificate...`` routed to ``...certificates.x509`` -> ``[authentication, ...]``.
    Order-insensitive (``x509`` matches the later ``x509`` segment) and singular-aware.
    Returns the original words when everything would be stripped.
    """
    segments = _path_words(module_path)
    index = 0
    while index < len(words) and _singular(words[index].lower()) in segments:
        index += 1
    return words[index:] or words


def _consume_prefix(entry: str, words: list[str]) -> int:
    """How many leading ``words`` a package name consumes, or 0.

    Matches the joined words exactly or as their plural (``call`` -> ``calls``).
    """
    target = entry.lower().replace("_", "")
    acc = ""
    for index, word in enumerate(words):
        acc += word.lower().replace("_", "")
        if target == acc or target == _plural(acc):
            return index + 1
        if not target.startswith(acc):
            break
    return 0


def _defines_class(path: str, class_name: str) -> bool:
    """Whether ``path`` defines a top-level class named ``class_name``."""
    try:
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except (OSError, SyntaxError):
        return False
    return any(isinstance(node, ast.ClassDef) and node.name == class_name for node in tree.body)


def _collides(directory: str, stem: str, class_name: str) -> bool:
    """Whether ``<directory>/<stem>.py`` exists and defines a *different* class."""
    path = os.path.join(directory, stem + ".py")
    return os.path.isfile(path) and not _defines_class(path, class_name)


def descend_module(module_path: str, class_name: str, output_base: str) -> tuple[str, str]:
    """Place a new type in a matching subsystem package, stripping prefixes.

    Three steps, all only for new files (placed types stay put: sticky):

    1. strip leading words implied by the module path
       (``WorkbookChartAxisFormat`` + ``...workbooks.charts`` -> ``axis_format``);
    2. descend into a subpackage whose name matches the remaining prefix,
       singular or plural (``CallMediaState`` -> ``calls/media_state``);
    3. otherwise strip a prefix equal to the module's own name
       (``communications`` + ``CommunicationsApplicationIdentity``).

    A prefix is only stripped when the result would not collide with a file that
    defines a *different* class; on collision the full name is kept.
    """
    file_stem = to_snake_case(class_name, avoid_keywords=False)
    if not module_path or not output_base:
        return module_path, file_stem
    base = module_directory(module_path, output_base)
    if not os.path.isdir(base):
        return module_path, file_stem
    words = _strip_path_prefix(file_stem.split("_"), module_path)

    best: tuple[int, int, str] | None = None
    for entry in sorted(os.listdir(base)):
        subdir = os.path.join(base, entry)
        if entry.startswith("__") or not os.path.isdir(subdir):
            continue
        if not os.path.isfile(os.path.join(subdir, "__init__.py")):
            continue
        consumed = _consume_prefix(entry, words)
        if consumed and (best is None or len(entry) > best[0]):
            best = (len(entry), consumed, entry)
    if best is not None:
        _, consumed, dirname = best
        remaining = "_".join(words[consumed:]) or file_stem
        if not _collides(os.path.join(base, dirname), remaining, class_name):
            return f"{module_path}.{dirname}", remaining
        return f"{module_path}.{dirname}", file_stem

    remaining = "_".join(words)
    if remaining and remaining != file_stem and not _collides(base, remaining, class_name):
        return module_path, remaining
    return module_path, file_stem


def planned_module(type_name: str, schema, registry, router: Router, output_base: str = "") -> Optional[str]:
    """The **file** module a type will live in (attached), or ``None`` if unrouted.

    For a routed new type this is ``<target module>.<snake_class_name>`` — the
    module of the file the generator will create (not the package), so imports
    point at the file rather than the package ``__init__``.
    """
    module = registry.strict_module_for(type_name, schema.BaseTypeFullName)
    if module:
        return module
    directory = router.module_for(type_name)
    if not directory:
        return None
    class_name = python_name(type_name, bool(schema.IsValueObject))
    directory, file_stem = descend_module(directory, class_name, output_base)
    return f"{directory}.{file_stem}"


def _in_fallback(module: str, fallback: str) -> bool:
    """Whether ``module`` lives in the catch-all (fallback) bucket."""
    if not fallback:
        return False
    prefix = fallback.rstrip(".")
    return module == prefix or module.startswith(prefix + ".")


def _owning_module(modules: Counter) -> str:
    """The module that most plausibly owns a type, given its referrer modules.

    A type is normally referenced from the package that *defines* its accessor,
    but sometimes also from a sub-package that extends it. Prefer the deepest
    referrer that is an ancestor of the dominant one, so a type used from
    ``.../app/protections`` lands in ``.../app`` rather than ``.../protections``.
    """
    ranked = modules.most_common()
    dominant = ranked[0][0]
    ancestors = [module for module, _ in ranked if module != dominant and dominant.startswith(module + ".")]
    return max(ancestors, key=len) if ancestors else dominant


def _majority(values: Iterable[str]) -> Optional[str]:
    """The most common value, or ``None`` when there are none."""
    counts = Counter(values)
    return counts.most_common(1)[0][0] if counts else None


def infer_placements(model, type_filter, registry, router: Router, rounds: int = 6) -> dict[str, str]:
    """Infer a module for every in-scope type, propagating from routed anchors.

    Seeds are the types already routed (or attached); each round assigns an
    unrouted type the majority module of the types that reference it (properties
    and navigation), so product groupings spread across the reference graph.
    Returns ``{odata_name: module}`` for every type it could place.
    """
    assigned: dict[str, str] = {}
    in_scope: list[str] = []
    fallback = router.fallback
    for name, schema in model.types.items():
        if not type_filter.in_scope(name, schema):
            continue
        in_scope.append(name)
        # A *directory* module: for an attached type drop the file segment.
        # Types parked in the fallback bucket are not anchors: they are
        # re-derived from their referrers so they can be re-routed.
        module = registry.strict_module_for(name)
        if module and not _in_fallback(module, fallback):
            assigned[name] = module.rsplit(".", 1)[0]
            continue
        routed = router.module_for(name, allow_fallback=False)
        if routed:
            assigned[name] = routed

    short = {name.rsplit(".", 1)[-1]: name for name in in_scope}

    def target(type_name: str | None) -> Optional[str]:
        base = strip_collection(type_name)
        if not base:
            return None
        return short.get(base) or short.get(base.rsplit(".", 1)[-1])

    referrers: dict[str, list[str]] = defaultdict(list)
    for name in in_scope:
        for prop in model.types[name].Properties.values():
            referenced = target(prop.TypeName)
            if referenced:
                referrers[referenced].append(name)

    pending = [name for name in in_scope if name not in assigned]
    for _ in range(rounds):
        changed = False
        for name in pending:
            if name in assigned:
                continue
            modules = Counter(assigned[r] for r in referrers.get(name, ()) if r in assigned)
            if modules:
                assigned[name] = _owning_module(modules)
                changed = True
        if not changed:
            break
    return assigned


def render_suggestions(
    model,
    type_filter,
    registry,
    router: Router,
    services: Optional[dict[str, str]] = None,
    service_map: Optional[dict[str, str]] = None,
) -> str:
    """Paste-ready routing proposals for types without a *specific* route.

    Signals, strongest first: the docs **service taxonomy**
    (``{type_lower: service}`` + ``{service: module}``), then the reference graph
    (:func:`infer_placements`), then ``Prefix*`` clusters. A human reviews and
    pastes the result — routing is never written automatically.
    """
    services = services or {}
    service_map = service_map or {}
    assigned = infer_placements(model, type_filter, registry, router)
    fallback = router.fallback
    unrouted: dict[str, list[str]] = defaultdict(list)
    relocatable: set[str] = set()
    for name, schema in model.types.items():
        if not type_filter.in_scope(name, schema):
            continue
        attached = registry.strict_module_for(name)
        if attached:
            if _in_fallback(attached, fallback):
                relocatable.add(name)
            continue
        if router.module_for(name, allow_fallback=False):
            continue
        unrouted[name.rsplit(".", 1)[0]].append(name)

    def service_module(name: str) -> Optional[str]:
        service = service_map.get(name.rsplit(".", 1)[-1].lower())
        return services.get(service) if service else None

    namespace_lines: list[str] = []
    for namespace, names in sorted(unrouted.items()):
        if namespace == "microsoft.graph":
            continue
        by_service = [module for module in (service_module(n) for n in names) if module]
        siblings = [module for name, module in assigned.items() if name.rsplit(".", 1)[0] == namespace]
        suggested = (
            _majority(by_service) or _majority(siblings) or f"office365.{_module_segment(namespace.rsplit('.', 1)[-1])}"
        )
        namespace_lines.append(f"  {namespace}: {suggested}   # {len(names)} type(s)")

    # Bare ``microsoft.graph.*`` types: the service taxonomy wins, then the
    # reference graph; the rest are grouped into ``Prefix*`` rules.
    exact_lines: list[str] = []
    by_prefix: dict[str, list[str]] = defaultdict(list)
    candidates = list(unrouted.get("microsoft.graph", []))
    candidates += [name for name in sorted(relocatable) if name.rsplit(".", 1)[0] == "microsoft.graph"]
    for name in candidates:
        short = name.rsplit(".", 1)[-1]
        module = service_module(name)
        if module:
            service = service_map.get(short.lower())
            exact_lines.append(f'  "{short}": {module}   # service: {service}')
        elif name in assigned and not _in_fallback(assigned[name], fallback):
            anchor = model.anchors.get(name)
            note = f"   # anchor: {anchor}" if anchor else (f"   # out of {fallback}" if name in relocatable else "")
            exact_lines.append(f'  "{short}": {assigned[name]}{note}')
        else:
            by_prefix[_first_word(short)].append(name)

    type_lines: list[str] = []
    for prefix, names in sorted(by_prefix.items(), key=lambda item: -len(item[1])):
        sample = ", ".join(n.rsplit(".", 1)[-1] for n in names[:3])
        type_lines.append(f'  "{prefix}*": <choose>   # {len(names)}: {sample}...')

    return "\n".join(["routing:", *namespace_lines, "type_routing:", *exact_lines, *type_lines])
