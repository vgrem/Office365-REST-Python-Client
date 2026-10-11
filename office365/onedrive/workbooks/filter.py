from __future__ import annotations

from typing import Optional

from typing_extensions import Self

from office365.entity import Entity
from office365.onedrive.workbooks.filter_criteria import WorkbookFilterCriteria
from office365.runtime.queries.service_operation import ServiceOperationQuery


class WorkbookFilter(Entity):
    """Manages the filtering of a table's column."""

    def apply_bottom_items_filter(self, count: int | None = None) -> Self:
        """Perform a sort operation.

        Args:
            count (int): The number of items to apply the filter to.
        """
        payload = {"count": count}
        qry = ServiceOperationQuery(self, "applyBottomItemsFilter", None, payload)
        self.context.add_query(qry)
        return self

    def clear(self) -> Self:
        """Clear the filter on the given column."""
        qry = ServiceOperationQuery(self, "clear")
        self.context.add_query(qry)
        return self

    @property
    def criteria(self) -> Optional[WorkbookFilterCriteria]:
        """The currently applied filter on the given column."""
        return self.properties.get("criteria", WorkbookFilterCriteria())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookFilter"
