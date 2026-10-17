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
* **List settings** — the container's own policy (versioning and its limits,
  content approval and draft visibility, attachments, item-level read/write
  permissions, list validation, and on a library minor versions and required
  check-out), replayed per property so a setting the target list type cannot
  accept is reported (as a warning) instead of failing the list.

Replay is **per list**, because that is as far as REST reaches: a *site* column or
a *site* content type is a web-level definition, and ``FieldLinks`` refuses to
attach a column that is not reachable from the list (``Column '<name>' does not
exist``) while the server assigns content types their own identifiers. A list that
uses one still gets a list-scoped copy; :func:`compare_web_scope_structure` reports
the web-level definitions the target web therefore lacks, so the gap is named
instead of silent.

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
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Set
from xml.etree import ElementTree

from office365.migration.map import ContentTypeMap
from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.fields.builtin_field_name import SYSTEM_FIELD_NAMES

if TYPE_CHECKING:
    from office365.sharepoint.contenttypes.content_type import ContentType
    from office365.sharepoint.contenttypes.fieldlinks.field_link import FieldLink
    from office365.sharepoint.fields.field import Field
    from office365.sharepoint.lists.list import List as SPList
    from office365.sharepoint.views.view import View
    from office365.sharepoint.webs.web import Web

logger = logging.getLogger(__name__)

__all__ = [
    "ContentTypeDefinition",
    "FieldDefinition",
    "ListStructure",
    "ViewDefinition",
    "WebScopeStructure",
    "capture_list_structure",
    "compare_web_scope_structure",
    "normalize_guid",
    "provision_list_structure",
    "rewrite_lookup_schema",
    "web_scope_note",
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
    "CustomFormatter",
    "ClientSideComponentId",
]

#: List container settings captured with the structure, in the order they must be
#: applied (versioning before its limits, moderation and versioning before the
#: draft-item policy). Every name is live-verified writable over REST.
_LIST_SETTING_ORDER = (
    "EnableVersioning",
    "EnableMinorVersions",
    "MajorVersionLimit",
    "MajorWithMinorVersionsLimit",
    "ForceCheckout",
    "EnableModeration",
    "DraftVersionVisibility",
    "EnableAttachments",
    "ReadSecurity",
    "WriteSecurity",
)

#: Minor versions, their limit and required check-out only exist on document
#: libraries - a plain list rejects them ("The list does not support minor
#: versioning"), so they are captured only where they can be replayed.
_LIBRARY_SETTING_NAMES = frozenset({"EnableMinorVersions", "MajorWithMinorVersionsLimit", "ForceCheckout"})

#: List validation names columns in its formula, so it is applied only once the
#: columns have been created.
_VALIDATION_SETTING_NAMES = ("ValidationFormula", "ValidationMessage")

#: A version limit only exists while the matching versioning flavour is on; the
#: server rejects the write outright ("Versioning must be enabled and the number of
#: major versions must be between 1 and 50000"), so a limit whose flag is off in the
#: snapshot is skipped instead of sent to bounce.
_SETTING_DEPENDS_ON = {
    "MajorVersionLimit": "EnableVersioning",
    "MajorWithMinorVersionsLimit": "EnableMinorVersions",
}

#: SharePoint rewrites a list validation formula on write (it dropped the brackets
#: around a column reference: ``=IF([Title]="",TRUE,FALSE)`` was stored as
#: ``=IF(Title="",TRUE,FALSE)``), so both sides are compared without decoration.
_FORMULA_NOISE = re.compile(r"[\s\[\]]")

#: ``SchemaXml`` attributes a faithful re-create legitimately changes: they name the
#: *containing* site (the owning list, a lookup's target list, a taxonomy column's
#: hidden note list and its web) or are assigned by the server (column id, storage
#: column/ordinal). Everything else — type, required/indexed/unique flags, length,
#: format, rich text, choice list, default, formula, validation — must reproduce.
_SCHEMA_ATTRIBUTE_NOISE = frozenset({"SourceID", "List", "ListId", "WebId", "TextField", "ID", "ColName", "RowOrdinal"})


def comparable_setting(name: str, value: Any) -> Any:
    """A list setting value in the form its own read-back is expected to take."""
    if name == "ValidationFormula" and value is not None:
        return _FORMULA_NOISE.sub("", str(value))
    return value


def _comparable_attribute(name: str, value: str) -> Any:
    """A schema attribute in the form its own read-back is expected to take."""
    if name in {"ValidationFormula", "Formula"}:
        return _FORMULA_NOISE.sub("", value)
    return value


def comparable_schema(schema_xml: Optional[str]) -> Dict[str, Any]:
    """A column's ``SchemaXml`` reduced to the parts a faithful copy reproduces.

    Returns the column's attributes and its value-bearing child elements
    (``Default``, ``CHOICES``, ``Formula``, ``FieldRefs``) keyed by name, with the
    site-specific and server-assigned attributes dropped (see
    :data:`_SCHEMA_ATTRIBUTE_NOISE`). Values are normalized the way their own
    read-back comes back: a formula without brackets/whitespace and a choice list as
    a tuple of its options. Unparsable schema yields an empty mapping, so an
    unreadable column is never reported as a difference.
    """
    if not schema_xml:
        return {}
    try:
        root = ElementTree.fromstring(schema_xml)
    except ElementTree.ParseError:
        return {}
    comparable: Dict[str, Any] = {
        f"attribute {name}": _comparable_attribute(name, value)
        for name, value in sorted(root.attrib.items())
        if name not in _SCHEMA_ATTRIBUTE_NOISE
    }
    for child in root:
        tag = child.tag.upper()
        if tag == "CHOICES":
            comparable["choices"] = tuple(choice.text or "" for choice in child)
        elif tag == "FIELDREFS":
            comparable["field references"] = tuple(ref.attrib.get("Name") or "" for ref in child)
        elif tag in {"FORMULA", "VALIDATIONFORMULA"}:
            comparable[tag.lower()] = _FORMULA_NOISE.sub("", child.text or "")
        else:
            comparable[tag.lower()] = (child.text or "").strip()
    return comparable


def _setting_names(base_type: Optional[int]) -> List[str]:
    """The container settings worth capturing for a list of this base type."""
    return [name for name in _LIST_SETTING_ORDER if base_type == 1 or name not in _LIBRARY_SETTING_NAMES]


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
    custom_formatter: Optional[str] = None
    client_side_component_id: Optional[str] = None

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
            custom_formatter=data.get("custom_formatter"),
            client_side_component_id=data.get("client_side_component_id"),
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
    custom_formatter: Optional[str] = None

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
            custom_formatter=data.get("custom_formatter"),
        )


@dataclass
class ListStructure:
    """A serializable snapshot of a list's container metadata and structure."""

    title: Optional[str] = None
    base_template: Optional[int] = None
    base_type: Optional[int] = None
    description: Optional[str] = None
    content_types_enabled: Optional[bool] = None
    settings: Dict[str, Any] = dc_field(default_factory=dict)
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
            settings=dict(data.get("settings") or {}),
            fields=[FieldDefinition.from_dict(item) for item in data.get("fields") or []],
            content_types=[ContentTypeDefinition.from_dict(item) for item in data.get("content_types") or []],
            views=[ViewDefinition.from_dict(item) for item in data.get("views") or []],
        )


def capture_list_structure(sp_list: SPList) -> ListStructure:
    """Read a SharePoint list's structure into a :class:`ListStructure` snapshot.

    Issues only GET requests. Loads the list's scalar properties, its columns,
    the non-hidden content types (with their field links), and the non-hidden
    views (with their columns).

    Args:
        sp_list: A ``List`` (possibly not yet loaded); it is loaded in place.

    Returns:
        A fully-populated, serializable snapshot.
    """
    sp_list.ensure_properties(["Title", "BaseTemplate", "BaseType", "Description", "ContentTypesEnabled"])
    # Container settings (versioning, content approval, attachments, item-level
    # permissions, validation) travel with the columns: a target list created from
    # its template alone keeps the template defaults, so a moderated or
    # version-limited source would lose that policy.
    setting_names = [*_LIST_SETTING_ORDER, *_VALIDATION_SETTING_NAMES]
    sp_list.ensure_properties(setting_names).execute_query()

    structure = ListStructure(
        title=sp_list.title,
        base_template=sp_list.base_template,
        base_type=sp_list.base_type,
        description=sp_list.description,
        content_types_enabled=sp_list.content_types_enabled,
        settings={
            name: value
            for name in [*_setting_names(sp_list.base_type), *_VALIDATION_SETTING_NAMES]
            if (value := sp_list.properties.get(name)) is not None
        },
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


def _is_capturable_field(field: Field) -> bool:
    """Only recreatable user columns — not built-in, framework, or hidden fields.

    Built-in/system fields are already present on any target list, and framework
    columns injected by SharePoint features (shortcuts, media, sensitivity
    labels, ...) cannot be recreated meaningfully. A list-scoped, deletable,
    visible column is what a user actually added.
    """
    name = field.internal_name
    if not name or name in SYSTEM_FIELD_NAMES:
        return False
    if field.from_base_type is True:
        return False
    if field.can_be_deleted is False:
        return False
    return field.hidden is not True


def _is_capturable_content_type(content_type: ContentType) -> bool:
    """Content types that carry useful, recreatable structure (non-hidden, identified)."""
    return bool(content_type.string_id) and not content_type.hidden


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


#: A column bound to an external (BCS) content type. The generated ``FieldType``
#: model does not carry this member, so the ``TypeAsString``/``SchemaXml``
#: spelling is what identifies it.
_EXTERNAL_DATA_TYPE = "BusinessData"


def _is_external_data_definition(definition: FieldDefinition) -> bool:
    """Whether a captured column reads its values from an external (BCS) source."""
    if (definition.type_as_string or "") == _EXTERNAL_DATA_TYPE:
        return True
    return f'Type="{_EXTERNAL_DATA_TYPE}"' in (definition.schema_xml or "")


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


def _ensure_taxonomy_field(sp_list: SPList, definition: FieldDefinition, warnings: List[str]) -> None:
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


def _schema_for_copy(field: Field) -> Optional[str]:
    """``SchemaXml`` stripped of origin attributes (``SourceID``/``Version``)."""
    return field.schema_xml_for_copy()


def _field_kind_int(field: Field) -> Optional[int]:
    # ``Field.field_type_kind`` is typed ``FieldType`` but a raw read leaves the
    # JSON integer in the property bag, so accept either shape.
    kind = field.field_type_kind
    if kind is None:
        return None
    value = getattr(kind, "value", kind)
    return value if isinstance(value, int) else None


def _field_definition(field: Field) -> FieldDefinition:
    return FieldDefinition(
        internal_name=field.internal_name or "",
        title=field.title,
        field_type_kind=_field_kind_int(field),
        type_as_string=field.type_as_string,
        schema_xml=_schema_for_copy(field),
        required=field.required,
        hidden=field.hidden,
        read_only=field.read_only_field,
        from_base_type=field.from_base_type,
        can_be_deleted=field.can_be_deleted,
        group=field.group,
        description=field.description,
        custom_formatter=field.properties.get("CustomFormatter"),
        client_side_component_id=_component_id(field),
    )


#: An "unset" ``ClientSideComponentId`` is the all-zero GUID, not an absent property.
_EMPTY_GUID = "00000000-0000-0000-0000-000000000000"


def _component_id(field: Field) -> Optional[str]:
    """The SPFx field customizer registered on a column, if any."""
    value = field.properties.get("ClientSideComponentId")
    if not value or normalize_guid(value) == _EMPTY_GUID:
        return None
    return str(value)


def _content_type_definition(content_type: ContentType, links: Iterable[FieldLink]) -> ContentTypeDefinition:
    return ContentTypeDefinition(
        string_id=content_type.string_id or "",
        name=content_type.name,
        group=content_type.group,
        description=content_type.description,
        hidden=content_type.hidden,
        sealed=content_type.sealed,
        read_only=content_type.read_only,
        field_internal_names=[name for name in (link.field_internal_name for link in links) if name],
    )


def _view_definition(view: View, field_names: Iterable[str]) -> ViewDefinition:
    return ViewDefinition(
        title=view.title or "",
        view_type=view.view_type,
        row_limit=view.row_limit,
        paged=view.paged,
        hidden=view.hidden,
        default_view=view.default_view,
        personal_view=view.personal_view,
        view_query=view.view_query,
        field_internal_names=[name for name in field_names if name],
        custom_formatter=view.properties.get("CustomFormatter"),
    )


def provision_list_structure(
    sp_list: SPList,
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

    The captured container settings (versioning, content approval, attachments,
    item-level read/write policy, list validation, and on libraries minor versions
    and required check-out) are applied as well, one ``MERGE`` per setting so a
    single rejected setting is reported instead of failing the list. Only settings
    that differ from the target's own values are written, so a list created from the
    same template (and a re-run) writes nothing. They are applied regardless of
    ``on_conflict`` because the snapshot *is* the wanted policy and the item copy
    depends on it: an item's approval status is only stored on a list that has
    content approval enabled. Settings the target list type does not support come
    back as warnings.

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

    _apply_list_settings(sp_list, structure, warnings, validation=False)

    if structure.content_types_enabled:
        _ensure_content_types_enabled(sp_list)

    taxonomy_definitions: List[FieldDefinition] = []
    for definition in structure.fields:
        if not definition.schema_xml:
            continue
        if _is_taxonomy_definition(definition):
            taxonomy_definitions.append(definition)
            continue
        if _is_external_data_definition(definition):
            # An external-data column is a *reference* into a BDC model: replaying
            # its schema would create a column that resolves nothing on the target,
            # so it is reported instead (the list itself is reported as a handoff).
            warning = (
                f"column '{definition.internal_name}' was not recreated: it is bound to an "
                "external (BCS) content type, which a client-side migration cannot provision"
            )
            logger.warning(warning)
            warnings.append(warning)
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
        assert schema_xml is not None  # a skipped lookup always names its unresolved list id
        sp_list.fields.ensure_xml(schema_xml, definition.internal_name)

    if taxonomy_definitions:
        # Executes the queued scalar column creates, then loads the resulting fields
        # so an already-present taxonomy column is not recreated (which would add a
        # duplicate hidden note field and a second column with the same name).
        existing = {field.internal_name for field in sp_list.fields.get().execute_query() if field.internal_name}
        for definition in taxonomy_definitions:
            if definition.internal_name in existing:
                continue
            _ensure_taxonomy_field(sp_list, definition, warnings)
        sp_list.execute_query()

    provisionable = [
        (item.name, item) for item in structure.content_types if item.name and _is_provisionable_content_type(item)
    ]
    for name, definition in provisionable:
        sp_list.content_types.ensure(
            name,
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
        for name, definition in provisionable:
            target = loaded.get(name)
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

    _apply_list_settings(sp_list, structure, warnings, validation=True)

    sp_list.execute_query()
    _apply_formatting(sp_list, structure, warnings)
    return warnings


def _apply_formatting(sp_list: SPList, structure: ListStructure, warnings: List[str]) -> None:
    """Replay the column and view formatting JSON the target does not carry.

    Column formatting lives on the column and row formatting on the view, and both
    are a plain ``MERGE`` on the entity — so both run once the columns and views
    exist. A column the server keeps sealed swallows the write without an error, so
    the pass reads both sides back and reports what did not take rather than
    claiming success.

    An SPFx field customizer is a pointer into a deployed solution: it cannot work
    on a target that does not have that solution, so it is reported, never copied.
    """
    for definition in structure.fields:
        if definition.client_side_component_id:
            warnings.append(
                f"column '{definition.internal_name}' carries an SPFx field customizer "
                f"({definition.client_side_component_id}), which is not carried: the solution has to be "
                "deployed on the target"
            )
    column_formatters = {
        definition.internal_name: definition.custom_formatter
        for definition in structure.fields
        if definition.custom_formatter and definition.internal_name
    }
    view_formatters = {
        view.title: view.custom_formatter for view in structure.views if view.custom_formatter and view.title
    }
    if not column_formatters and not view_formatters:
        return

    written = False
    for name, formatter in column_formatters.items():
        field = sp_list.fields.get_by_internal_name_or_title(name).get().execute_query()
        if field.properties.get("CustomFormatter") == formatter:
            continue
        field.set_property("CustomFormatter", formatter)
        field.update()
        written = True
    for title, formatter in view_formatters.items():
        view = sp_list.views.get_by_title(title).get().execute_query()
        if view.properties.get("CustomFormatter") == formatter:
            continue
        view.set_property("CustomFormatter", formatter)
        view.update()
        written = True
    if not written:
        return
    sp_list.execute_query()

    # A sealed column accepts the MERGE and drops the value: read back, then report.
    current_fields = {
        field.internal_name: field.properties.get("CustomFormatter")
        for field in sp_list.fields.select(["InternalName", "CustomFormatter"]).get().execute_query()
        if field.internal_name
    }
    for name, formatter in column_formatters.items():
        if name in current_fields and current_fields[name] != formatter:
            warnings.append(f"column '{name}' kept its own formatting: the target would not accept the formatter")
    current_views = {view.title: view.properties.get("CustomFormatter") for view in sp_list.views.get().execute_query()}
    for title, formatter in view_formatters.items():
        if title in current_views and current_views[title] != formatter:
            warnings.append(f"view '{title}' kept its own formatting: the target would not accept the formatter")


def _apply_list_settings(sp_list: SPList, structure: ListStructure, warnings: List[str], *, validation: bool) -> None:
    """Apply the captured container settings the target does not already carry.

    Only *differing* settings are written (one GET reads the target's current
    values first): a target created from the list template already carries most of
    them, and blindly ``MERGE``-ing an equal value is both a needless request and a
    false alarm — SharePoint rejects some of those writes for policy reasons (a
    version limit with versioning off, a system library that grants no write) even
    though the target is already correct.

    Each remaining setting is written by its own throw-away list handle (addressed
    by title), so a server rejection of one setting cannot leak into the next
    ``MERGE`` and the caller's own list object keeps no half-applied state. Failure
    reasons are collected as warnings: a policy the target list type cannot express
    (minor versions on a plain list, for instance) is a fidelity note, not an error.
    """
    title = structure.title or sp_list.title
    if not title:
        return
    wanted = {
        name: value
        for name, value in structure.settings.items()
        if (name in _VALIDATION_SETTING_NAMES) is validation
        and not (name in _LIBRARY_SETTING_NAMES and structure.base_type != 1)
        and _setting_is_expressible(name, structure.settings)
    }
    if not wanted:
        return
    current = _current_settings(sp_list, list(wanted))
    for name, value in wanted.items():
        if name in current and comparable_setting(name, current[name]) == comparable_setting(name, value):
            continue
        handle = sp_list.context.web.lists.get_by_title(title)
        handle.set_property(name, value)
        try:
            handle.update().execute_query()
        except Exception as exc:  # noqa: BLE001 - any rejection is a fidelity note
            warning = f"list setting '{name}' was not applied: {_rejection_reason(exc)}"
            logger.warning(warning)
            warnings.append(warning)


def _setting_is_expressible(name: str, settings: Dict[str, Any]) -> bool:
    """Whether a captured setting can be applied given the snapshot's other values."""
    dependency = _SETTING_DEPENDS_ON.get(name)
    return dependency is None or bool(settings.get(dependency))


def _current_settings(sp_list: SPList, names: List[str]) -> Dict[str, Any]:
    """The target list's current values for the settings about to be applied."""
    sp_list.ensure_properties(names)
    sp_list.get().execute_query()
    return {name: sp_list.properties.get(name) for name in names if sp_list.properties.get(name) is not None}


def _rejection_reason(exc: Exception) -> str:
    """The server's own wording for a rejected write, trimmed for a warning."""
    message = getattr(exc, "message", None) or str(exc)
    return message.strip()[:200]


def _ensure_content_types_enabled(sp_list: SPList) -> None:
    """Turn on content types on the list, only when it is currently off."""

    def _enable(_: Any) -> None:
        if sp_list.content_types_enabled is not True:
            sp_list.set_property("ContentTypesEnabled", True)
            sp_list.update()

    sp_list.ensure_property("ContentTypesEnabled").after_execute(_enable)


def _reconcile_field_links(content_type: ContentType, internal_names: List[str], available: set[str]) -> List[str]:
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


# --- web scope ---------------------------------------------------------------
#
# A site column and a site content type live at *web* scope. REST can create both
# (`web.fields` / `web.content_types`), but it cannot *link* a fresh site column to
# a content type (`FieldLinks` answers `Column '<name>' does not exist`), and the
# server assigns content types their own identifiers. Provisioning therefore
# replays a source list's structure onto the target *list*, which is faithful for
# the list and lossy for the web. These helpers name the loss.

#: Web field properties needed to tell a user-facing column from a system one.
_WEB_FIELD_SELECT = ["InternalName", "Group", "Hidden", "FromBaseType", "CanBeDeleted", "Sealed"]

#: Web content type properties needed to compare presence (ids are not preserved).
_WEB_CONTENT_TYPE_SELECT = ["Name", "Hidden"]

#: Names listed inline in a note before it is truncated.
_MAX_WEB_SCOPE_NAMES = 5


@dataclass
class WebScopeStructure:
    """Web-scope definitions the target web lacks after a per-list replay.

    Attributes:
        columns: Internal names of source web columns with no counterpart on the target web.
        content_types: Names of source web content types absent from the target web.
    """

    columns: List[str] = dc_field(default_factory=list)
    content_types: List[str] = dc_field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        """Whether the target web already carries every web-scope definition."""
        return not self.columns and not self.content_types

    def to_dict(self) -> Dict[str, Any]:
        """A JSON-serializable form."""
        return {"columns": list(self.columns), "content_types": list(self.content_types)}


def _is_web_scope_column(column: Field) -> bool:
    """Whether a web field is a user-facing column rather than platform plumbing."""
    name = column.internal_name
    if not name or name in SYSTEM_FIELD_NAMES:
        return False
    if column.hidden is True or column.from_base_type is True or column.sealed is True:
        return False
    return column.can_be_deleted is not False


def _web_scope_columns(web: Web) -> List[str]:
    """The user-facing column names registered on ``web`` (one projected GET)."""
    loaded = web.fields.select(_WEB_FIELD_SELECT).get().execute_query()
    names: Set[str] = set()
    for column in loaded:
        name = column.internal_name
        if name and _is_web_scope_column(column):
            names.add(name)
    return sorted(names)


def _web_scope_content_types(web: Web) -> List[str]:
    """The content type names registered on ``web`` (one projected GET)."""
    loaded = web.content_types.select(_WEB_CONTENT_TYPE_SELECT).get().execute_query()
    return sorted(
        {content_type.name for content_type in loaded if content_type.name and content_type.hidden is not True}
    )


def compare_web_scope_structure(source_web: Web, target_web: Web) -> WebScopeStructure:
    """Web-scope columns/content types of ``source_web`` that ``target_web`` lacks.

    Two projected GETs per web, read-only. The comparison is *by presence*:
    columns by internal name, content types by name-casefolded (a content type's
    ``string_id`` is assigned by the server and is not preserved by a copy, so it
    cannot be the key).

    Args:
        source_web: The web the migration reads structure from.
        target_web: The web the migration replays it onto.
    """
    source_columns = _web_scope_columns(source_web)
    target_columns = set(_web_scope_columns(target_web))
    source_content_types = _web_scope_content_types(source_web)
    target_content_types = {name.casefold() for name in _web_scope_content_types(target_web)}
    return WebScopeStructure(
        columns=[name for name in source_columns if name not in target_columns],
        content_types=[name for name in source_content_types if name.casefold() not in target_content_types],
    )


def _sample_names(names: List[str]) -> str:
    """Name a few entries inline, counting the rest."""
    shown = ", ".join(names[:_MAX_WEB_SCOPE_NAMES])
    if len(names) <= _MAX_WEB_SCOPE_NAMES:
        return shown
    return f"{shown} (+{len(names) - _MAX_WEB_SCOPE_NAMES} more)"


def web_scope_note(missing: WebScopeStructure, source_url: Optional[str] = None) -> Optional[str]:
    """A warning line for the web-scope gap, or ``None`` when there is none.

    Args:
        missing: The result of :func:`compare_web_scope_structure`.
        source_url: The *source* web's URL. The note names the affected target by
            its source, because the target web handle is often not URL-loaded and
            one note is emitted per web pair anyway.
    """
    if missing.is_empty:
        return None
    parts: List[str] = []
    if missing.columns:
        parts.append(f"{len(missing.columns)} column(s): {_sample_names(missing.columns)}")
    if missing.content_types:
        parts.append(f"{len(missing.content_types)} content type(s): {_sample_names(missing.content_types)}")
    return (
        f"web-scope structure is not replayed: the target of {source_url or 'this web'} lacks "
        + "; ".join(parts)
        + " — a migrated list that uses one still gets a list-scoped copy, but the web-level "
        "definition and its inheritance by the web's other lists are missing; create it out of "
        "band (CSOM/PnP) if anything else depends on it"
    )
