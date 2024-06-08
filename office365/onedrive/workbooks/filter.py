from typing import Optional

from office365.entity import Entity
from office365.onedrive.workbooks.filter_criteria import WorkbookFilterCriteria
from office365.runtime.queries.service_operation import ServiceOperationQuery


class WorkbookFilter(Entity):
    """Manages the filtering of a table's column."""

    def clear(self):
        """Clear the filter on the given column."""
        qry = ServiceOperationQuery(self, "clear")
        self.context.add_query(qry)
        return self

    @property
    def criteria(self):
        # type: () -> Optional[WorkbookFilterCriteria]
        """The currently applied filter on the given column."""
        return self.properties.get("criteria", WorkbookFilterCriteria())
