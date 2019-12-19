from office365.onedrive.conflictBehavior import ConflictBehavior
from office365.onedrive.fileSystemInfo import FileSystemInfo
from office365.onedrive.uploadSession import UploadSession
from office365.runtime.client_query import ClientQuery, ServiceOperationQuery
from office365.runtime.client_result import ClientResult
from office365.runtime.resource_path_entity import ResourcePathEntity
from office365.onedrive.baseItem import BaseItem
from office365.onedrive.listItem import ListItem
from office365.runtime.resource_path_url import ResourcePathUrl
from office365.runtime.utilities.http_method import HttpMethod


class DriveItem(BaseItem):
    """The driveItem resource represents a file, folder, or other item stored in a drive. All file system objects in
    OneDrive and SharePoint are returned as driveItem resources """

    def create_upload_session(self, item):
        """Creates a temporary storage location where the bytes of the file will be saved until the complete file is
        uploaded. """
        qry = ServiceOperationQuery(self,
                                    HttpMethod.Post,
                                    "createUploadSession",
                                    None,
                                    {
                                        "item": item
                                    }
                                    )
        result = ClientResult(UploadSession())
        self.context.add_query(qry, result)
        return result

    def upload(self, name, content):
        """The simple upload API allows you to provide the contents of a new file or update the contents of an
        existing file in a single API call. This method only supports files up to 4MB in size. """
        drive_item = DriveItem(self.context, ResourcePathUrl(self.context, self.resourcePath, name))
        qry = ClientQuery(r"{0}content".format(drive_item.resourceUrl), HttpMethod.Put, content)
        self.context.add_query(qry, drive_item)
        return drive_item

    def download(self):
        """Download the contents of the primary stream (file) of a DriveItem. Only driveItems with the file property
        can be downloaded. """
        url = r"{0}content".format(self.resourceUrl)
        qry = ClientQuery(url, HttpMethod.Get)
        result = ClientResult(None)
        self.context.add_query(qry, result)
        return result

    def create_folder(self, name):
        """Create a new folder or DriveItem in a Drive with a specified parent item or path."""
        drive_item = DriveItem(self.context, None)
        drive_item._parent_collection = self.children
        payload = {
            "name": name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": ConflictBehavior.Rename
        }
        qry = ClientQuery(self.resourceUrl + "/children", HttpMethod.Post, payload)
        self.context.add_query(qry, drive_item)
        return drive_item

    def convert(self, format_name):
        """Converts the contents of an item in a specific format"""
        url = r"{0}content?format={1}".format(self.resourceUrl, format_name)
        qry = ClientQuery(url, HttpMethod.Get)
        result = ClientResult(None)
        self.context.add_query(qry, result)
        return result

    def copy(self, name, parent_reference=None):
        """Asynchronously creates a copy of an driveItem (including any children), under a new parent item or with a
        new name. """
        qry = ServiceOperationQuery(self,
                                    HttpMethod.Post,
                                    "copy",
                                    None,
                                    {
                                        "name": name,
                                        "parentReference": parent_reference
                                    }
                                    )
        result = ClientResult(None)
        self.context.add_query(qry, result)
        return result

    def move(self, name, parent_reference=None):
        """To move a DriveItem to a new parent item, your app requests to update the parentReference of the DriveItem
        to move. """
        qry = ServiceOperationQuery(self,
                                    HttpMethod.Patch,
                                    "move",
                                    None,
                                    {
                                        "name": name,
                                        "parentReference": parent_reference
                                    }
                                    )
        result = ClientResult(None)
        self.context.add_query(qry, result)
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
            return DriveItemCollection(self.context, ResourcePathEntity(self.context, self.resourcePath, "children"))

    @property
    def listItem(self):
        """For drives in SharePoint, the associated document library list item."""
        if self.is_property_available('listItem'):
            return self.properties['listItem']
        else:
            return ListItem(self.context, ResourcePathEntity(self.context, self.resourcePath, "listItem"))
