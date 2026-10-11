"""Declarative OData query-option capabilities for collections.

Some Microsoft Graph feeds reject standard OData query options — the
``callRecords`` feed rejects ``$top`` with *"Query option 'Top' is not allowed.
To allow it, set the 'AllowedQueryOptions' property on EnableQueryAttribute or
QueryValidationSettings."* Those named knobs are **server-side** ASP.NET OData
configuration a client cannot change, so the library declares the *exceptions*
on the collection and guards its fluent query-option setters before a request is
sent.

The same server-side configuration also restricts *individual properties*: a
drive's ``$filter`` cannot touch ``size`` (SharePoint maps it to
``SMTotalFileStreamSize``, which it refuses to evaluate), and filtering
``driveItem.lastModifiedDateTime`` requires a ``Prefer`` header. Those are
expressed here too — declare the offending properties (``unsupported_filter`` /
``unsupported_orderby``) and the headers the endpoint needs when a property is
referenced (``prefer``), and the collection validates/injects them at the seam.

This mirrors the ``@odata`` / ``@limit`` / ``@require_permission`` family: declare
on the model (a ``ClientObjectCollection`` subclass), collect the metadata on the
class, and enforce it at the seam (``top`` / ``skip`` / ``order_by`` / ``filter``
/ ``select`` / ``expand`` — and therefore ``paged`` / ``get_all``).

    >>> from office365.runtime.query_capabilities import query_capabilities
    >>> @query_capabilities(unsupported={"top"}, unsupported_filter={"size"}, doc=_DOC)
    ... class CallRecordCollection(EntityCollection[CallRecord]): ...
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping, Optional

#: Attribute the decorator stamps the :class:`QueryCapability` onto.
_QUERY_CAPABILITY_MARKER = "__query_capability__"
_ON_UNSUPPORTED = ("raise", "warn")

#: Quoted OData string literals (single-quoted, ``''`` escapes a quote).
_STRING_LITERAL = re.compile(r"'(?:[^']|'')*'")
#: Unquoted ISO-8601 date/time literals (``2020-01-01T00:00:00Z``). Masked because
#: their ``T``/``Z``/offset fragments look like identifiers to a naive scan.
_DATETIME_LITERAL = re.compile(r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?")
#: A bare identifier (property, function or keyword).
_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
#: OData operators / literals that are never property names.
_NON_PROPERTY_TOKENS = frozenset(
    {
        "eq",
        "ne",
        "gt",
        "ge",
        "lt",
        "le",
        "and",
        "or",
        "not",
        "in",
        "add",
        "sub",
        "mul",
        "div",
        "mod",
        "has",
        "null",
        "true",
        "false",
    }
)

#: How each option is spelled in a user-facing hint.
_OPTION_LABELS = {"filter": "$filter", "order_by": "$orderby"}


def referenced_properties(expression: Optional[str]) -> frozenset[str]:
    """The property names referenced by an OData expression (best effort).

    Quoted string literals are ignored, function names (an identifier followed
    by ``(``) are skipped, and OData operators/literals are excluded. A nested
    path such as ``fields/customField`` contributes both ``fields`` and
    ``customField`` — callers intersect the result with a declared property set,
    so the extra tokens are harmless.

    Args:
        expression: The raw ``$filter`` / ``$orderby`` expression (or ``None``).
    """
    if not expression:
        return frozenset()
    text = _DATETIME_LITERAL.sub("''", _STRING_LITERAL.sub("''", expression))
    return frozenset(
        match.group(0)
        for match in _IDENTIFIER.finditer(text)
        if match.group(0) not in _NON_PROPERTY_TOKENS and not text[match.end() :].lstrip().startswith("(")
    )


def _normalize(option: str) -> str:
    """Normalize an option name to the ``QueryOptions`` field form (``top``)."""
    return option.strip().lstrip("$").lower().replace("-", "_")


def _option_label(option: str) -> str:
    option = _normalize(option)
    return _OPTION_LABELS.get(option, f"${option}")


@dataclass(frozen=True)
class QueryCapability:
    """Which OData query options a collection/endpoint accepts.

    ``unsupported`` / ``unsupported_filter`` / ``unsupported_orderby`` are
    deny-lists — declare only what is rejected. ``allowed`` / ``filterable`` /
    ``orderable`` are the inverse allow-lists for a feed that accepts a fixed
    set. For each pair only one side is set.

    ``prefer`` maps a referenced property token to a ``Prefer`` header value the
    endpoint requires when that property appears in a query expression (for
    example ``lastModifiedDateTime`` on a drive item).
    """

    unsupported: frozenset[str] = frozenset()
    allowed: Optional[frozenset[str]] = None
    unsupported_filter: frozenset[str] = frozenset()
    filterable: Optional[frozenset[str]] = None
    unsupported_orderby: frozenset[str] = frozenset()
    orderable: Optional[frozenset[str]] = None
    prefer: Mapping[str, str] = field(default_factory=dict)
    on_unsupported: str = "raise"
    doc: str = ""
    note: str = ""

    def supports(self, option: str) -> bool:
        """Whether ``option`` (e.g. ``"top"`` or ``"$top"``) is accepted."""
        option = _normalize(option)
        if self.allowed is not None:
            return option in self.allowed
        return option not in self.unsupported

    def filter_violations(self, expression: Optional[str]) -> tuple[str, ...]:
        """Properties an expression references that ``$filter`` may not touch."""
        return self._property_violations(expression, self.filterable, self.unsupported_filter)

    def orderby_violations(self, expression: Optional[str]) -> tuple[str, ...]:
        """Properties an expression references that ``$orderby`` may not touch."""
        return self._property_violations(expression, self.orderable, self.unsupported_orderby)

    @staticmethod
    def _property_violations(
        expression: Optional[str],
        allowed: Optional[frozenset[str]],
        denied: frozenset[str],
    ) -> tuple[str, ...]:
        referenced = referenced_properties(expression)
        if allowed is not None:
            return tuple(sorted(referenced - allowed))
        if not denied:
            return ()
        return tuple(sorted(referenced & denied))

    def preference_values(self, *expressions: Optional[str]) -> tuple[str, ...]:
        """``Prefer`` values required by the properties referenced across expressions."""
        if not self.prefer:
            return ()
        values: list[str] = []
        for expression in expressions:
            for prop in referenced_properties(expression):
                value = self.prefer.get(prop)
                if value and value not in values:
                    values.append(value)
        return tuple(values)


class QueryOptionNotSupportedError(ValueError):
    """Raised when a collection is asked for a query option its endpoint rejects."""

    def __init__(self, owner: type, option: str, capability: QueryCapability) -> None:
        self.owner = owner
        self.option = _normalize(option)
        self.capability = capability
        super().__init__(hint(owner, option, capability))


class QueryPropertyNotSupportedError(ValueError):
    """Raised when a filter/order expression touches a property the endpoint rejects."""

    def __init__(self, owner: type, option: str, property_name: str, capability: QueryCapability) -> None:
        self.owner = owner
        self.option = _normalize(option)
        self.property_name = property_name
        self.capability = capability
        super().__init__(property_hint(owner, option, property_name, capability))


def hint(owner: type, option: str, capability: QueryCapability) -> str:
    """An actionable message for an unsupported query option."""
    option = _normalize(option)
    text = f"{owner.__name__} does not support ${option}"
    if capability.note:
        text += f" — {capability.note}"
    text += f"; bound the result client-side instead of calling .{option}(...)"
    if capability.doc:
        text += f". See {capability.doc}"
    return text


def property_hint(owner: type, option: str, property_name: str, capability: QueryCapability) -> str:
    """An actionable message for an unsupported filter/order property."""
    label = _option_label(option)
    verb = "filter on" if _normalize(option) == "filter" else "sort by"
    text = f"{owner.__name__} cannot {verb} '{property_name}' ({label})"
    if capability.note:
        text += f" — {capability.note}"
    text += "; use a different property or do it client-side"
    if capability.doc:
        text += f". See {capability.doc}"
    return text


def _append_doc(target: type, capability: QueryCapability) -> None:
    lines: list[str] = []
    if capability.allowed is not None:
        lines.append(f"allowed: {', '.join(sorted(capability.allowed)) or 'none'}")
    else:
        lines.append(f"unsupported: {', '.join(sorted(capability.unsupported)) or 'none'}")
    if capability.filterable is not None:
        lines.append(f"filterable: {', '.join(sorted(capability.filterable)) or 'none'}")
    if capability.unsupported_filter:
        lines.append(f"non-filterable: {', '.join(sorted(capability.unsupported_filter))}")
    if capability.orderable is not None:
        lines.append(f"orderable: {', '.join(sorted(capability.orderable)) or 'none'}")
    if capability.unsupported_orderby:
        lines.append(f"non-orderable: {', '.join(sorted(capability.unsupported_orderby))}")
    if capability.prefer:
        lines.append(f"prefer: {', '.join(sorted(capability.prefer))}")
    target.__doc__ = (target.__doc__ or "") + f"\n    Query options ({'; '.join(lines)}).\n"


def query_capabilities(
    *,
    unsupported: Optional[Iterable[str]] = None,
    allowed: Optional[Iterable[str]] = None,
    unsupported_filter: Optional[Iterable[str]] = None,
    filterable: Optional[Iterable[str]] = None,
    unsupported_orderby: Optional[Iterable[str]] = None,
    orderable: Optional[Iterable[str]] = None,
    prefer: Optional[Mapping[str, str]] = None,
    on_unsupported: str = "raise",
    doc: str = "",
    note: str = "",
) -> Callable[[type], type]:
    """Declare which OData query options a collection class accepts.

    Args:
        unsupported: Options the endpoint rejects (deny-list), e.g. ``{"top"}``.
        allowed: The exact set the endpoint accepts (allow-list). Mutually
            exclusive with ``unsupported``.
        unsupported_filter: Properties ``$filter`` may not reference.
        filterable: The only properties ``$filter`` may reference (allow-list).
        unsupported_orderby: Properties ``$orderby`` may not reference.
        orderable: The only properties ``$orderby`` may reference (allow-list).
        prefer: Property token -> ``Prefer`` header value required when that
            property appears in a query expression.
        on_unsupported: ``"raise"`` (default) or ``"warn"`` — the latter warns
            and continues. A rejected option is ignored; a rejected *property*
            is still sent (silently dropping part of a filter would change its
            meaning), so the warning is a caution, not a rewrite.
        doc: Link to the endpoint documentation.
        note: Extra guidance surfaced in the error or warning.

    Returns:
        A class decorator for a ``ClientObjectCollection`` subclass.
    """
    for option, property_set in (
        ("unsupported", unsupported),
        ("allowed", allowed),
        ("unsupported_filter", unsupported_filter),
        ("filterable", filterable),
        ("unsupported_orderby", unsupported_orderby),
        ("orderable", orderable),
    ):
        if property_set is None:
            continue
        if not all(isinstance(item, str) for item in property_set):
            raise TypeError(f"{option}=() must contain strings")
    if unsupported is not None and allowed is not None:
        raise ValueError("pass either unsupported= or allowed=, not both")
    if unsupported_filter is not None and filterable is not None:
        raise ValueError("pass either unsupported_filter= or filterable=, not both")
    if unsupported_orderby is not None and orderable is not None:
        raise ValueError("pass either unsupported_orderby= or orderable=, not both")
    if on_unsupported not in _ON_UNSUPPORTED:
        raise ValueError(f"on_unsupported must be one of {_ON_UNSUPPORTED}, got {on_unsupported!r}")

    capability = QueryCapability(
        unsupported=frozenset(_normalize(option) for option in (unsupported or ())),
        allowed=frozenset(_normalize(option) for option in allowed) if allowed is not None else None,
        unsupported_filter=frozenset(unsupported_filter or ()),
        filterable=frozenset(filterable) if filterable is not None else None,
        unsupported_orderby=frozenset(unsupported_orderby or ()),
        orderable=frozenset(orderable) if orderable is not None else None,
        prefer=dict(prefer or {}),
        on_unsupported=on_unsupported,
        doc=doc,
        note=note,
    )

    def decorator(target: type) -> type:
        if not isinstance(target, type):
            raise TypeError("@query_capabilities applies to a class (a ClientObjectCollection subclass)")
        setattr(target, _QUERY_CAPABILITY_MARKER, capability)
        target._query_capability_decl = capability
        _append_doc(target, capability)
        return target

    return decorator


def query_capabilities_of(target: object) -> Optional[QueryCapability]:
    """The :class:`QueryCapability` declared on a class (or instance), if any."""
    cls = target if isinstance(target, type) else type(target)
    return getattr(cls, "_query_capability_decl", None)


__all__ = [
    "QueryCapability",
    "QueryOptionNotSupportedError",
    "QueryPropertyNotSupportedError",
    "hint",
    "property_hint",
    "query_capabilities",
    "query_capabilities_of",
    "referenced_properties",
]
