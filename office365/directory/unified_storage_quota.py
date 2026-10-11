from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.service_storage_quota_breakdown import (
        ServiceStorageQuotaBreakdown,
    )


class UnifiedStorageQuota(Entity):
    @property
    def deleted(self) -> Optional[int]:
        """Gets the deleted property"""
        return self.properties.get("deleted", None)

    @property
    def manage_web_url(self) -> Optional[str]:
        """Gets the manageWebUrl property"""
        return self.properties.get("manageWebUrl", None)

    @property
    def remaining(self) -> Optional[int]:
        """Gets the remaining property"""
        return self.properties.get("remaining", None)

    @property
    def state(self) -> Optional[str]:
        """Gets the state property"""
        return self.properties.get("state", None)

    @property
    def total(self) -> Optional[int]:
        """Gets the total property"""
        return self.properties.get("total", None)

    @property
    def used(self) -> Optional[int]:
        """Gets the used property"""
        return self.properties.get("used", None)

    @property
    def services(self) -> EntityCollection[ServiceStorageQuotaBreakdown]:
        """Gets the services property"""
        from office365.directory.service_storage_quota_breakdown import (
            ServiceStorageQuotaBreakdown,
        )

        return self.properties.get(
            "services",
            EntityCollection[ServiceStorageQuotaBreakdown](
                self.context, ServiceStorageQuotaBreakdown, ResourcePath("services", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedStorageQuota"
