from office365.entity import Entity
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
    def worksheet(self):
        """The worksheet containing the current range """
        from office365.onedrive.workbooks.worksheets.worksheet import WorkbookWorksheet
        return self.properties.get('worksheet',
                                   WorkbookWorksheet(self.context, ResourcePath("worksheet", self.resource_path)))
