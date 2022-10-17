from office365.entity_collection import EntityCollection
from office365.onedrive.columns.definition import ColumnDefinition
from office365.runtime.queries.create_entity import CreateEntityQuery


class ColumnDefinitionCollection(EntityCollection):

    def __init__(self, context, resource_path, parent):
        super(ColumnDefinitionCollection, self).__init__(context, ColumnDefinition, resource_path, parent)

    def add_text(self, name, max_length=None, text_type=None):
        """
        Creates a text column

        :param str name: The API-facing name of the column as it appears in the fields on a listItem
        :param int or None max_length: The maximum number of characters for the value.
        :param str or None text_type: The type of text being stored
        :rtype: ColumnDefinition
        """
        from office365.onedrive.columns.text import TextColumn
        return self.add(name=name, text=TextColumn(max_length=max_length, text_type=text_type))

    def add_hyperlink_or_picture(self, name, is_picture=None):
        """
        Creates a hyperlink or picture column

        :param str name: The API-facing name of the column as it appears in the fields on a listItem
        :param bool is_picture: Specifies whether the display format used for URL columns is an image or a hyperlink.
        """
        from office365.onedrive.columns.hyperlink_or_picture import HyperlinkOrPictureColumn
        return self.add(name=name, hyperlinkOrPicture=HyperlinkOrPictureColumn(is_picture=is_picture))

    def add_lookup(self, name, list_or_id, column_name=None):
        """
        Creates a lookup column

        :param str name: The API-facing name of the column as it appears in the fields on a listItem
        :param office365.onedrive.lists.list.List or str list_or_id: Lookup source list or identifier
        :param str column_name: The name of the lookup source column.
        :rtype: ColumnDefinition
        """
        from office365.onedrive.columns.lookup import LookupColumn
        from office365.onedrive.lists.list import List

        if isinstance(list_or_id, List):
            return_type = ColumnDefinition(self.context)
            self.add_child(return_type)

            def _list_loaded():
                params = {"name": name, "lookup": LookupColumn(list_or_id.id, column_name)}
                qry = CreateEntityQuery(self, params, return_type)
                self.context.add_query(qry)
            list_or_id.ensure_property("id", _list_loaded)
            return return_type
        else:
            return self.add(name=name, lookup=LookupColumn(list_or_id, column_name))
