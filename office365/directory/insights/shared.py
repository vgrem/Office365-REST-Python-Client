from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.insights.resource_reference import ResourceReference
from office365.directory.insights.sharing_detail import SharingDetail
from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.resource_visualization import ResourceVisualization


class SharedInsight(Entity):
    """
    An insight representing files shared with or by a specific user. The following shared files are supported:

      Files attached directly in an email or a meeting invite.
      OneDrive for Business and SharePoint modern attachments - files stored in OneDrive for Business and SharePoint
      that users share as a links in an email.
    """

    @odata(name="lastShared")
    @property
    def last_shared(self) -> SharingDetail:
        """Details about the shared item. Read-only"""
        return self.properties.get("lastShared", SharingDetail())

    @odata(name="resourceReference")
    @property
    def resource_reference(self) -> ResourceReference:
        """Reference properties of the used document, such as the url and type of the document. Read-only"""
        return self.properties.get("resourceReference", ResourceReference())

    @property
    def resource(self) -> Entity:
        """Used for navigating to the item that was shared. For file attachments, the type is fileAttachment.
        For linked attachments, the type is driveItem."""
        return self.properties.get(
            "resource",
            Entity(self.context, ResourcePath("resource", self.resource_path)),
        )

    @odata(name="sharingHistory")
    @property
    def sharing_history(self) -> ClientValueCollection[SharingDetail]:
        """Details about the sharing history. Read-only"""
        return self.properties.get("sharingHistory", ClientValueCollection(SharingDetail))

    @property
    def resource_visualization(self) -> ResourceVisualization:
        """Gets the resourceVisualization property"""
        from office365.directory.resource_visualization import ResourceVisualization

        return self.properties.get("resourceVisualization", ResourceVisualization())

    @property
    def last_shared_method(self) -> Entity:
        """Gets the lastSharedMethod property"""
        from office365.entity import Entity

        return self.properties.get(
            "lastSharedMethod", Entity(self.context, ResourcePath("lastSharedMethod", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SharedInsight"
