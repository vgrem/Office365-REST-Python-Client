from office365.entity_collection import EntityCollection
from office365.onedrive.workbooks.tables.rows.row import WorkbookTableRow


class WorkbookTableRowCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(WorkbookTableRowCollection, self).__init__(context, WorkbookTableRow, resource_path)

    def add(self, values, index=None):
        """
        Adds rows to the end of a table.
        Note that this API can accept multiple rows of data. Adding one row at a time can affect performance.
        The recommended approach is to batch the rows together in a single call rather than inserting single rows.
        For best results, collect the rows to be inserted on the application side and perform a single
        row add operation. Experiment with the number of rows to determine the ideal number of rows to use
        in a single API call.

        This request might occasionally result in a 504 HTTP error. The appropriate response to this error
        is to repeat the request.

        :param list values: A two-dimensional array of unformatted values of the table rows.
        :param int index: Specifies the relative position of the new row. If null, the addition happens at the end.
             Any rows below the inserted row are shifted downwards. Zero-indexed.
        """
        return super(WorkbookTableRowCollection, self).add(values=values, index=index)
