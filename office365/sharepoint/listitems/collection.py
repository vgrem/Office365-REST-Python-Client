from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Self

from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.thresholds import LIST_VIEW_THRESHOLD

if TYPE_CHECKING:
    from office365.runtime.converters.upsert import UpsertTarget
    from office365.runtime.operations import ProgressCallback


class ListItemCollection(EntityCollection[ListItem]):
    """List Item collection"""

    _list_view_threshold = LIST_VIEW_THRESHOLD
    _truncation_hint = "page it with List.get_items(query, page_size=2000) or items.get_all(page_size=2000)"

    def __init__(self, context, resource_path=None, parent=None):
        super().__init__(context, ListItem, resource_path, parent)

    def queue_records(self, records, progress: "ProgressCallback | None" = None) -> Self:
        """Queue an item create per record.

        List item columns are defined per list at runtime, not on the ``ListItem``
        class, so every record key is forwarded to the server (no unknown-column
        filtering). Deferred — run the creates with ``execute_query()``.
        """
        from office365.runtime.converters.csv_reader import coerce_records

        return self._import_records(coerce_records(self._item_type, records, allow_unknown=True), progress=progress)

    def _import_records(self, records: list[dict], progress: "ProgressCallback | None" = None) -> Self:
        """Queue the creates and adopt the list's entity type annotation first.

        The server needs the typed name (``SP.Data.<List>ListItem``) to interpret
        collection-valued columns; without it a create carrying a multi-lookup or
        multi-person value lacks the expected type and is rejected. ``List.add_item``
        resolves the annotation explicitly, so bulk record creation must do the same.
        One list read (skipped once the property is cached) stamps every item, and it
        is queued before the creates so the annotation is in place when they serialize.
        """
        parent = self._parent
        if parent is not None and records:
            from office365.runtime.queries.deferred import DeferredOperationQuery

            def _stamp(_) -> None:
                name = parent.properties.get("ListItemEntityTypeFullName")
                if not name:
                    return
                for item in self._data:
                    if item._entity_type_name is None:
                        item._entity_type_name = name

            parent.ensure_property("ListItemEntityTypeFullName").after_execute(_stamp)
            # A barrier splits the type-name read into its own round so the
            # annotation is resolved before the creates are serialized.
            parent.context.add_query(DeferredOperationQuery(parent.context))
        return super()._import_records(records, progress)

    def upsert_target(self, *, key_field: str = "MigrationKey", enforce_unique: bool = False) -> "UpsertTarget":
        """The keyed skip/upsert target for this list (see ``from_records(key=...)``)."""
        from office365.sharepoint.listitems.upsert import ListItemUpsertTarget

        return ListItemUpsertTarget(self, key_field=key_field, enforce_unique=enforce_unique)

    def _key_column(self, column: str) -> str:
        """List-item record keys are field internal names (``Name`` -> ``Name_``)."""
        from office365.sharepoint.fields.name import internal_field_name

        return internal_field_name(column)

    def get_by_id(self, item_id: int) -> ListItem:
        """Returns the list item with the specified list item identifier."""
        return ListItem(self.context, ServiceOperationPath("GetById", [item_id], self.resource_path))

    def get_by_string_id(self, s_id: str) -> ListItem:
        """Returns the list item with either the specified list item identifier or the specified identifier
        for an instance of an external content type.
        """
        return ListItem(
            self.context,
            ServiceOperationPath("GetByStringId", {"sId": s_id}, self.resource_path),
        )

    def get_by_url(self, url: str) -> ListItem:
        """Returns the list item with the specified site or server relative url."""
        return self.single(f"FileRef eq '{url}'")
