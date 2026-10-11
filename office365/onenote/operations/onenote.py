from __future__ import annotations

from typing import Optional

from office365.onenote.operations.onenote_operation_error import OnenoteOperationError
from office365.onenote.operations.operation import Operation


class OnenoteOperation(Operation):
    """The status of certain long-running OneNote operations."""

    @property
    def error(self) -> OnenoteOperationError:
        """The error returned by the operation."""
        return self.properties.get("error", OnenoteOperationError())

    @property
    def percent_complete(self) -> Optional[str]:
        """Gets the percentComplete property"""
        return self.properties.get("percentComplete", None)

    @property
    def resource_id(self) -> Optional[str]:
        """Gets the resourceId property"""
        return self.properties.get("resourceId", None)

    @property
    def resource_location(self) -> Optional[str]:
        """Gets the resourceLocation property"""
        return self.properties.get("resourceLocation", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnenoteOperation"
