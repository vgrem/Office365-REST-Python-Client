from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity_collection import BaseEntityCollection


class ViewFieldCollection(BaseEntityCollection):
    """Represents a collection of Field resources."""
    def __init__(self, context, resource_path=None):
        super(ViewFieldCollection, self).__init__(context, str, resource_path)

    @property
    def schema_xml(self):
        """Gets Schema Xml.

        :rtype: str or None
        """
        return self.properties.get('SchemaXml', None)

    @property
    def items(self):
        """Gets items.

        :rtype: list[str] or None
        """
        return self.properties.get('Items', None)

    def set_property(self, name, value, persist_changes=False):
        self._properties[name] = value
        if name == "Items":
            self._data = list(value.values())
        return self

    def add_view_field(self, field_name):
        """
        Adds the field with the specified field internal name or display name to the collection.

        :param str field_name:
        :return:
        """
        qry = ServiceOperationQuery(self, "AddViewField", [field_name])
        self.context.add_query(qry)
        return self

    def move_view_field_to(self, name, index):
        """
        Moves the field with the specified field internal name to the specified position in the collection

        :param str name: Specifies the field internal name.
        :param int index: Specifies the new position for the field (2). The first position is 0.

        """
        params = {"field": name, "index": index}
        qry = ServiceOperationQuery(self, "MoveViewFieldTo", None, params)
        self.context.add_query(qry)
        return self

    def remove_all_view_fields(self):
        """
        Removes all the fields from the collection.

        """
        qry = ServiceOperationQuery(self, "RemoveAllViewFields")
        self.context.add_query(qry)
        return self

    def remove_view_field(self, field_name):
        """
        Removes the field with the specified field internal name or display name from the collection.

        :param str field_name:
        """
        qry = ServiceOperationQuery(self, "RemoveViewField", [field_name])
        self.context.add_query(qry)
        return self
