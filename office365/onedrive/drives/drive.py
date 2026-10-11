from __future__ import annotations

from typing import Optional

from office365.directory.permissions.identity_set import IdentitySet
from office365.directory.permissions.require_permission import require_permission
from office365.entity_collection import EntityCollection
from office365.onedrive.base_item import BaseItem
from office365.onedrive.driveitems.collection import DriveItemCollection
from office365.onedrive.driveitems.conflict_behavior import ConflictBehavior
from office365.onedrive.driveitems.driveItem import DriveItem
from office365.onedrive.driveitems.system_facet import SystemFacet
from office365.onedrive.drives.quota import Quota
from office365.onedrive.internal.paths.root import RootPath
from office365.onedrive.lists.list import List
from office365.onedrive.recyclebin.recyclebin import RecycleBin
from office365.onedrive.sharepoint.ids import SharePointIds
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.types.odata_property import odata


class Drive(BaseItem):
    """The drive resource is the top level object representing a user's OneDrive or a document library in
    SharePoint."""

    @require_permission(
        delegated=[
            "Files.Read",
            "Files.Read.All",
            "Files.ReadWrite",
            "Files.ReadWrite.All",
            "Sites.Read.All",
            "Sites.ReadWrite.All",
        ],
        application=["Files.Read.All", "Files.ReadWrite.All", "Sites.Read.All", "Sites.ReadWrite.All"],
        notes="Get metadata about a drive",
    )
    def get(self):
        """Retrieve drive metadata"""
        return super().get()

    def create_bundle(self, name: str, children: list | None = None) -> DriveItem:
        """Add a new bundle to the user's drive.

        Args:
            name (str): Bundle name
            children (list): the list of file facets if creating a files or a folder facets if creating a folder or
              a remoteItem facets if adding a shared folders
        """
        return_type = DriveItem(self.context)
        self.bundles.add_child(return_type)
        payload = {
            "name": name,
            "@microsoft.graph.conflictBehavior": ConflictBehavior.Rename,
            "bundle": {},
            "children": [{"id": item_id} for item_id in children or []],
        }
        qry = CreateEntityQuery(self.bundles, payload, return_type)
        self.context.add_query(qry)
        return return_type

    def search(self, query_text: str) -> EntityCollection[DriveItem]:
        """Search the hierarchy of items for items matching a query.

        Args:
            query_text (str):
        """
        return_type = DriveItemCollection(self.context, self.items.resource_path)
        qry = FunctionQuery(self, "search", {"q": query_text}, return_type)
        self.context.add_query(qry)
        return return_type

    def recent(self) -> EntityCollection[DriveItem]:
        """
        List a set of items that have been recently used by the signed in user.
        This collection includes items that are in the user's drive as well as items
        they have access to from other drives.
        """
        return_type = DriveItemCollection(self.context, self.items.resource_path)
        qry = FunctionQuery(self, "recent", None, return_type)
        self.context.add_query(qry)
        return return_type

    def shared_with_me(self) -> EntityCollection[DriveItem]:
        """Retrieve a collection of DriveItem resources that have been shared with the owner of the Drive."""
        return_type = DriveItemCollection(self.context, self.items.resource_path)
        qry = FunctionQuery(self, "sharedWithMe", None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def drive_type(self) -> Optional[str]:
        """
        Describes the type of drive represented by this resource. OneDrive personal drives will return personal.
        OneDrive for Business will return business. SharePoint document libraries will return documentLibrary.
        """
        return self.properties.get("driveType", None)

    @odata(name="sharepointIds")
    @property
    def sharepoint_ids(self) -> SharePointIds:
        """Returns identifiers useful for SharePoint REST compatibility."""
        return self.properties.get("sharepointIds", SharePointIds())

    @property
    def system(self) -> SystemFacet:
        """Optional. The user account that owns the drive. Read-only."""
        return self.properties.get("system", SystemFacet())

    @property
    def owner(self) -> IdentitySet:
        """If present, indicates that this is a system-managed drive. Read-only."""
        return self.properties.get("owner", IdentitySet())

    @property
    @require_permission(
        delegated=[
            "Files.Read",
            "Files.Read.All",
            "Files.ReadWrite",
            "Files.ReadWrite.All",
            "Sites.Read.All",
            "Sites.ReadWrite.All",
        ],
        application=["Files.Read.All", "Files.ReadWrite.All", "Sites.Read.All", "Sites.ReadWrite.All"],
        notes="Get root folder of a drive",
    )
    def root(self) -> DriveItem:
        """The root folder of the drive."""
        return self.properties.get(
            "root", DriveItem(self.context, RootPath(self.resource_path, self.items.resource_path))
        )

    @property
    def list(self) -> List:
        """For drives in SharePoint, the underlying document library list."""
        return self.properties.get("list", List(self.context, ResourcePath("list", self.resource_path)))

    @property
    def bundles(self) -> EntityCollection[DriveItem]:
        """Bundle metadata, if the item is a bundle."""
        return self.properties.get(
            "bundles", DriveItemCollection(self.context, ResourcePath("bundles", self.resource_path))
        )

    @property
    def items(self) -> EntityCollection[DriveItem]:
        """All items contained in the drive."""
        return self.properties.get("items", DriveItemCollection(self.context, ResourcePath("items", self.resource_path)))

    @property
    @require_permission(
        delegated=[
            "Files.Read",
            "Files.Read.All",
            "Files.ReadWrite",
            "Files.ReadWrite.All",
            "Sites.Read.All",
            "Sites.ReadWrite.All",
        ],
        application=["Files.Read.All", "Files.ReadWrite.All"],
        notes="List items the signed-in user is following. Not supported for personal Microsoft accounts.",
    )
    def following(self) -> EntityCollection[DriveItem]:
        """The list of items the user is following. Only in OneDrive for Business."""
        return self.properties.get(
            "following", DriveItemCollection(self.context, ResourcePath("following", self.resource_path))
        )

    @property
    def quota(self) -> Quota:
        """Optional. Information about the drive's storage space quota. Read-only."""
        return self.properties.get("quota", Quota())

    @property
    @require_permission(
        delegated=[
            "Files.Read",
            "Files.Read.All",
            "Files.ReadWrite",
            "Files.ReadWrite.All",
            "Sites.Read.All",
            "Sites.ReadWrite.All",
        ],
        application=["Files.Read.All", "Files.ReadWrite.All", "Sites.Read.All", "Sites.ReadWrite.All"],
        notes="Access special folders by canonical name (e.g. 'Documents', 'CameraRoll')",
    )
    def special(self) -> EntityCollection[DriveItem]:
        """Collection of special folders available in OneDrive. Read-only. Nullable."""
        return self.properties.get(
            "special", DriveItemCollection(self.context, ResourcePath("special", self.resource_path))
        )

    @property
    def list_(self) -> List:
        """Gets the list property"""
        return self.properties.get("list", List(self.context, ResourcePath("list", self.resource_path)))

    @property
    def recycle_bin(self) -> RecycleBin:
        """Represents a container for a collection of recycleBinItem resources in a SharePoint site or a
        SharePoint Embedded fileStorageContainer."""
        return self.properties.get(
            "recycleBin", RecycleBin(self.context, ResourcePath("recycleBin", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Drive"
