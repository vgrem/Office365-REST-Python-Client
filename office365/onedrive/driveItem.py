from office365.onedrive.conflictBehavior import ConflictBehavior
from office365.onedrive.fileSystemInfo import FileSystemInfo
from office365.onedrive.uploadSession import UploadSession
from office365.runtime.client_query import ServiceOperationQuery, CreateEntityQuery
from office365.runtime.client_result import ClientResult
from office365.runtime.resource_path import ResourcePath
from office365.onedrive.baseItem import BaseItem
from office365.onedrive.listItem import ListItem


class DriveItem(BaseItem):
    """The driveItem resource represents a file, folder, or other item stored in a drive. All file system objects in
    OneDrive and SharePoint are returned as driveItem resources """

    def create_upload_session(self, item):
        """Creates a temporary storage location where the bytes of the file will be saved until the complete file is
        uploaded. """
        result = ClientResult(UploadSession())
        qry = ServiceOperationQuery(self,
                                    "createUploadSession",
                                    None,
                                    {
                                        "item": item
                                    },
                                    None,
                                    result
                                    )
        self.context.add_query(qry)
        return result

    def upload(self, name, content):
        """The simple upload API allows you to provide the contents of a new file or update the contents of an
        existing file in a single API call. This method only supports files up to 4MB in size. """
        from office365.graphClient import UploadContentQuery
        qry = UploadContentQuery(self, name, content)
        self.context.add_query(qry)
        return qry.returnType

    def download(self):
        """Download the contents of the primary stream (file) of a DriveItem. Only driveItems with the file property
        can be downloaded. """
        from office365.graphClient import DownloadContentQuery
        qry = DownloadContentQuery(self)
        self.context.add_query(qry)
        return qry.returnType

    def create_folder(self, name):
        """Create a new folder or DriveItem in a Drive with a specified parent item or path."""
        drive_item = DriveItem(self.context, None)
        drive_item._parent_collection = self.children
        payload = {
            "name": name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": ConflictBehavior.Rename
        }
        qry = CreateEntityQuery(self.children, payload, drive_item)
        self.context.add_query(qry)
        return drive_item

    def convert(self, format_name):
        """Converts the contents of an item in a specific format"""
        from office365.graphClient import DownloadContentQuery
        qry = DownloadContentQuery(self, format_name)
        self.context.add_query(qry)
        return qry.returnType

    def copy(self, name, parent_reference=None):
        """Asynchronously creates a copy of an driveItem (including any children), under a new parent item or with a
        new name. """
        result = ClientResult(None)
        qry = ServiceOperationQuery(self,
                                    "copy",
                                    None,
                                    {
                                        "name": name,
                                        "parentReference": parent_reference
                                    },
                                    None,
                                    result
                                    )
        self.context.add_query(qry)
        return result

    def move(self, name, parent_reference=None):
        """To move a DriveItem to a new parent item, your app requests to update the parentReference of the DriveItem
        to move. """
        from office365.graphClient import ReplaceMethodQuery
        result = ClientResult(None)
        qry = ReplaceMethodQuery(self,
                                 "move",
                                 None,
                                 {
                                     "name": name,
                                     "parentReference": parent_reference
                                 },
                                 None,
                                 result
                                 )
        self.context.add_query(qry)
        return result

    def search(self, query_text):
        """Search the hierarchy of items for items matching a query. You can search within a folder hierarchy,
        a whole drive, or files shared with the current user. """
        from office365.graphClient import SearchQuery
        result = ClientResult(None)
        qry = SearchQuery(self, query_text, result)
        self.context.add_query(qry)
        return result

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
            from office365.onedrive.driveItemCollection import DriveItemCollection
            return DriveItemCollection(self.context, ResourcePath("children", self.resourcePath))

    @property
    def listItem(self):
        """For drives in SharePoint, the associated document library list item."""
        if self.is_property_available('listItem'):
            return self.properties['listItem']
        else:
            return ListItem(self.context, ResourcePath("listItem", self.resourcePath))

    def set_property(self, name, value, persist_changes=True):
        super(DriveItem, self).set_property(name, value, persist_changes)
        if name == "id" and self._resource_path.parent.segment == "children":
            self._resource_path = ResourcePath(
                value,
                ResourcePath("items", self._parent_collection.resourcePath.parent.parent))
