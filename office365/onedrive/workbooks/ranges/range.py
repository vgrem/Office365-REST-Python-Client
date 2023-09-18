from office365.entity import Entity
from office365.onedrive.workbooks.ranges.format import WorkbookRangeFormat
from office365.onedrive.workbooks.ranges.sort import WorkbookRangeSort
from office365.onedrive.workbooks.ranges.view import WorkbookRangeView
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery


class WorkbookRange(Entity):
    """Range represents a set of one or more contiguous cells such as a cell, a row, a column, block of cells, etc."""

    def visible_view(self):
        """"""
        return_type = WorkbookRangeView(self.context)
        qry = FunctionQuery(self, "visibleView", return_type=return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def address(self):
        """
        Represents the range reference in A1-style. Address value will contain the Sheet reference
        (e.g. Sheet1!A1:B4)
        :rtype: str or None
        """
        return self.properties.get("address", None)

    @property
    def address_local(self):
        """
        Represents range reference for the specified range in the language of the user. Read-only.
        :rtype: str or None
        """
        return self.properties.get("addressLocal", None)

    @property
    def cell_count(self):
        """
        Number of cells in the range. Read-only.
        :rtype: int or None
        """
        return self.properties.get("cellCount", None)

    @property
    def column_count(self):
        """
        Represents the total number of columns in the range. Read-only.
        :rtype: int or None
        """
        return self.properties.get("columnCount", None)

    @property
    def format(self):
        """Returns a format object, encapsulating the range's font, fill, borders, alignment, and other properties"""
        return self.properties.get('format',
                                   WorkbookRangeFormat(self.context, ResourcePath("format", self.resource_path)))

    @property
    def sort(self):
        """The worksheet containing the current range. """
        return self.properties.get('sort',
                                   WorkbookRangeSort(self.context, ResourcePath("sort", self.resource_path)))

    @property
    def worksheet(self):
        """The worksheet containing the current range """
        from office365.onedrive.workbooks.worksheets.worksheet import WorkbookWorksheet
        return self.properties.get('worksheet',
                                   WorkbookWorksheet(self.context, ResourcePath("worksheet", self.resource_path)))
