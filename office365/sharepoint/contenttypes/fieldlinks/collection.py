from __future__ import annotations

from typing import Union

from typing_extensions import Self

from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.contenttypes.fieldlinks.field_link import FieldLink
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.fields.field import Field


class FieldLinkCollection(EntityCollection[FieldLink]):
    """Specifies a Collection for field links."""

    def __init__(self, context, resource_path=None):
        super().__init__(context, FieldLink, resource_path)

    def add(self, field: Union[str, Field]) -> FieldLink:
        """Add a field link with the specified link information to the collection.
        A reference to the SP.Field that was added is returned.

        Args:
            field (str or office365.sharepoint.fields.field.Field): Specifies the internal name of the field or type
        """

        def _add(field_internal_name: str | None) -> None:
            assert field_internal_name is not None
            return_type.set_property("FieldInternalName", field_internal_name)
            qry = CreateEntityQuery(self, return_type, return_type)
            self.context.add_query(qry)

        return_type = FieldLink(self.context)
        self.add_child(return_type)
        if isinstance(field, Field):
            field.ensure_property("InternalName").after_execute(lambda _: _add(field.internal_name))
        else:
            _add(field)
        return return_type

    def get_by_id(self, _id: str) -> FieldLink:
        """Gets the field link with the given id from this collection.<20> If the id is not found in the collection,
        returns null.

        Args:
            _id (str): The GUID that specifies the Microsoft.SharePoint.Client.FieldLink (section 3.2.5.46) that is
                returned.
        """
        return FieldLink(self.context, ServiceOperationPath("GetById", [_id], self.resource_path))

    def reorder(self, internal_names: list[str]) -> Self:
        """Rearranges the collection of field links in the order in which field internal names are specified.

        Args:
            internal_names (list[str]): Specifies field internal names that are arranged in the order in which the
                collection of field links is reordered.
        """
        payload = {"internalNames": list(internal_names)}
        qry = ServiceOperationQuery(self, "Reorder", None, payload)
        self.context.add_query(qry)
        return self
