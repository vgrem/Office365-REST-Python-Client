"""Product-agnostic service limits, metadata and guardrails.

A :class:`Limit` describes one service limit — a static threshold *or* a rate
quota — with its value, kind, unit, scope and docs. Limits are declared on the
model with the :func:`limit` decorator (mirroring ``@odata`` / ``@require_permission``):
the declaration is stamped on the callable, appended to its docstring, and
collected into the model's ``_schema``. ``arg=`` also *enforces* a numeric
argument (warn by default, ``raise`` or ``clamp``).

The helpers :func:`exceeds` / :func:`warn_if_exceeds` / :func:`ensure_within`
apply a limit imperatively at a call site; :func:`limits_of` / :func:`verify_limits`
inspect what a method/class declares.

Product packages declare the concrete values — ``office365.sharepoint.thresholds``
for SharePoint/CSOM limits, and the ``quotas`` module of each Graph product
(``outlook``, ``teams``, ``reports``, ``security``, ``onedrive``, ``onedrive.workbooks``,
``directory``, ``communications``) for throttling quotas. This module owns the
mechanics so the runtime and every product share them, plus the single Graph-wide
row (:data:`GLOBAL_QUOTAS`) that no product can own.
"""

from __future__ import annotations

import inspect
import warnings
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable, Iterable, Optional, Protocol, Tuple, TypeVar, overload, runtime_checkable

from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")

_ON_EXCEED = ("warn", "raise")
_LIMIT_MARKER = "__limit_decls__"

#: A conservative default page/chunk size that stays below SharePoint's 5,000-item
#: list view threshold, so paged reads and imports are safe by default.
SAFE_PAGE_SIZE = 2000

#: Default number of items per OData batch (also SharePoint's bulk-operation limit).
DEFAULT_BATCH_SIZE = 100


class LimitKind(Enum):
    """How strictly a limit is enforced (per Microsoft's definitions)."""

    BOUNDARY = "boundary"  # absolute, can't be exceeded by design
    THRESHOLD = "threshold"  # configurable default
    SUPPORTED = "supported"  # tested value


def _human_bytes(value: int) -> str:
    """Format a byte count as ``250 GB`` when it divides evenly, else ``8,000 bytes``."""
    for suffix, step in (("TB", 1024**4), ("GB", 1024**3), ("MB", 1024**2), ("KB", 1024)):
        if value >= step and value % step == 0:
            return f"{value // step} {suffix}"
    return f"{value:,} bytes"


@dataclass(frozen=True)
class Limit:
    """A single service limit — a static threshold or a rate quota.

    Args:
        name: Human-readable name (e.g. ``"list view threshold"``).
        value: The numeric limit.
        kind: :class:`LimitKind` — boundary / threshold / supported.
        unit: What is counted (``items``, ``bytes``, ``requests``, ...).
        scope: The object it applies to (``list``, ``file``, ``app+tenant``, ...).
        note: Extra guidance surfaced in warnings.
        doc: Link to the authoritative documentation.
        window_seconds: The rate window in seconds (``None`` for a static
            threshold; ``0`` for a concurrency limit).
        request_type: ``""`` (n/a) | ``read`` | ``write`` | ``delete`` | ``any``.
    """

    name: str
    value: int
    kind: LimitKind = LimitKind.THRESHOLD
    unit: str = "items"
    scope: str = ""
    note: str = ""
    doc: str = ""
    window_seconds: Optional[int] = None
    request_type: str = ""

    def __str__(self) -> str:
        if self.window_seconds is not None:
            window = f" / {self.window_seconds:,}s" if self.window_seconds else ""
            return f"{self.value:,} {self.unit}{window}".strip()
        if self.unit == "bytes":
            return _human_bytes(self.value)
        return f"{self.value:,} {self.unit}".strip()

    def exceeds(self, value: int) -> bool:
        """Whether ``value`` is over this limit."""
        return value > self.value

    @property
    def is_rate(self) -> bool:
        """Whether this is a rate quota (has a window)."""
        return self.window_seconds is not None


class LimitExceededError(ValueError):
    """Raised when a value exceeds a service limit."""

    def __init__(self, limit: Limit, value: int, *, context: str = "") -> None:
        self.limit = limit
        self.value = value
        self.context = context
        super().__init__(hint(limit, context=context, value=value))


def exceeds(limit: Limit, value: int) -> bool:
    """Whether ``value`` is over ``limit``."""
    return limit.exceeds(value)


def hint(limit: Limit, *, context: str = "", value: Optional[int] = None) -> str:
    """An actionable message for a limit, optionally naming the offending value."""
    where = f" for {context}" if context else ""
    if value is None:
        text = f"limit '{limit.name}'{where} is {limit}"
    else:
        text = f"{_format_value(limit, value)}{where} exceeds the limit '{limit.name}' ({limit})"
    if limit.note:
        text += f" — {limit.note}"
    if limit.doc:
        text += f" See {limit.doc}"
    return text


def _format_value(limit: Limit, value: int) -> str:
    if limit.unit == "bytes":
        return _human_bytes(value)
    return f"{value:,} {limit.unit}".strip()


def warn_if_exceeds(limit: Limit, value: int, *, context: str = "", stacklevel: int = 3) -> bool:
    """Warn when ``value`` is over ``limit``. Returns whether it warned."""
    if not limit.exceeds(value):
        return False
    warnings.warn(hint(limit, context=context, value=value), UserWarning, stacklevel=stacklevel)
    return True


def ensure_within(
    limit: Limit,
    value: int,
    *,
    context: str = "",
    on_exceed: str = "raise",
) -> None:
    """Enforce ``limit`` for ``value`` — raise :class:`LimitExceededError` or warn.

    Args:
        on_exceed: ``"raise"`` (default) or ``"warn"``.
    """
    if on_exceed not in _ON_EXCEED:
        raise ValueError(f"on_exceed must be one of {_ON_EXCEED}, got {on_exceed!r}")
    if not limit.exceeds(value):
        return
    if on_exceed == "warn":
        warn_if_exceeds(limit, value, context=context, stacklevel=4)
    else:
        raise LimitExceededError(limit, value, context=context)


@dataclass(frozen=True)
class LimitDecl:
    """One declared limit — a :class:`Limit`, optionally bound to an argument.

    ``arg`` names the numeric argument the limit is enforced against (``None``
    for a documentation-only declaration); ``on_exceed`` / ``clamp`` decide the
    enforcement behaviour.
    """

    limit: Limit
    arg: Optional[str] = None
    on_exceed: str = "warn"
    clamp: bool = False


def _append_doc(target: Callable[..., Any], decls: Tuple[LimitDecl, ...]) -> None:
    lines: list[str] = []
    for decl in decls:
        bound = f" (<= {decl.limit})" if decl.arg else ""
        lines.append(f"      {decl.limit.name}: {decl.limit}{bound}")
    if lines:
        target.__doc__ = (target.__doc__ or "") + "\n    Limits:\n" + "\n".join(lines)


@overload
def limit(
    *limits: Limit,
    arg: None = ...,
    on_exceed: str = ...,
    clamp: bool = ...,
) -> Callable[[T], T]: ...


@overload
def limit(
    *limits: Limit,
    arg: str,
    on_exceed: str = ...,
    clamp: bool = ...,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


def limit(
    *limits: Limit,
    arg: Optional[str] = None,
    on_exceed: str = "warn",
    clamp: bool = False,
) -> Any:
    """Declare service limits on a class, method or property (and optionally enforce one).

    Metadata-only by default (like ``@odata`` / ``@require_permission``): the
    declared :class:`Limit` values are stamped on the target and appended to its
    docstring, then collected into the model's schema.
    Pass ``arg`` to also enforce that argument against the (single) limit — warn
    by default, ``on_exceed="raise"`` to raise, or ``clamp=True`` to lower it
    (methods only).

    Usage::

        @limit(Limits.FILE_UPLOAD)  # document
        @limit(Limits.LIST_VIEW, arg="page_size")  # document + warn
        @limit(Limits.BATCH_ITEMS, arg="items_per_batch", on_exceed="raise")
        @limit(*IDENTITY_QUOTAS)  # on a class
        class DirectoryObject(Entity): ...

    Args:
        *limits: The :class:`Limit` values to declare.
        arg: Argument name to enforce (requires exactly one limit).
        on_exceed: ``"warn"`` (default) or ``"raise"``.
        clamp: Lower the argument to the limit instead of warning/raising.
    """
    if arg is not None and len(limits) != 1:
        raise ValueError("arg= requires exactly one limit")
    if on_exceed not in _ON_EXCEED:
        raise ValueError(f"on_exceed must be one of {_ON_EXCEED}, got {on_exceed!r}")

    decls = tuple(
        LimitDecl(limit=item, arg=arg if index == 0 else None, on_exceed=on_exceed, clamp=clamp)
        for index, item in enumerate(limits)
    )

    def decorator(func: Any) -> Any:
        if isinstance(func, type):
            if arg is not None:
                raise ValueError("arg= cannot be used on a class")
            from office365.runtime.schema import TypeSchema

            _stamp(func, decls)
            # ``__init_subclass__`` ran before this decorator, so the schema was built
            # without this declaration. Rebuild it — idempotent, the getters still carry
            # their own markers — rather than patch one field of a frozen object.
            func._schema = TypeSchema.build(func)
            register_catalog(func)
            return func
        if isinstance(func, property):
            if arg is not None:
                raise ValueError("arg= cannot be used on a property (properties take no arguments)")
            _stamp(func.fget, decls)
            return func

        _stamp(func, decls)
        if arg is None:
            return func

        arg_name: str = arg
        signature = inspect.signature(func)
        enforced = decls[0]

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound = signature.bind_partial(*args, **kwargs)
            value: Any = bound.arguments.get(arg_name)
            if value is None or not enforced.limit.exceeds(value):
                return func(*args, **kwargs)
            if enforced.clamp:
                bound.arguments[arg_name] = enforced.limit.value
                return func(*bound.args, **bound.kwargs)
            if enforced.on_exceed == "raise":
                raise LimitExceededError(enforced.limit, value, context=func.__qualname__)
            warn_if_exceeds(enforced.limit, value, context=func.__qualname__, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _stamp(target: Any, decls: Tuple[LimitDecl, ...]) -> None:
    setattr(target, _LIMIT_MARKER, decls)
    _append_doc(target, decls)


_limit = limit  # module alias (the ``bounded`` param name shadows ``limit`` below)


def bounded(
    arg: str,
    limit: Limit,
    *,
    on_exceed: str = "warn",
    clamp: bool = False,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Back-compat: ``@bounded(arg, limit)`` is ``@limit(limit, arg=arg)``."""
    return _limit(limit, arg=arg, on_exceed=on_exceed, clamp=clamp)


def collect_limit_meta(cls: type) -> dict[str, Tuple[LimitDecl, ...]]:
    """Collect ``@limit`` declarations from a class's methods/properties.

    Called from :meth:`TypeSchema.build` so a class carries its own limits — keyed by
    attribute/method name, inheriting the base class's entries.
    """
    # The base class's declarations are inherited through its schema. Naming the
    # attribute rather than importing ``TypeSchema`` keeps this module free of a cycle:
    # ``schema`` imports the limit types, so the dependency can only run one way.
    inherited_schema = getattr(cls, "_schema", None)
    meta: dict[str, Tuple[LimitDecl, ...]] = dict(getattr(inherited_schema, "member_limits", {}))
    for attr_name, attr in cls.__dict__.items():
        target = attr.fget if isinstance(attr, property) else attr
        decls = getattr(target, _LIMIT_MARKER, None)
        if decls is not None:
            meta[attr_name] = decls
    return meta


@runtime_checkable
class LimitCatalog(Protocol):
    """A source of :class:`Limit` values — anything with a ``catalog()`` method."""

    def catalog(self) -> Iterable[Limit]: ...


#: Registered limit sources, keyed by product (``"model"`` for ``@limit`` classes).
_SOURCES: dict[str, list[Any]] = {}


def _limits_from(source: Any) -> list[Limit]:
    if isinstance(source, (list, tuple)):
        return list(source)
    catalog_fn = getattr(source, "catalog", None)
    if catalog_fn is not None:
        return list(catalog_fn())
    declared = getattr(source, "declared_limits", None)
    if declared is not None:
        return list(declared())
    raise TypeError(f"{source!r} is not a Limit catalog (needs catalog()/declared_limits() or be a sequence)")


def register_catalog(*sources: Any, product: str = "model") -> None:
    """Register limit sources — catalogs (``catalog()``), classes, or plain sequences.

    A product catalog is a tuple of :class:`Limit` rows or an object that answers
    ``catalog()``; a ``@limit``-decorated class answers ``declared_limits()``. Sources
    register themselves at import time (e.g. ``register_catalog(OUTLOOK_QUOTAS,
    product="outlook")``); ``@limit`` on a class registers that class automatically
    (under ``product="model"``).
    """
    bucket = _SOURCES.setdefault(product, [])
    for source in sources:
        if source not in bucket:
            bucket.append(source)


def catalog(product: Optional[str] = None) -> list[Limit]:
    """All registered limits (optionally for one product), de-duplicated by identity."""
    products = [product] if product is not None else list(_SOURCES)
    seen: set[int] = set()
    result: list[Limit] = []
    for name in products:
        for source in _SOURCES.get(name, ()):
            for item in _limits_from(source):
                if id(item) not in seen:
                    seen.add(id(item))
                    result.append(item)
    return result


def catalog_products() -> list[str]:
    """The registered products, in registration order — the keys :func:`catalog` accepts."""
    return list(_SOURCES)


def collect_class_limits(cls: type) -> Tuple[LimitDecl, ...]:
    """The class-level ``@limit`` declarations of ``cls``.

    Accumulates up the hierarchy: the base class's declarations plus the class's
    own (a subclass is subject to both).
    """
    inherited = getattr(getattr(cls, "_schema", None), "class_limits", ())
    own = cls.__dict__.get(_LIMIT_MARKER)
    if own is None:
        return inherited
    return (*inherited, *own)


def limits_of(target: Any) -> Tuple[LimitDecl, ...]:
    """The limits declared on a method/property, or a class's collected limits.

    Args:
        target: A callable (reads ``__limit_decls__``), a ``property``, or a
            class (reads the ``member_limits`` of its schema).
    """
    if isinstance(target, type):
        member_limits = getattr(getattr(target, "_schema", None), "member_limits", {})
        return tuple(decl for decls in member_limits.values() for decl in decls)
    if isinstance(target, property):
        target = target.fget
    return tuple(getattr(target, _LIMIT_MARKER, ()))


@dataclass
class LimitReport:
    """Diagnostic result of inspecting the limits declared on a target.

    ``violations`` holds the ``(decl, value)`` pairs whose supplied value is over
    the limit. This never raises and never touches the network.
    """

    target: str
    decls: Tuple[LimitDecl, ...] = ()
    violations: Tuple[Tuple[LimitDecl, int], ...] = field(default_factory=tuple)

    @property
    def limits(self) -> Tuple[Limit, ...]:
        return tuple(decl.limit for decl in self.decls)

    @property
    def ok(self) -> bool:
        """Whether all supplied values are within their limits."""
        return not self.violations

    def __str__(self) -> str:
        head = f"{self.target}: {len(self.decls)} limit(s)"
        if self.violations:
            over = ", ".join(f"{decl.limit.name}={value:,}" for decl, value in self.violations)
            return f"{head}; over: {over}"
        return head


def verify_limits(target: Any, **values: int) -> LimitReport:
    """Inspect the limits declared on a method/property/class (diagnostic-only).

    Keyword ``values`` are checked against the arg-bound declarations
    (``@limit(..., arg=...)``); other limits are reported for reference.

    Args:
        target: A callable, ``property``, or class.
        **values: Argument name -> value to check.

    Returns:
        A :class:`LimitReport`.
    """
    name = getattr(target, "__qualname__", None) or getattr(target, "__name__", str(target))
    decls = limits_of(target)
    violations = tuple(
        (decl, values[decl.arg])
        for decl in decls
        if decl.arg is not None and decl.arg in values and decl.limit.exceeds(values[decl.arg])
    )
    return LimitReport(target=name, decls=decls, violations=violations)


#: The one vendor-wide ceiling: every Microsoft Graph request, whatever the product,
#: counts against the calling app's global budget. It lives here rather than in a
#: product catalog because no single product owns it — a SharePoint workload and a
#: Teams workload spend from the same budget once both go through Graph.
GLOBAL_QUOTAS = (
    Limit(
        "any Microsoft Graph request",
        130_000,
        LimitKind.SUPPORTED,
        "requests",
        "app",
        note="across all tenants",
        doc="https://learn.microsoft.com/en-us/graph/throttling-limits",
        window_seconds=10,
    ),
)

register_catalog(GLOBAL_QUOTAS, product="graph")
