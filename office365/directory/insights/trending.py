from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.insights.resource_reference import ResourceReference
from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.resource_visualization import ResourceVisualization


class Trending(Entity):
    """
    Rich relationship connecting a user to documents that are trending around the user (are relevant to the user).
    OneDrive files, and files stored on SharePoint team sites can trend around the user.
    """

    @odata(name="lastModifiedDateTime")
    @property
    def last_modified_datetime(self) -> Optional[datetime]:
        """Gets date and time the item was last modified."""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @odata(name="resourceReference")
    @property
    def resource_reference(self) -> ResourceReference:
        """Reference properties of the trending document, such as the url and type of the document."""
        return self.properties.get("resourceReference", ResourceReference())

    @property
    def resource(self) -> Entity:
        """Used for navigating to the trending document."""
        return self.properties.get(
            "resource",
            Entity(self.context, ResourcePath("resource", self.resource_path)),
        )

    @property
    def resource_visualization(self) -> ResourceVisualization:
        """Gets the resourceVisualization property"""
        from office365.directory.resource_visualization import ResourceVisualization

        return self.properties.get("resourceVisualization", ResourceVisualization())

    @property
    def weight(self) -> Optional[float]:
        """Gets the weight property"""
        return self.properties.get("weight", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Trending"
