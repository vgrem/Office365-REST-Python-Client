from office365.entity_collection import EntityCollection
from office365.onedrive.columns.definition import ColumnDefinition
from office365.onedrive.columns.lookup import LookupColumn
from office365.onedrive.columns.text import TextColumn
from office365.runtime.queries.create_entity import CreateEntityQuery


class ColumnDefinitionCollection(EntityCollection):

    def __init__(self, context, resource_path, parent):
        super(ColumnDefinitionCollection, self).__init__(context, ColumnDefinition, resource_path, parent)

    def add_text(self, name, max_length=None):
        """
        Create a text column

        :param str name: The API-facing name of the column as it appears in the fields on a listItem
        :param int or None max_length: The maximum number of characters for the value.
        :rtype: ColumnDefinition
        """
        return self.add(name=name, text=TextColumn(max_length=max_length))

    def add_lookup(self, name):
        """
        Create a lookup column

        :param str name: The API-facing name of the column as it appears in the fields on a listItem
        :rtype: ColumnDefinition
        """
        from office365.onedrive.lists.list import List
        if isinstance(self.parent, List):
            return_type = ColumnDefinition(self.context)
            self.add_child(return_type)

            def _list_loaded():
                payload = {
                    "name": name,
                    "lookup": LookupColumn(list_id=self.parent.id)
                }
                qry = CreateEntityQuery(self, payload, return_type)
                self.context.add_query(qry)
            self.parent.ensure_property("id", _list_loaded)
            return return_type
        else:
            return self.add(name=name, lookup=LookupColumn())
