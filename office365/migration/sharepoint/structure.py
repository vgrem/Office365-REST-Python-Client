"""Capture and recreate a SharePoint list's *structure* (columns, content types, views).

A whole-site migration recreates each target list container, but content copied
into a list whose custom columns/content types/views do not exist yet has nowhere
to land. This module takes a **read-only, serializable snapshot** of a source
list's structure (:func:`capture_list_structure`) and can replay it onto a target
list (:func:`provision_list_structure`) before content is copied.

``capture_list_structure`` performs GETs only — it never writes. The snapshot is
a plain tree of dataclasses that round-trips through :meth:`ListStructure.to_dict`
/ :meth:`ListStructure.from_dict` (JSON-friendly), so a plan can be captured once
and replayed.

Scope, deliberately:

* **Fields** — user-defined list columns with their ``SchemaXml`` prepared for
  ``CreateFieldAsXml`` (see :meth:`~office365.sharepoint.fields.field.Field.schema_xml_for_copy`).
  Built-in/system columns and framework columns injected by SharePoint features
  (hidden, or not deletable) are skipped — a target list already has them. A
  **lookup** column's schema names the list it points at; replayed verbatim it
  would name the *source* list id, so it is repointed at the matching target list
  (or skipped with a warning when that list is not part of the migration).
* **Content types** — non-hidden content types with their ordered field links.
* **Views** — non-hidden, non-personal views with their ordered columns.

Provisioning is idempotent: with ``on_conflict="skip"`` (default) it only creates
what is missing, so a re-run is a no-op. The server assigns content type
identifiers, so content types are matched and recreated **by name** (their
``Id`` cannot be preserved over REST); field links are reconciled best-effort
and any column the server refuses to link is reported back to the caller.
Built-in columns the target list already provides are left alone rather than
sent as guaranteed link failures.
"""

from __future__ import annotations

import logging
import re
from dataclasses import asdict, dataclass
from dataclasses import field as dc_field
from typing import Any, Dict, List, Optional

from office365.migration.map import ContentTypeMap
from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.fields.builtin_field_name import SYSTEM_FIELD_NAMES

logger = logging.getLogger(__name__)

__all__ = [
    "ContentTypeDefinition",
    "FieldDefinition",
    "ListStructure",
    "ViewDefinition",
    "capture_list_structure",
    "normalize_guid",
    "provision_list_structure",
    "rewrite_lookup_schema",
]

#: Field properties requested per column. ``SchemaXml`` is explicit because it is
#: the payload used to recreate the column on another list.
_FIELD_SELECT = [
    "Id",
    "InternalName",
    "Title",
    "FieldTypeKind",
    "TypeAsString",
    "SchemaXml",
    "Required",
    "Hidden",
    "ReadOnlyField",
    "FromBaseType",
    "CanBeDeleted",
    "Group",
    "Description",
]


@dataclass
class FieldDefinition:
    """A single list column, ready to recreate via ``CreateFieldAsXml``."""

    internal_name: str
    title: Optional[str] = None
    field_type_kind: Optional[int] = None
    type_as_string: Optional[str] = None
    schema_xml: Optional[str] = None
    required: Optional[bool] = None
    hidden: Optional[bool] = None
    read_only: Optional[bool] = None
    from_base_type: Optional[bool] = None
    can_be_deleted: Optional[bool] = None
    group: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FieldDefinition":
        return cls(
            internal_name=data.get("internal_name", ""),
            title=data.get("title"),
            field_type_kind=data.get("field_type_kind"),
            type_as_string=data.get("type_as_string"),
            schema_xml=data.get("schema_xml"),
            required=data.get("required"),
            hidden=data.get("hidden"),
            read_only=data.get("read_only"),
            from_base_type=data.get("from_base_type"),
            can_be_deleted=data.get("can_be_deleted"),
            group=data.get("group"),
            description=data.get("description"),
        )


@dataclass
class ContentTypeDefinition:
    """A content type bound to the list, with its field links in display order."""

    string_id: str
    name: Optional[str] = None
    group: Optional[str] = None
    description: Optional[str] = None
    hidden: Optional[bool] = None
    sealed: Optional[bool] = None
    read_only: Optional[bool] = None
    field_internal_names: List[str] = dc_field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentTypeDefinition":
        return cls(
            string_id=data.get("string_id", ""),
            name=data.get("name"),
            group=data.get("group"),
            description=data.get("description"),
            hidden=data.get("hidden"),
            sealed=data.get("sealed"),
            read_only=data.get("read_only"),
            field_internal_names=list(data.get("field_internal_names") or []),
        )


@dataclass
class ViewDefinition:
    """A list view, with its columns in display order."""

    title: str
    view_type: Optional[str] = None
    row_limit: Optional[int] = None
    paged: Optional[bool] = None
    hidden: Optional[bool] = None
    default_view: Optional[bool] = None
    personal_view: Optional[bool] = None
    view_query: Optional[str] = None
    field_internal_names: List[str] = dc_field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ViewDefinition":
        return cls(
            title=data.get("title", ""),
            view_type=data.get("view_type"),
            row_limit=data.get("row_limit"),
            paged=data.get("paged"),
            hidden=data.get("hidden"),
            default_view=data.get("default_view"),
            personal_view=data.get("personal_view"),
            view_query=data.get("view_query"),
            field_internal_names=list(data.get("field_internal_names") or []),
        )


@dataclass
class ListStructure:
    """A serializable snapshot of a list's container metadata and structure."""

    title: Optional[str] = None
    base_template: Optional[int] = None
    base_type: Optional[int] = None
    description: Optional[str] = None
    content_types_enabled: Optional[bool] = None
    fields: List[FieldDefinition] = dc_field(default_factory=list)
    content_types: List[ContentTypeDefinition] = dc_field(default_factory=list)
    views: List[ViewDefinition] = dc_field(default_factory=list)

    @property
    def is_document_library(self) -> bool:
        """Whether the captured list is a document library (``BaseType`` 1)."""
        return self.base_type == 1

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-friendly dict (nested dataclasses are expanded)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListStructure":
        """Rebuild a snapshot from :meth:`to_dict` output (unknown keys ignored)."""
        return cls(
            title=data.get("title"),
            base_template=data.get("base_template"),
            base_type=data.get("base_type"),
            description=data.get("description"),
            content_types_enabled=data.get("content_types_enabled"),
            fields=[FieldDefinition.from_dict(item) for item in data.get("fields") or []],
            content_types=[ContentTypeDefinition.from_dict(item) for item in data.get("content_types") or []],
            views=[ViewDefinition.from_dict(item) for item in data.get("views") or []],
        )


def capture_list_structure(sp_list: Any) -> ListStructure:
    """Read a SharePoint list's structure into a :class:`ListStructure` snapshot.

    Issues only GET requests. Loads the list's scalar properties, its columns,
    the non-hidden content types (with their field links), and the non-hidden
    views (with their columns).

    Args:
        sp_list: A ``List`` (possibly not yet loaded); it is loaded in place.

    Returns:
        A fully-populated, serializable snapshot.
    """
    sp_list.ensure_properties(
        ["Title", "BaseTemplate", "BaseType", "Description", "ContentTypesEnabled"]
    ).execute_query()

    structure = ListStructure(
        title=getattr(sp_list, "title", None),
        base_template=getattr(sp_list, "base_template", None),
        base_type=getattr(sp_list, "base_type", None),
        description=getattr(sp_list, "description", None),
        content_types_enabled=getattr(sp_list, "content_types_enabled", None),
    )

    loaded_fields = sp_list.fields.select(list(_FIELD_SELECT)).get().execute_query()
    structure.fields = [_field_definition(field) for field in loaded_fields if _is_capturable_field(field)]

    for content_type in sp_list.content_types.get().execute_query():
        if not _is_capturable_content_type(content_type):
            continue
        links = content_type.field_links.get().execute_query()
        structure.content_types.append(_content_type_definition(content_type, links))

    for view in sp_list.views.get().execute_query():
        if getattr(view, "hidden", False) or getattr(view, "personal_view", False):
            continue
        field_names = list(view.view_fields.get().execute_query())
        structure.views.append(_view_definition(view, field_names))

    return structure


def _is_capturable_field(field: Any) -> bool:
    """Only recreatable user columns — not built-in, framework, or hidden fields.

    Built-in/system fields are already present on any target list, and framework
    columns injected by SharePoint features (shortcuts, media, sensitivity
    labels, ...) cannot be recreated meaningfully. A list-scoped, deletable,
    visible column is what a user actually added.
    """
    name = getattr(field, "internal_name", None)
    if not name or name in SYSTEM_FIELD_NAMES:
        return False
    if getattr(field, "from_base_type", None) is True:
        return False
    if getattr(field, "can_be_deleted", None) is False:
        return False
    return getattr(field, "hidden", None) is not True


def _is_capturable_content_type(content_type: Any) -> bool:
    """Content types that carry useful, recreatable structure (non-hidden, identified)."""
    return bool(getattr(content_type, "string_id", None)) and not getattr(content_type, "hidden", False)


#: Content types in this length range are base types (Item ``0x01``, Document
#: ``0x0101``, ...); custom content types append a 32-hex-digit GUID.
_MIN_CUSTOM_CONTENT_TYPE_ID_LENGTH = 20

#: A GUID, optionally wrapped in the braces SharePoint uses in ``SchemaXml``.
_GUID_RE = re.compile(r"^\{?[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}?$")
#: ``Type="Lookup"`` / ``Type="LookupMulti"`` — the columns that name their list.
_LOOKUP_TYPE_RE = re.compile(r'\bType="Lookup(?:Multi)?"')
#: The ``List="..."`` attribute a lookup column carries in its ``SchemaXml``.
_LIST_ATTR_RE = re.compile(r'\sList="([^"]*)"')


def normalize_guid(value: Any) -> Optional[str]:
    """A lower-cased, brace-stripped GUID, or ``None`` when not a GUID.

    Lookup schemas carry ``List="{...}"`` while the migration threads list ids
    around as plain strings; normalizing both sides keeps the lookup keyed by the
    same value regardless of case or brace style.
    """
    if value is None:
        return None
    text = str(value).strip()
    if text.startswith("{") and text.endswith("}"):
        text = text[1:-1]
    return text.lower() if _GUID_RE.match(text) else None


def rewrite_lookup_schema(
    schema_xml: Optional[str], list_id_map: Dict[str, str] | None
) -> tuple[Optional[str], Optional[str]]:
    """Repoint a lookup column's ``SchemaXml`` at the target list.

    A lookup column is recreated from its source ``SchemaXml``, which names the
    *source* list (``List="{source-guid}"``). Replayed verbatim onto another site
    the target column points at a list id that does not exist there, so the column
    is broken and every value written to it is silently dropped. Given a
    ``list_id_map`` (normalized source list id -> normalized target list id) this
    rewrites the attribute to the target list.

    Returns ``(schema, unresolved)``: the rewritten schema (or ``None`` when the
    field must be skipped), and the unresolved source list id when the referenced
    list is not part of the migration (so the caller can warn).
    """
    if not schema_xml or not _LOOKUP_TYPE_RE.search(schema_xml):
        return schema_xml, None
    match = _LIST_ATTR_RE.search(schema_xml)
    if match is None:
        return schema_xml, None
    referenced = normalize_guid(match.group(1))
    if referenced is None:
        # ``List="UserInfo"`` (the User column's user-information list) is a
        # keyword, portable as-is.
        return schema_xml, None
    target = (list_id_map or {}).get(referenced)
    if target is None:
        return None, referenced
    rewritten = f'{schema_xml[: match.start()]} List="{{{target}}}"{schema_xml[match.end() :]}'
    return rewritten, None


#: Managed-metadata column types; recreated through ``TaxonomyField.create`` below.
_TAXONOMY_TYPES = frozenset({"TaxonomyFieldType", "TaxonomyFieldTypeMulti"})


def _is_taxonomy_definition(definition: FieldDefinition) -> bool:
    """Whether a captured column is a managed-metadata (taxonomy) column."""
    if (definition.type_as_string or "") in _TAXONOMY_TYPES:
        return True
    schema = definition.schema_xml or ""
    return "TaxonomyFieldType" in schema and "<Name>TermSetId</Name>" in schema


def _taxonomy_property(schema_xml: Optional[str], name: str) -> Optional[str]:
    """Read a value from a taxonomy column's ``<Customization>`` property bag."""
    if not schema_xml:
        return None
    match = re.search(
        r"<Name>\s*" + re.escape(name) + r"\s*</Name>\s*<Value\b[^>]*>\s*([^<\s]+)\s*</Value>",
        schema_xml,
        re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def _taxonomy_allow_multiple(schema_xml: str) -> bool:
    match = re.search(r'\bMult="(TRUE|FALSE)"', schema_xml, re.IGNORECASE)
    if match:
        return match.group(1).upper() == "TRUE"
    return 'Type="TaxonomyFieldTypeMulti"' in schema_xml


def _ensure_taxonomy_field(sp_list: Any, definition: FieldDefinition, warnings: List[str]) -> None:
    """Recreate a managed-metadata column bound to the same term set on the target.

    A taxonomy column cannot be replayed from its ``SchemaXml``: that schema names
    the *source* web's hidden TaxonomyHiddenList and note field, so the copy ends
    up pointing at columns that do not exist on the target and every value is
    dropped. ``TaxonomyField.create`` lets SharePoint provision a fresh hidden
    note column and bind ``LookupList`` to the target web's TaxonomyHiddenList.
    """
    name = definition.internal_name
    term_set = _taxonomy_property(definition.schema_xml, "TermSetId")
    if not term_set:
        warning = f"taxonomy column '{name}' was not recreated: its term set id could not be read"
        logger.warning(warning)
        warnings.append(warning)
        return
    from office365.sharepoint.taxonomy.field import TaxonomyField

    try:
        TaxonomyField.create(
            sp_list.fields,
            name,
            term_set,
            _taxonomy_property(definition.schema_xml, "SspId"),
            _taxonomy_allow_multiple(definition.schema_xml or ""),
        )
    except Exception as exc:  # noqa: BLE001 - best effort, surfaced as a warning
        warning = f"taxonomy column '{name}' could not be recreated: {exc}"
        logger.warning(warning)
        warnings.append(warning)


def _is_provisionable_content_type(definition: ContentTypeDefinition) -> bool:
    """Skip base content types — they already exist on any target list."""
    return len(definition.string_id or "") >= _MIN_CUSTOM_CONTENT_TYPE_ID_LENGTH


def _schema_for_copy(field: Any) -> Optional[str]:
    """``SchemaXml`` stripped of origin attributes, when the field offers it."""
    copier = getattr(field, "schema_xml_for_copy", None)
    value: Any = copier() if callable(copier) else getattr(field, "schema_xml", None)
    return value


def _field_kind_int(field: Any) -> Optional[int]:
    kind = getattr(field, "field_type_kind", None)
    if kind is None:
        return None
    return int(getattr(kind, "value", kind))


def _field_definition(field: Any) -> FieldDefinition:
    return FieldDefinition(
        internal_name=field.internal_name or "",
        title=getattr(field, "title", None),
        field_type_kind=_field_kind_int(field),
        type_as_string=getattr(field, "type_as_string", None),
        schema_xml=_schema_for_copy(field),
        required=getattr(field, "required", None),
        hidden=getattr(field, "hidden", None),
        read_only=getattr(field, "read_only_field", None),
        from_base_type=getattr(field, "from_base_type", None),
        can_be_deleted=getattr(field, "can_be_deleted", None),
        group=getattr(field, "group", None),
        description=getattr(field, "description", None),
    )


def _content_type_definition(content_type: Any, links: Any) -> ContentTypeDefinition:
    return ContentTypeDefinition(
        string_id=content_type.string_id or "",
        name=getattr(content_type, "name", None),
        group=getattr(content_type, "group", None),
        description=getattr(content_type, "description", None),
        hidden=getattr(content_type, "hidden", None),
        sealed=getattr(content_type, "sealed", None),
        read_only=getattr(content_type, "read_only", None),
        field_internal_names=[name for name in (getattr(link, "field_internal_name", None) for link in links) if name],
    )


def _view_definition(view: Any, field_names: List[Any]) -> ViewDefinition:
    return ViewDefinition(
        title=view.title or "",
        view_type=getattr(view, "view_type", None),
        row_limit=getattr(view, "row_limit", None),
        paged=getattr(view, "paged", None),
        hidden=getattr(view, "hidden", None),
        default_view=getattr(view, "default_view", None),
        personal_view=getattr(view, "personal_view", None),
        view_query=getattr(view, "view_query", None),
        field_internal_names=[name for name in field_names if name],
    )


def provision_list_structure(
    sp_list: Any,
    structure: ListStructure,
    *,
    on_conflict: str = "skip",
    content_type_map: Dict[str, str] | None = None,
    list_id_map: Dict[str, str] | None = None,
) -> List[str]:
    """Recreate a captured list structure on ``sp_list`` (idempotent).

    Ensures the captured user columns exist (creating missing ones from their
    ``SchemaXml``), the custom content types exist (with their field links), and
    the views exist. Existing structure is left intact with ``on_conflict="skip"``
    (default); ``"update"`` reconciles content type metadata and view settings
    where supported.

    Unlike the deferred ``ensure_*`` primitives this executes the requests, so it
    can be called right after creating/resolving the target list and before
    content is copied. Run it again and it is a no-op.

    Field links are reconciled best-effort: SharePoint Online rejects adding a
    field link for a column that is not already inherited or auto-linked to the
    content type (``Column '<name>' does not exist``). Such columns cannot be
    attached over REST, so they are skipped and returned as warnings rather than
    failing the whole provisioning.

    Args:
        sp_list: The target SharePoint list (its container must already exist).
        structure: A snapshot from :func:`capture_list_structure`.
        on_conflict: ``"skip"`` (default) or ``"update"``.
        content_type_map: An optional mapping to populate with source→target content
            type identifiers (only where they differ). SharePoint assigns recreated
            list content types a fresh ``StringId``, so this lets a caller rewrite an
            item's ``ContentTypeId`` to the target one (see
            :class:`~office365.migration.map.ContentTypeMap`).
        list_id_map: An optional mapping of **normalized** source list ids to target
            list ids, used to repoint a lookup column's ``SchemaXml`` at the target
            list (see :func:`rewrite_lookup_schema`). When a lookup references a list
            absent from the map, the column is skipped and reported as a warning
            rather than created broken.

    Returns:
        Human-readable warnings for anything the server would not let us apply
        (unlinked content type columns, or lookup columns into a list that is not
        part of the migration); empty when fully applied.
    """
    if on_conflict not in ("skip", "update"):
        raise ValueError(f"on_conflict must be 'skip' or 'update', got {on_conflict!r}")

    warnings: List[str] = []

    if structure.content_types_enabled:
        _ensure_content_types_enabled(sp_list)

    taxonomy_definitions: List[FieldDefinition] = []
    for definition in structure.fields:
        if not definition.schema_xml:
            continue
        if _is_taxonomy_definition(definition):
            taxonomy_definitions.append(definition)
            continue
        schema_xml, unresolved = rewrite_lookup_schema(definition.schema_xml, list_id_map)
        if unresolved is not None:
            warning = (
                f"column '{definition.internal_name}' was not recreated: it is a lookup into "
                f"list {{{unresolved}}}, which is not part of this migration"
            )
            logger.warning(warning)
            warnings.append(warning)
            continue
        sp_list.fields.ensure_xml(schema_xml, definition.internal_name)

    if taxonomy_definitions:
        # Executes the queued scalar column creates, then loads the resulting fields
        # so an already-present taxonomy column is not recreated (which would add a
        # duplicate hidden note field and a second column with the same name).
        existing = {
            field.internal_name
            for field in sp_list.fields.get().execute_query()
            if getattr(field, "internal_name", None)
        }
        for definition in taxonomy_definitions:
            if definition.internal_name in existing:
                continue
            _ensure_taxonomy_field(sp_list, definition, warnings)
        sp_list.execute_query()

    provisionable = [item for item in structure.content_types if _is_provisionable_content_type(item)]
    for definition in provisionable:
        sp_list.content_types.ensure(
            definition.name,
            definition.description,
            definition.group,
            content_type_id=definition.string_id,
            on_conflict=on_conflict,
        )

    # Only captured user columns can be (re)linked. A content type's field links
    # also name every built-in and SharePoint-owned column (``Title``,
    # ``FileLeafRef``, framework columns, ...) which this module deliberately does
    # not recreate — attempting to link one is a guaranteed server error, so they
    # are left to the target list's own defaults.
    available = {definition.internal_name for definition in structure.fields if definition.internal_name}

    if provisionable or content_type_map is not None:
        # Executes the queued field/content-type creates, then loads the (now
        # created) content types so their field links can be reconciled and item
        # content-type ids can be rewritten.
        loaded = {ct.name: ct for ct in sp_list.content_types.get().execute_query() if ct.name}
        for definition in provisionable:
            target = loaded.get(definition.name)
            if target is not None and definition.field_internal_names:
                warnings.extend(_reconcile_field_links(target, definition.field_internal_names, available))
        if content_type_map is not None:
            content_type_map.update(ContentTypeMap.build(structure.content_types, loaded.values()).entries)

    for view in structure.views:
        sp_list.views.ensure_view(
            view.title,
            fields=list(view.field_internal_names) or None,
            row_limit=view.row_limit,
            view_type=view.view_type,
            paged=view.paged,
            personal_view=view.personal_view,
            on_conflict=on_conflict,
        )

    sp_list.execute_query()
    return warnings


def _ensure_content_types_enabled(sp_list: Any) -> None:
    """Turn on content types on the list, only when it is currently off."""

    def _enable(_: Any) -> None:
        if getattr(sp_list, "content_types_enabled", None) is not True:
            sp_list.set_property("ContentTypesEnabled", True)
            sp_list.update()

    sp_list.ensure_property("ContentTypesEnabled").after_execute(_enable)


def _reconcile_field_links(content_type: Any, internal_names: List[str], available: set[str]) -> List[str]:
    """Add any missing field links to a content type and restore their order.

    Only columns in ``available`` (the captured user columns) or already linked
    are attempted; every other captured link names a built-in/SharePoint-owned
    column the target list provides itself, so it is skipped rather than sent to
    the server as a guaranteed failure.

    Returns a list of warnings for columns the server would not link. Adding a
    link for a ready column is a no-op; adding one for a column SharePoint does
    not consider part of the content type fails (``Column '<name>' does not
    exist``), which is a REST limitation rather than a client error, so it is
    reported instead of raised.
    """
    warnings: List[str] = []
    name = content_type.name or content_type.string_id or "<content type>"
    try:
        links = content_type.field_links.get().execute_query()
    except ClientRequestException as exc:
        return [f"content type '{name}': field links could not be read: {_message(exc)}"]

    existing = {link.field_internal_name for link in links}
    skipped = [name_ for name_ in internal_names if name_ not in existing and name_ not in available]
    if skipped:
        logger.debug(
            "content type %r: left %d built-in column(s) to the target list: %s",
            name,
            len(skipped),
            ", ".join(sorted(skipped)),
        )

    linkable = [name_ for name_ in internal_names if name_ in existing or name_ in available]
    added = False
    for internal_name in linkable:
        if internal_name in existing:
            continue
        try:
            content_type.field_links.add(internal_name).execute_query()
        except ClientRequestException as exc:
            warning = f"content type '{name}': column '{internal_name}' was not linked: {_message(exc)}"
            logger.warning(warning)
            warnings.append(warning)
            continue
        added = True
    if added:
        try:
            content_type.field_links.reorder(linkable).execute_query()
        except ClientRequestException as exc:
            warning = f"content type '{name}': field link order was not applied: {_message(exc)}"
            logger.warning(warning)
            warnings.append(warning)
    return warnings


def _message(exc: ClientRequestException) -> str:
    """Best-effort short description of a request failure."""
    return getattr(exc, "message", None) or str(exc)
