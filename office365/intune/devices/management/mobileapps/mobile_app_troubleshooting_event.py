from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.management.mobileapps.app_log_collection_request import AppLogCollectionRequest


class MobileAppTroubleshootingEvent(Entity):
    @property
    def app_log_collection_requests(self) -> EntityCollection[AppLogCollectionRequest]:
        """Gets the appLogCollectionRequests property"""
        from office365.intune.devices.management.mobileapps.app_log_collection_request import AppLogCollectionRequest

        return self.properties.get(
            "appLogCollectionRequests",
            EntityCollection[AppLogCollectionRequest](
                self.context, AppLogCollectionRequest, ResourcePath("appLogCollectionRequests", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MobileAppTroubleshootingEvent"
