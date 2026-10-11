from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from office365.directory.permissions.require_permission import require_permission
from office365.entity_collection import EntityCollection
from office365.onedrive.analytics.item_activity_stat import ItemActivityStat
from office365.onedrive.analytics.item_analytics import ItemAnalytics
from office365.onedrive.base_item import BaseItem
from office365.onedrive.contenttypes.info import ContentTypeInfo
from office365.onedrive.documentsets.version import DocumentSetVersion
from office365.onedrive.internal.queries.get_activities_by_interval import (
    build_get_activities_by_interval_query,
)
from office365.onedrive.listitems.field_value_set import FieldValueSet
from office365.onedrive.versions.list_item import ListItemVersion
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.onedrive.driveitems.driveItem import DriveItem
    from office365.onedrive.permissions.permission import Permission


class ListItem(BaseItem):
    """Represents an item in a SharePoint list. Column values in the list are available through the fieldValueSet
    dictionary."""

    @require_permission(
        delegated=["Sites.Read.All", "Sites.ReadWrite.All"],
        application=["Sites.Read.All", "Sites.ReadWrite.All"],
    )
    def get_activities_by_interval(
        self,
        start_dt: datetime | None = None,
        end_dt: datetime | None = None,
        interval: str | None = None,
    ) -> EntityCollection[ItemActivityStat]:
        """Get a collection of itemActivityStats resources for the activities that took place on this resource
        within the specified time interval.

        Args:
            start_dt (datetime): The start time over which to aggregate activities.
            end_dt (datetime): The end time over which to aggregate activities.
            interval (str): The aggregation interval.
        """
        qry = build_get_activities_by_interval_query(self, start_dt, end_dt, interval)
        self.context.add_query(qry)
        return qry.return_type  # type: ignore

    @property
    def fields(self) -> FieldValueSet:
        """The values of the columns set on this list item."""
        return self.properties.get(
            "fields",
            FieldValueSet(self.context, ResourcePath("fields", self.resource_path)),
        )

    @property
    def versions(self) -> EntityCollection[ListItemVersion]:
        """The list of previous versions of the list item."""
        return self.properties.get(
            "versions",
            EntityCollection(
                self.context,
                ListItemVersion,
                ResourcePath("versions", self.resource_path),
            ),
        )

    @odata(name="driveItem")
    @property
    def drive_item(self) -> DriveItem:
        """For document libraries, the driveItem relationship exposes the listItem as a driveItem."""
        from office365.onedrive.driveitems.driveItem import DriveItem

        return self.properties.get(
            "driveItem",
            DriveItem(self.context, ResourcePath("driveItem", self.resource_path)),
        )

    @odata(name="contentType")
    @property
    def content_type(self) -> ContentTypeInfo:
        """The content type of this list item"""
        return self.properties.get("contentType", ContentTypeInfo())

    @property
    def analytics(self) -> ItemAnalytics:
        """Analytics about the view activities that took place on this item."""
        return self.properties.get(
            "analytics",
            ItemAnalytics(self.context, ResourcePath("analytics", self.resource_path)),
        )

    @odata(name="documentSetVersions")
    @property
    def document_set_versions(self) -> EntityCollection[DocumentSetVersion]:
        """Version information for a document set version created by a user."""
        return self.properties.get(
            "documentSetVersions",
            EntityCollection(
                self.context,
                DocumentSetVersion,
                ResourcePath("documentSetVersions", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.listItem"

    @property
    def permissions(self) -> EntityCollection[Permission]:
        """Gets the permissions property"""
        from office365.onedrive.permissions.permission import Permission

        return self.properties.get(
            "permissions",
            EntityCollection[Permission](self.context, Permission, ResourcePath("permissions", self.resource_path)),
        )
