"""Capture a SharePoint list's *structure* (columns, content types, views).

A whole-site migration recreates each target list container, but content copied
into a list whose custom columns/content types/views do not exist yet has nowhere
to land. This module takes a **read-only, serializable snapshot** of a source
list's structure, so it can be inspected, persisted, and (in a later step)
reprovisioned on the target before content is copied.

``capture_list_structure`` performs GETs only — it never writes. The snapshot is
a plain tree of dataclasses that round-trips through :meth:`ListStructure.to_dict`
/ :meth:`ListStructure.from_dict` (JSON-friendly), so a plan can be captured once
and replayed.

Scope, deliberately:

* **Fields** — user-defined list columns with their ``SchemaXml`` prepared for
  ``CreateFieldAsXml`` (see :meth:`~office365.sharepoint.fields.field.Field.schema_xml_for_copy`).
  Built-in/system columns and framework columns injected by SharePoint features
  (hidden, or not deletable) are skipped — a target list already has them.
* **Content types** — non-hidden content types with their ordered field links.
* **Views** — non-hidden, non-personal views with their ordered columns.

Provisioning the captured structure onto a target list is a separate step.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from dataclasses import field as dc_field
from typing import Any, Dict, List, Optional

from office365.sharepoint.fields.builtin_field_name import SYSTEM_FIELD_NAMES

__all__ = [
    "ContentTypeDefinition",
    "FieldDefinition",
    "ListStructure",
    "ViewDefinition",
    "capture_list_structure",
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
