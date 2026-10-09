from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Union

from typing_extensions import Self

from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.fields.field import Field


class ViewFieldCollection(Entity):
    """Represents a collection of Field resources."""

    def __len__(self):
        items = self.items
        return len(items) if items else 0

    def __iter__(self):
        return iter(self.items or [])

    def __getitem__(self, index: int) -> str:
        """Gets view field by index"""
        items = self.items
        if items is None:
            raise IndexError("view field items is None")
        return items[index]

    def __repr__(self):
        return repr(self.items)

    @property
    def schema_xml(self) -> Optional[str]:
        """Gets Schema Xml."""
        return self.properties.get("SchemaXml", None)

    @property
    def items(self) -> Optional[List[str]]:
        """Gets items."""
        return self.properties.get("Items", None)

    def set_property(self, name, value, persist_changes=False):
        if name == "Items":
            value = list(value.values())
        super().set_property(name, value, persist_changes)
        return self

    def add_view_field(self, field: Union[str, Field]) -> Self:
        """Adds the field with the specified field internal name or display name to the collection.

        Args:
            field (str):
        """
        from office365.sharepoint.fields.field import Field

        def _add_view_field(field_name: str | None) -> None:
            """
            Adds the field with the specified field internal name or display name to the collection.
            """
            assert field_name is not None
            qry = ServiceOperationQuery(self, "AddViewField", [field_name])
            self.context.add_query(qry)

        if isinstance(field, Field):
            field.ensure_property("InternalName").after_execute(lambda _: _add_view_field(field.internal_name))
        else:
            _add_view_field(field)
        return self

    def move_view_field_to(self, field: Union[str, Field], index: int) -> Self:
        """Moves the field with the specified field internal name to the specified position in the collection

        Args:
            field (str): Specifies the field internal name.
            index (int): Specifies the new position for the field (2). The first position is 0.
        """
        from office365.sharepoint.fields.field import Field

        def _move_view_field_to(field_name: str | None) -> None:
            assert field_name is not None
            params = {"field": field_name, "index": index}
            qry = ServiceOperationQuery(self, "MoveViewFieldTo", None, params)
            self.context.add_query(qry)

        if isinstance(field, Field):
            field.ensure_property("InternalName").after_execute(lambda _: _move_view_field_to(field.internal_name))
        else:
            _move_view_field_to(field)

        return self

    def remove_all_view_fields(self) -> Self:
        """Removes all the fields from the collection."""
        qry = ServiceOperationQuery(self, "RemoveAllViewFields")
        self.context.add_query(qry)
        return self

    def remove_view_field(self, field: Union[str, Field]) -> Self:
        """Removes the field with the specified field internal name or display name from the collection.

        Args:
            field (str):
        """
        from office365.sharepoint.fields.field import Field

        def _remove_view_field(field_name: str | None) -> None:
            assert field_name is not None
            qry = ServiceOperationQuery(self, "RemoveViewField", [field_name])
            self.context.add_query(qry)

        if isinstance(field, Field):
            field.ensure_property("InternalName").after_execute(lambda _: _remove_view_field(field.internal_name))
        else:
            _remove_view_field(field)

        return self

    @property
    def entity_type_name(self):
        return "SP.ViewFieldCollection"
