from __future__ import annotations

from typing import Optional

from typing_extensions import Self

from office365.entity import Entity
from office365.onedrive.workbooks.worksheets.protection_options import (
    WorkbookWorksheetProtectionOptions,
)
from office365.runtime.queries.service_operation import ServiceOperationQuery


class WorkbookWorksheetProtection(Entity):
    """Represents the protection of a sheet object."""

    def protect(self, options: WorkbookWorksheetProtectionOptions | None = None) -> Self:
        """Protect a worksheet. It throws if the worksheet has been protected."""
        qry = ServiceOperationQuery(self, "protect", parameters_type=options)
        self.context.add_query(qry)
        return self

    def unprotect(self) -> Self:
        """Unprotect a worksheet"""
        qry = ServiceOperationQuery(self, "unprotect")
        self.context.add_query(qry)
        return self

    @property
    def options(self) -> WorkbookWorksheetProtectionOptions:
        """ """
        return self.properties.get("options", WorkbookWorksheetProtectionOptions())

    @property
    def protected(self) -> Optional[bool]:
        """Gets the protected property"""
        return self.properties.get("protected", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookWorksheetProtection"
