from office365.onedrive.base_item import BaseItem
from office365.runtime.resource_path_entity import ResourcePathEntity


class DriveItem(BaseItem):
    """The driveItem resource represents a file, folder, or other item stored in a drive. All file system objects in
    OneDrive and SharePoint are returned as driveItem resources """

    def item_with_path(self, path):
        """Retrieve DriveItem by path"""
        return DriveItem(self.context,
                         ResourcePathEntity(self.context, self.resource_path, ':/{0}'.format(path)))
