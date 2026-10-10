from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection

if TYPE_CHECKING:
    from office365.sharepoint.views.view import View


class VisualizationAppSynchronizationResult(Entity):
    @property
    def synchronization_data(self) -> Optional[str]:
        """Gets the SynchronizationData property"""
        return self.properties.get("SynchronizationData", None)

    @property
    def synchronization_status(self) -> Optional[int]:
        """Gets the SynchronizationStatus property"""
        return self.properties.get("SynchronizationStatus", None)

    @property
    def app_mapped_views(self) -> EntityCollection[View]:
        """Gets the AppMappedViews property"""
        from office365.sharepoint.views.view import View

        return self.properties.get(
            "AppMappedViews",
            EntityCollection[View](self.context, View, ResourcePath("AppMappedViews", self.resource_path)),
        )
