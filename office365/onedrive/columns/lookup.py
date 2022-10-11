from office365.runtime.client_value import ClientValue


class LookupColumn(ClientValue):
    """
    The lookupColumn on a columnDefinition resource indicates that the column's values
    are looked up from another source in the site.
    """

    def __init__(self, list_id=None, column_name=None, allow_multiple_values=None, primary_lookup_column_id=None):
        """
        :param str list_id: The unique identifier of the lookup source list.
        :param str column_name: The name of the lookup source column.
        :param bool allow_multiple_values: Indicates whether multiple values can be selected from the source.
        :param str primary_lookup_column_id:
        """
        self.listId = list_id
        self.columnName = column_name
        self.allowMultipleValues = allow_multiple_values
        self.primaryLookupColumnId = primary_lookup_column_id
