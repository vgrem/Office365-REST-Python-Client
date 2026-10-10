from __future__ import annotations

from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity


class RemoveExternalUsersResults(Entity):
    @property
    def entity_type_name(self):  # type: ignore[override]
        return "Microsoft.Online.SharePoint.TenantManagement.RemoveExternalUsersResults"

    @property
    def remove_failed(self) -> StringCollection:
        """Gets the RemoveFailed property"""
        return self.properties.get("RemoveFailed", StringCollection())

    @property
    def remove_succeeded(self) -> StringCollection:
        """Gets the RemoveSucceeded property"""
        return self.properties.get("RemoveSucceeded", StringCollection())
