"""The JSON dialects this client speaks, expressed as data.

SharePoint's OData V3 JSON (``odata=verbose|minimalmetadata|nometadata``) and
Microsoft Graph's OData V4 JSON differ only in *how they spell control
information*: whether a payload is wrapped in ``d``, whether a collection is
named ``results`` or ``value``, whether the entity type arrives as a
``__metadata`` object or as an ``@odata.type`` string. Each of those
differences used to be an ``isinstance(format, JsonLightFormat)`` check spread
over the runtime; here it is a field of a frozen value, so a dialect is a row
in a table rather than a branch in the code.

A dialect answers only *"what is this key called, and is this entry control
information?"*. The behaviour built on those answers — which columns enter a
payload, how a response is walked back into a model — lives in
:class:`~office365.runtime.odata.json_format.JsonProfile`.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Optional

from office365.runtime.odata.v3.metadata_level import ODataV3MetadataLevel


@dataclass(frozen=True)
class JsonDialect:
    """How one OData JSON dialect spells its control information."""

    container: Optional[str] = None
    """Key wrapping every response payload (JSON Light: ``d``); ``None`` means unwrapped."""

    collection: str = "value"
    """Key naming a collection payload."""

    collection_next: str = "@odata.nextLink"
    """Key holding the link to the next page of a collection."""

    collection_delta: str = "@odata.deltaLink"
    """Key holding the link to the delta (change-tracking) page."""

    type_marker: str = "@odata.type"
    """Key (or, for JSON Light, object) carrying the entity's type name."""

    type_wrapped: bool = False
    """``True`` writes ``{"type": name}``, ``False`` writes ``"#name"``."""

    etag: str = "@odata.etag"
    """Key carrying the entity tag, ingested as the local ``__etag`` property."""

    control_prefix: Optional[str] = None
    """Any key containing this is control information; ``None`` means keys are named explicitly."""

    control_aliases: Mapping[str, str] = field(default_factory=dict)
    """Scalar control keys that are ingested under a local name instead of dropped."""

    deferred: Optional[str] = None
    """Key marking a navigation property the service chose not to expand."""

    enum_by_name: bool = True
    """``True`` writes an enum member's name, ``False`` its numeric value."""

    tunnels_methods: bool = False
    """``True`` tunnels ``MERGE``/``DELETE`` through ``X-HTTP-Method`` on a ``POST``."""

    paginates_by_offset: bool = False
    """``True`` honours ``$skip``; ``False`` paginates by server-supplied link only."""

    def dropped(self, name: str, value: Any) -> bool:
        """Whether ``name``/``value`` is control information the entity never stores."""
        if name in self.control_aliases:
            return True
        if self.control_prefix is not None and self.control_prefix in name:
            return True
        if name == self.type_marker:
            return True
        return self.deferred is not None and isinstance(value, dict) and self.deferred in value

    def alias(self, name: str) -> Optional[str]:
        """The local name a scalar control key is ingested under (``__etag``), if any."""
        return self.control_aliases.get(name)


V4 = JsonDialect(control_aliases={"@odata.etag": "__etag", "@odata.type": "__odata_type"})
"""Microsoft Graph / OData V4 JSON."""

V3_VERBOSE = JsonDialect(
    container="d",
    collection="results",
    collection_next="__next",
    collection_delta="__delta",
    type_marker="__metadata",
    type_wrapped=True,
    etag="__etag",
    control_aliases={"__metadata": "__odata_type"},
    deferred="__deferred",
    enum_by_name=False,
    tunnels_methods=True,
    paginates_by_offset=True,
)
"""SharePoint REST JSON Light at ``odata=verbose``."""

V3_MINIMAL = replace(V3_VERBOSE, collection="value")
"""SharePoint REST JSON Light at ``odata=minimalmetadata``/``nometadata``: the
collection key shortens to ``value``; nothing else about the spelling changes."""

_V3_BY_LEVEL: Mapping[Any, JsonDialect] = {
    ODataV3MetadataLevel.Verbose: V3_VERBOSE,
    ODataV3MetadataLevel.MinimalMetadata: V3_MINIMAL,
    ODataV3MetadataLevel.NoMetadata: V3_MINIMAL,
}


def dialect_for_level(metadata_level: Any) -> JsonDialect:
    """The JSON Light dialect a SharePoint metadata level selects."""
    return _V3_BY_LEVEL.get(metadata_level, V3_VERBOSE)
