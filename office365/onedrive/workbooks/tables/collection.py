from office365.entity_collection import EntityCollection
from office365.onedrive.workbooks.tables.table import WorkbookTable


class WorkbookTableCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(WorkbookTableCollection, self).__init__(context, WorkbookTable, resource_path)

    def __getitem__(self, id_or_name):
        """
        :rtype: WorkbookTable
        """
        return super(WorkbookTableCollection, self).__getitem__(id_or_name)

    def add(self, address, has_headers):
        """
        Create a new table. The range source address determines the worksheet under which the table will be added.
        If the table cannot be added (e.g., because the address is invalid, or the table would overlap with
        another table), an error will be thrown.

        :param str address: Address or name of the range object representing the data source.
           If the address does not contain a sheet name, the currently-active sheet is used.
        :param bool has_headers: Boolean value that indicates whether the data being imported has column labels. If
           the source does not contain headers (i.e,. when this property set to false),
           Excel will automatically generate header shifting the data down by one row.
        :rtype: WorkbookTable
        """
        return super(WorkbookTableCollection, self).add(address=address, hasHeaders=has_headers)
