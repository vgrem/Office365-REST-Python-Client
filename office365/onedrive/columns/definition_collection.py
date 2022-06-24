from office365.entity_collection import EntityCollection
from office365.onedrive.columns.definition import ColumnDefinition
from office365.onedrive.columns.text import TextColumn


class ColumnDefinitionCollection(EntityCollection):

    def __init__(self, context, resource_path):
        super(ColumnDefinitionCollection, self).__init__(context, ColumnDefinition, resource_path)

    def add_text(self, name):
        """
        Create a column

        :param str name: The API-facing name of the column as it appears in the fields on a listItem

        :rtype: ColumnDefinition
        """
        return_type = self.add(name=name, text=TextColumn())
        return return_type
