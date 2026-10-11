from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity_collection import EntityCollection
from office365.onedrive.base_item import BaseItem
from office365.onedrive.columns.definition_collection import ColumnDefinitionCollection
from office365.onedrive.contenttypes.collection import ContentTypeCollection
from office365.onedrive.listitems.collection import ListItemCollection
from office365.onedrive.lists.info import ListInfo
from office365.onedrive.operations.rich_long_running import RichLongRunningOperation
from office365.onedrive.sharepoint.ids import SharePointIds
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.subscriptions.subscription import Subscription

if TYPE_CHECKING:
    from office365.onedrive.driveitems.system_facet import SystemFacet
    from office365.onedrive.permissions.permission import Permission


class List(BaseItem):
    """The list resource represents a list in a site. This resource contains the top level properties of the list,
    including template and field definitions."""

    def __str__(self):
        return self.display_name or self.entity_type_name

    @property
    def display_name(self) -> Optional[str]:
        """The displayable title of the list"""
        return self.properties.get("displayName", None)

    @property
    def list(self) -> ListInfo:
        """Provides additional details about the list."""
        return self.properties.get("list", ListInfo())

    @property
    def sharepoint_ids(self) -> SharePointIds:
        """Returns identifiers useful for SharePoint REST compatibility."""
        return self.properties.get("sharepointIds", SharePointIds())

    @property
    def drive(self):
        """Only present on document libraries. Allows access to the list as a drive resource with driveItems."""
        from office365.onedrive.drives.drive import Drive

        return self.properties.get("drive", Drive(self.context, ResourcePath("drive", self.resource_path)))

    @property
    def columns(self) -> ColumnDefinitionCollection:
        """The collection of columns under this site."""
        return self.properties.setdefault(
            "columns",
            ColumnDefinitionCollection(self.context, ResourcePath("columns", self.resource_path), self),
        )

    @odata(name="contentTypes")
    @property
    def content_types(self) -> ContentTypeCollection:
        """The collection of content types under this site."""
        return self.properties.get(
            "contentTypes",
            ContentTypeCollection(self.context, ResourcePath("contentTypes", self.resource_path)),
        )

    @property
    def items(self) -> ListItemCollection:
        """All items contained in the list."""
        return self.properties.get(
            "items",
            ListItemCollection(self.context, ResourcePath("items", self.resource_path)),
        )

    @property
    def operations(self) -> EntityCollection[RichLongRunningOperation]:
        """The collection of long-running operations on the list."""
        return self.properties.get(
            "operations",
            EntityCollection(
                self.context,
                RichLongRunningOperation,
                ResourcePath("operations", self.resource_path),
            ),
        )

    @property
    def subscriptions(self) -> EntityCollection[Subscription]:
        """The set of subscriptions on the list."""
        return self.properties.get(
            "subscriptions",
            EntityCollection(
                self.context,
                Subscription,
                ResourcePath("subscriptions", self.resource_path),
            ),
        )

    @property
    def system(self) -> SystemFacet:
        """Gets the system property"""
        from office365.onedrive.driveitems.system_facet import SystemFacet

        return self.properties.get("system", SystemFacet())

    @property
    def permissions(self) -> EntityCollection[Permission]:
        """Gets the permissions property"""
        from office365.onedrive.permissions.permission import Permission

        return self.properties.get(
            "permissions",
            EntityCollection[Permission](self.context, Permission, ResourcePath("permissions", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.List"
