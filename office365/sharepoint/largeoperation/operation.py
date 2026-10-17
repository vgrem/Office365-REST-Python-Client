from __future__ import annotations

from typing import Optional

from office365.runtime.pollable import PollableOperation
from office365.sharepoint.entity import Entity


class SPLargeOperation(PollableOperation, Entity):
    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.LargeOperation.SPLargeOperation"

    @property
    def operation_type(self) -> Optional[str]:
        """Gets the OperationType property"""
        return self.properties.get("OperationType", None)

    @property
    def progress_percentage(self) -> Optional[float]:
        """Gets the ProgressPercentage property"""
        return self.properties.get("ProgressPercentage", None)

    @property
    def resource_location(self) -> Optional[str]:
        """Gets the ResourceLocation property"""
        return self.properties.get("ResourceLocation", None)

    @property
    def status(self) -> Optional[str]:
        """Gets the Status property"""
        return self.properties.get("Status", None)
