from office365.actions.search_query import create_search_query
from office365.actions.upload_content_query import create_upload_content_query
from office365.base_item import BaseItem
from office365.directory.permission import Permission
from office365.directory.permission_collection import PermissionCollection
from office365.entity_collection import EntityCollection
from office365.onedrive.children_resource_path import ChildrenResourcePath
from office365.onedrive.conflictBehavior import ConflictBehavior
from office365.onedrive.driveItemVersion import DriveItemVersion
from office365.onedrive.file import File
from office365.onedrive.fileSystemInfo import FileSystemInfo
from office365.onedrive.folder import Folder
from office365.onedrive.listItem import ListItem
from office365.onedrive.publicationFacet import PublicationFacet
from office365.onedrive.root_resource_path import RootResourcePath
from office365.onedrive.uploadSession import UploadSession
from office365.excel.workbook import Workbook
from office365.resource_path_url import ResourcePathUrl
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.create_entity_query import CreateEntityQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath


class DriveItem(BaseItem):
    """The driveItem resource represents a file, folder, or other item stored in a drive. All file system objects in
    OneDrive and SharePoint are returned as driveItem resources """

    def get_by_path(self, url_path):
        """
        Retrieve DriveItem by path

        :type url_path: str
        """
        return DriveItem(self.context, ResourcePathUrl(url_path, self.resource_path))

    def create_link(self, link_type, scope="", expiration_datetime=None, password=None, message=None):
        """
        The createLink action will create a new sharing link if the specified link type doesn't already exist
        for the calling application. If a sharing link of the specified type already exists for the app,
        the existing sharing link will be returned.

        :param str link_type: The type of sharing link to create. Either view, edit, or embed.
        :param str scope:  The scope of link to create. Either anonymous or organization.
        :param str expiration_datetime: A String with format of yyyy-MM-ddTHH:mm:ssZ of DateTime indicates the expiration
            time of the permission.
        :param str password: The password of the sharing link that is set by the creator. Optional
            and OneDrive Personal only.
        :param str message:
        """
        payload = {
            "type": link_type,
            "scope": scope,
            "message": message,
            "expirationDateTime": expiration_datetime,
            "password": password
        }
        permission = Permission(self.context)
        self.permissions.add_child(permission)
        qry = ServiceOperationQuery(self, "createLink", None, payload, None, permission)
        self.context.add_query(qry)
        return permission

    def follow(self):
        """
        Follow a driveItem.
        """
        qry = ServiceOperationQuery(self, "follow")
        self.context.add_query(qry)
        return self

    def unfollow(self):
        """
        Unfollow a driveItem.
        """
        qry = ServiceOperationQuery(self, "unfollow")
        self.context.add_query(qry)
        return self

    def checkout(self):
        """
        Check out a driveItem resource to prevent others from editing the document, and prevent your changes
        from being visible until the documented is checked in.
        """
        qry = ServiceOperationQuery(self,
                                    "checkout",
                                    None
                                    )
        self.context.add_query(qry)
        return self

    def checkin(self, comment, checkInAs=""):
        """
        Check in a checked out driveItem resource, which makes the version of the document available to others.

        :param str comment: comment to the new version of the file
        :param str checkInAs: The status of the document after the check-in operation is complete.
            Can be published or unspecified.
        """
        qry = ServiceOperationQuery(self,
                                    "checkin",
                                    None,
                                    {
                                        "comment": comment,
                                        "checkInAs": checkInAs
                                    }
                                    )
        self.context.add_query(qry)
        return self

    def resumable_upload(self, source_path, chunk_size=1000000, chunk_uploaded=None):
        """
        Create an upload session to allow your app to upload files up to the maximum file size.
        An upload session allows your app to upload ranges of the file in sequential API requests,
        which allows the transfer to be resumed if a connection is dropped while the upload is in progress.

        To upload a file using an upload session, there are two steps:
            Create an upload session
            Upload bytes to the upload session

        :param chunk_uploaded:
        :param str source_path: Local file path
        :param int chunk_size: chunk size
        """
        from office365.onedrive.file_upload import ResumableFileUpload
        upload_query = ResumableFileUpload(self, source_path, chunk_size, chunk_uploaded)
        self.context.add_query(upload_query)
        return upload_query.return_type.get()

    def create_upload_session(self, item):
        """Creates a temporary storage location where the bytes of the file will be saved until the complete file is
        uploaded.

        :type item: office365.graph.onedrive.driveItemUploadableProperties.DriveItemUploadableProperties
        """
        result = ClientResult(self.context, UploadSession())
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
        qry = create_upload_content_query(self, name, content)
        self.context.add_query(qry)
        return qry.return_type

    def get_content(self):
        """Download the contents of the primary stream (file) of a DriveItem. Only driveItems with the file property
        can be downloaded. """
        from office365.graph_client import DownloadContentQuery
        qry = DownloadContentQuery(self)
        self.context.add_query(qry)
        return qry.return_type

    def download(self, file_object):
        """
        :type file_object: typing.IO
        """
        result = self.get_content()

        def _content_downloaded(resp):
            file_object.write(result.value)

        self.context.after_execute(_content_downloaded)
        return self

    def create_folder(self, name):
        """Create a new folder or DriveItem in a Drive with a specified parent item or path.

        :param str name: Folder name
        """
        drive_item = DriveItem(self.context, None)
        self.children.add_child(drive_item)
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
        from office365.graph_client import DownloadContentQuery
        qry = DownloadContentQuery(self, format_name)
        self.context.add_query(qry)
        return qry.return_type

    def copy(self, name, parent_reference=None):
        """Asynchronously creates a copy of an driveItem (including any children), under a new parent item or with a
        new name.

        :type name: str
        :type parent_reference: ItemReference or None
        """
        result = ClientResult(self.context)
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

        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self,
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

        def _construct_request(request):
            request.method = HttpMethod.Patch

        self.context.before_execute(_construct_request)
        return result

    def search(self, query_text):
        """Search the hierarchy of items for items matching a query. You can search within a folder hierarchy,
        a whole drive, or files shared with the current user.

        :type query_text: str
        :rtype: ClientResult
        """
        qry = create_search_query(self, query_text)
        self.context.add_query(qry)
        return qry.return_type

    def invite(self, recipients, message, require_sign_in=True, send_invitation=True, roles=None):
        """Sends a sharing invitation for a driveItem. A sharing invitation provides permissions to the recipients
        and optionally sends them an email with a sharing link.

        :param list[DriveRecipient] recipients: A collection of recipients who will receive access and the sharing
        invitation.
        :param str message: A plain text formatted message that is included in the sharing invitation.
        Maximum length 2000 characters.
        :param bool require_sign_in: Specifies whether the recipient of the invitation is required to sign-in to view
        the shared item.
        :param bool send_invitation: If true, a sharing link is sent to the recipient. Otherwise, a permission is
        granted directly without sending a notification.
        :param list[str] roles: Specify the roles that are to be granted to the recipients of the sharing invitation.
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
        return self.properties.get('fileSystemInfo', FileSystemInfo())

    @property
    def folder(self):
        """Folder metadata, if the item is a folder."""
        return self.properties.get('folder', Folder())

    @property
    def file(self):
        """File metadata, if the item is a file."""
        return self.properties.get('file', File())

    @property
    def is_folder(self):
        return self.is_property_available("folder")

    @property
    def is_file(self):
        return self.is_property_available("file")

    @property
    def children(self):
        """Collection containing Item objects for the immediate children of Item. Only items representing folders
        have children."""
        from office365.onedrive.driveItemCollection import DriveItemCollection
        return self.properties.get('children',
                                   DriveItemCollection(self.context, ChildrenResourcePath(self.resource_path)))

    @property
    def listItem(self):
        """For drives in SharePoint, the associated document library list item."""
        return self.properties.get('listItem', ListItem(self.context, ResourcePath("listItem", self.resource_path)))

    @property
    def workbook(self):
        """For files that are Excel spreadsheets, accesses the workbook API to work with the spreadsheet's contents. """
        return self.properties.get('workbook', Workbook(self.context, ResourcePath("workbook", self.resource_path)))

    @property
    def permissions(self):
        """The set of permissions for the item. Read-only. Nullable."""
        return self.properties.get('permissions',
                                   PermissionCollection(self.context, ResourcePath("permissions", self.resource_path)))

    @property
    def publication(self):
        """Provides information about the published or checked-out state of an item,
        in locations that support such actions. This property is not returned by default. Read-only."""
        return self.properties.get('publication', PublicationFacet())

    @property
    def versions(self):
        """The list of previous versions of the item. For more info, see getting previous versions.
        Read-only. Nullable."""
        return self.properties.get('versions',
                                   EntityCollection(self.context, DriveItemVersion,
                                                    ResourcePath("versions", self.resource_path)))

    def set_property(self, name, value, persist_changes=True):
        if self._resource_path is None and name == "id":
            self._resource_path = self._resolve_path(value)
        super(DriveItem, self).set_property(name, value, persist_changes)
        return self

    def _resolve_path(self, item_id):
        path = None
        parent_path = self.parent_collection.resource_path
        while path is None:
            if isinstance(parent_path, ChildrenResourcePath) or isinstance(parent_path, ResourcePathUrl) or isinstance(parent_path, RootResourcePath):
                parent_path = parent_path.parent
            elif parent_path.segment == "items":
                path = ResourcePath(item_id, parent_path)
            else:
                path = ResourcePath(item_id, ResourcePath("items", parent_path))
        return path
