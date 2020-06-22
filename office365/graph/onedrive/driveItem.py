from functools import partial
from office365.graph.directory.permission_collection import PermissionCollection
from office365.graph.onedrive.folder import Folder
from office365.graph.onedrive.conflictBehavior import ConflictBehavior
from office365.graph.onedrive.file import File
from office365.graph.onedrive.fileSystemInfo import FileSystemInfo
from office365.graph.onedrive.uploadSession import UploadSession
from office365.runtime.client_query import CreateEntityQuery
from office365.runtime.client_result import ClientResult
from office365.runtime.resource_path import ResourcePath
from office365.graph.base_item import BaseItem
from office365.graph.onedrive.listItem import ListItem
from office365.runtime.queries.serviceOperationQuery import ServiceOperationQuery


def _content_downloaded(file_object, result):
    file_object.write(result.value)


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
        existing file in a single API call. This method only supports files up to 4MB in size.

        :param name: The contents of the request body should be the binary stream of the file to be uploaded.
        :type name: str
        :param content: The contents of the request body should be the binary stream of the file to be uploaded.
        :type content: str
        :rtype: DriveItem
        """
        from office365.graph.graph_client import UploadContentQuery
        qry = UploadContentQuery(self, name, content)
        self.context.add_query(qry)
        return qry.return_type

    def get_content(self):
        """Download the contents of the primary stream (file) of a DriveItem. Only driveItems with the file property
        can be downloaded. """
        from office365.graph.graph_client import DownloadContentQuery
        qry = DownloadContentQuery(self)
        self.context.add_query(qry)
        return qry.return_type

    def download(self, file_object):
        self.get_content()
        self.context.afterExecuteOnce += partial(_content_downloaded, file_object)

    def create_folder(self, name):
        """Create a new folder or DriveItem in a Drive with a specified parent item or path.

        :param name: Folder name
        :type name: str
        """
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
        """Converts the contents of an item in a specific format

        :param format_name: Specify the format the item's content should be downloaded as.
        :type format_name: str
        :rtype: ClientResult
        """
        from office365.graph.graph_client import DownloadContentQuery
        qry = DownloadContentQuery(self, format_name)
        self.context.add_query(qry)
        return qry.return_type

    def copy(self, name, parent_reference=None):
        """Asynchronously creates a copy of an driveItem (including any children), under a new parent item or with a
        new name.

        :type name: str
        :type parent_reference: ItemReference or None
        """
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
        to move.

        :type name: str
        :type parent_reference: ItemReference
        """
        from office365.graph.graph_client import ReplaceMethodQuery
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
        a whole drive, or files shared with the current user.

        :type query_text: str"""
        from office365.graph.graph_client import SearchQuery
        result = ClientResult(None)
        qry = SearchQuery(self, query_text, result)
        self.context.add_query(qry)
        return result

    def invite(self, recipients, message, require_sign_in=True, send_invitation=True, roles=None):
        """Sends a sharing invitation for a driveItem. A sharing invitation provides permissions to the recipients
        and optionally sends them an email with a sharing link.

        :param recipients: A collection of recipients who will receive access and the sharing invitation.
        :type recipients: list[DriveRecipient]

        :param message: A plain text formatted message that is included in the sharing invitation. Maximum length 2000 characters.
        :type message: str

        :param require_sign_in: Specifies whether the recipient of the invitation is required to sign-in to view the shared item.
        :type require_sign_in: bool

        :param send_invitation: If true, a sharing link is sent to the recipient. Otherwise, a permission is granted directly without sending a notification.
        :type send_invitation: bool

        :param roles: Specify the roles that are to be granted to the recipients of the sharing invitation.
        :type roles: list[str]
        """
        if roles is None:
            roles = ["read"]
        permissions = PermissionCollection(self.context)
        payload = {
            "requireSignIn": require_sign_in,
            "sendInvitation": send_invitation,
            "roles": roles,
            "recipients": recipients,
            "message": message
        }
        qry = ServiceOperationQuery(self, "invite", payload, None, None, permissions)
        self.context.add_query(qry)
        return permissions

    @property
    def fileSystemInfo(self):
        """File system information on client."""
        if self.is_property_available('fileSystemInfo'):
            return self.properties['fileSystemInfo']
        else:
            return FileSystemInfo()

    @property
    def folder(self):
        """Folder metadata, if the item is a folder."""
        if self.is_property_available('folder'):
            return self.properties['folder']
        else:
            return Folder()

    @property
    def file(self):
        """File metadata, if the item is a file."""
        if self.is_property_available('file'):
            return self.properties['file']
        else:
            return File()

    @property
    def children(self):
        """Collection containing Item objects for the immediate children of Item. Only items representing folders
        have children."""
        if self.is_property_available('children'):
            return self.properties['children']
        else:
            from office365.graph.onedrive.driveItemCollection import DriveItemCollection
            return DriveItemCollection(self.context, ResourcePath("children", self.resource_path))

    @property
    def listItem(self):
        """For drives in SharePoint, the associated document library list item."""
        if self.is_property_available('listItem'):
            return self.properties['listItem']
        else:
            return ListItem(self.context, ResourcePath("listItem", self.resource_path))

    @property
    def permissions(self):
        """The set of permissions for the item. Read-only. Nullable."""
        if self.is_property_available('permissions'):
            return self.properties['permissions']
        else:
            return PermissionCollection(self.context, ResourcePath("permissions", self.resource_path))

    def set_property(self, name, value, persist_changes=True):
        super(DriveItem, self).set_property(name, value, persist_changes)
        if name == "id" and self._resource_path.parent.segment == "children":
            self._resource_path = ResourcePath(
                value,
                ResourcePath("items", self._parent_collection.resource_path.parent.parent))
