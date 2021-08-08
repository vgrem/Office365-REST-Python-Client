from office365.base_item import BaseItem
from office365.entity_collection import EntityCollection
from office365.onedrive.driveitems.driveItem import DriveItem
from office365.onedrive.lists.list import List
from office365.onedrive.internal.root_resource_path import RootResourcePath
from office365.onedrive.system_facet import SystemFacet
from office365.runtime.resource_path import ResourcePath


class Drive(BaseItem):
    """The drive resource is the top level object representing a user's OneDrive or a document library in
    SharePoint. """

    @property
    def system(self):
        """If present, indicates that this is a system-managed drive. Read-only."""
        return self.properties.get('system', SystemFacet())

    @property
    def shared_with_me(self):
        """Retrieve a collection of DriveItem resources that have been shared with the owner of the Drive.

        :rtype: EntityCollection
        """
        return self.get_property('sharedWithMe',
                                 EntityCollection(self.context, DriveItem,
                                                  ResourcePath("sharedWithMe", self.resource_path)))

    @property
    def root(self):
        """The root folder of the drive.

        :rtype: DriveItem
        """
        return self.get_property('root', DriveItem(self.context, RootResourcePath(self.resource_path)))

    @property
    def list(self):
        """For drives in SharePoint, the underlying document library list.

        :rtype: List
        """
        return self.get_property('list', List(self.context, ResourcePath("list", self.resource_path)))

    @property
    def items(self):
        """All items contained in the drive.

        :rtype: EntityCollection
        """
        return self.get_property('items',
                                 EntityCollection(self.context, DriveItem, ResourcePath("items", self.resource_path)))

    @property
    def following(self):
        """The list of items the user is following. Only in OneDrive for Business.

        :rtype: EntityCollection
        """
        return self.get_property('following',
                                 EntityCollection(self.context, DriveItem,
                                                  ResourcePath("following", self.resource_path)))

    @property
    def special(self):
        """Collection of common folders available in OneDrive. Read-only. Nullable.

        :rtype: EntityCollection
        """
        return self.get_property('special',
                                 EntityCollection(self.context, DriveItem,
                                                  ResourcePath("special", self.resource_path)))
