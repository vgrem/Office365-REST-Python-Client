from typing import Optional

from office365.entity import Entity
from office365.onedrive.workbooks.filter_criteria import WorkbookFilterCriteria


class WorkbookFilter(Entity):
    """Manages the filtering of a table's column."""

    @property
    def criteria(self):
        # type: () -> Optional[WorkbookFilterCriteria]
        """The currently applied filter on the given column."""
        return self.properties.get("criteria", WorkbookFilterCriteria())
