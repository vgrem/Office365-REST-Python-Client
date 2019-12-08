from office365.onedrive.file_system_info import FileSystemInfo
from office365.runtime.client_query import ClientQuery
from office365.runtime.resource_path_entity import ResourcePathEntity
from office365.onedrive.base_item import BaseItem
from office365.onedrive.list_item import ListItem
from office365.runtime.utilities.http_method import HttpMethod


class DriveItem(BaseItem):
    """The driveItem resource represents a file, folder, or other item stored in a drive. All file system objects in
    OneDrive and SharePoint are returned as driveItem resources """

    def upload_file(self, name, content):
        """Uploads a file"""
        drive_item = DriveItem(self.context, None)
        qry = ClientQuery(self.resourceUrl + ":/{0}:/content".format(name), HttpMethod.Put, content)
        self.context.add_query(qry, drive_item)
        return drive_item

    def create_folder(self, name):
        """Create a new folder or DriveItem in a Drive with a specified parent item or path."""
        drive_item = DriveItem(self.context, None)
        drive_item._parent_collection = self.children
        payload = {
          "name": name,
          "folder": {},
          "@microsoft.graph.conflictBehavior": "rename"
        }
        qry = ClientQuery(self.resourceUrl + "/children", HttpMethod.Post, payload)
        self.context.add_query(qry, drive_item)
        return drive_item

    @property
    def fileSystemInfo(self):
        """File system information on client."""
        if self.is_property_available('fileSystemInfo'):
            return FileSystemInfo(self.properties['fileSystemInfo'])
        else:
            return None

    @property
    def children(self):
        """Collection containing Item objects for the immediate children of Item. Only items representing folders
        have children."""
        if self.is_property_available('children'):
            return self.properties['children']
        else:
            from office365.onedrive.drive_item_collection import DriveItemCollection
            return DriveItemCollection(self.context, ResourcePathEntity(self.context, self.resourcePath, "children"))

    @property
    def listItem(self):
        """For drives in SharePoint, the associated document library list item."""
        if self.is_property_available('listItem'):
            return self.properties['listItem']
        else:
            return ListItem(self.context, ResourcePathEntity(self.context, self.resourcePath, "listItem"))

    def item_with_path(self, path):
        """Retrieve DriveItem by path"""
        return DriveItem(self.context,
                         ResourcePathEntity(self.context, self.resourcePath, ':/{0}'.format(path)))
