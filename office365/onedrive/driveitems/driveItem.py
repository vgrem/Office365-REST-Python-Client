import os

from office365.onedrive.driveitems.audio import Audio
from office365.onedrive.driveitems.geo_coordinates import GeoCoordinates
from office365.onedrive.driveitems.image import Image
from office365.onedrive.driveitems.item_preview_info import ItemPreviewInfo
from office365.onedrive.driveitems.photo import Photo
from office365.onedrive.driveitems.special_folder import SpecialFolder
from office365.onedrive.internal.queries.resumable_file_upload import create_resumable_file_upload_query
from office365.onedrive.internal.queries.upload_content import create_upload_content_query
from office365.base_item import BaseItem
from office365.onedrive.analytics.item_activity_stat import ItemActivityStat
from office365.onedrive.analytics.item_analytics import ItemAnalytics
from office365.onedrive.permissions.permission import Permission
from office365.entity_collection import EntityCollection
from office365.onedrive.internal.paths.children import ChildrenPath
from office365.onedrive.driveitems.conflict_behavior import ConflictBehavior
from office365.onedrive.shares.shared import Shared
from office365.onedrive.versions.drive_item import DriveItemVersion
from office365.onedrive.files.file import File
from office365.onedrive.files.system_info import FileSystemInfo
from office365.onedrive.folders.folder import Folder
from office365.onedrive.listitems.list_item import ListItem
from office365.onedrive.driveitems.publication_facet import PublicationFacet
from office365.onedrive.driveitems.thumbnail_set import ThumbnailSet
from office365.onedrive.workbooks.workbook import Workbook
from office365.onedrive.internal.paths.url import UrlPath
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.upload_session import UploadSessionQuery
from office365.subscriptions.subscription import Subscription


class DriveItem(BaseItem):
    """The driveItem resource represents a file, folder, or other item stored in a drive. All file system objects in
    OneDrive and SharePoint are returned as driveItem resources """

    def get_by_path(self, url_path):
        """
        Retrieve DriveItem by server relative path

        :type url_path: str
        """
        return DriveItem(self.context, UrlPath(url_path, self.resource_path), self.children)

    def create_powerpoint(self, name):
        """
        Creates a PowerPoint file

        :param str name:
        """
        return self.upload(name, None)

    def create_link(self, link_type, scope="", expiration_datetime=None, password=None, message=None):
        """
        The createLink action will create a new sharing link if the specified link type doesn't already exist
        for the calling application. If a sharing link of the specified type already exists for the app,
        the existing sharing link will be returned.

        :param str link_type: The type of sharing link to create. Either view, edit, or embed.
        :param str scope:  The scope of link to create. Either anonymous or organization.
        :param str expiration_datetime: A String with format of yyyy-MM-ddTHH:mm:ssZ of DateTime indicates
            the expiration time of the permission.
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
        return_type = Permission(self.context)
        self.permissions.add_child(return_type)
        qry = ServiceOperationQuery(self, "createLink", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

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
        qry = ServiceOperationQuery(self, "checkout")
        self.context.add_query(qry)
        return self

    def checkin(self, comment, checkin_as=""):
        """
        Check in a checked out driveItem resource, which makes the version of the document available to others.

        :param str comment: comment to the new version of the file
        :param str checkin_as: The status of the document after the check-in operation is complete.
            Can be published or unspecified.
        """
        qry = ServiceOperationQuery(self,
                                    "checkin",
                                    None,
                                    {
                                        "comment": comment,
                                        "checkInAs": checkin_as
                                    }
                                    )
        self.context.add_query(qry)
        return self

    def resumable_upload(self, source_path, chunk_size=2000000, chunk_uploaded=None):
        """
        Create an upload session to allow your app to upload files up to the maximum file size.
        An upload session allows your app to upload ranges of the file in sequential API requests,
        which allows the transfer to be resumed if a connection is dropped while the upload is in progress.

        To upload a file using an upload session, there are two steps:
            Create an upload session
            Upload bytes to the upload session

        :param chunk_uploaded:
        :param str source_path: File path
        :param int chunk_size: chunk size
        """
        file_name = os.path.basename(source_path)
        return_type = DriveItem(self.context, UrlPath(file_name, self.resource_path))
        qry = create_resumable_file_upload_query(return_type, source_path, chunk_size, chunk_uploaded)
        self.context.add_query(qry)
        return return_type

    def create_upload_session(self, item):
        """Creates a temporary storage location where the bytes of the file will be saved until the complete file is
        uploaded.

        :type item: office365.graph.onedrive.driveItemUploadableProperties.DriveItemUploadableProperties
        """
        qry = UploadSessionQuery(self, {"item": item})
        self.context.add_query(qry)
        return qry.return_type

    def upload(self, name, content):
        """The simple upload API allows you to provide the contents of a new file or update the contents of an
        existing file in a single API call. This method only supports files up to 4MB in size.

        :param name: The contents of the request body should be the binary stream of the file to be uploaded.
        :type name: str
        :param content: The contents of the request body should be the binary stream of the file to be uploaded.
        :type content: str or bytes or None
        :rtype: DriveItem
        """
        qry = create_upload_content_query(self, name, content)
        self.children.add_child(qry.return_type)
        self.context.add_query(qry)
        return qry.return_type

    def get_content(self):
        """Download the contents of the primary stream (file) of a DriveItem. Only driveItems with the file property
        can be downloaded. """
        from office365.onedrive.internal.queries.download_content import create_download_content_query
        qry = create_download_content_query(self)
        self.context.add_query(qry)
        return qry.return_type

    def download(self, file_object):
        """
        :type file_object: typing.IO
        """
        result = self.get_content()

        def _content_downloaded(resp):
            """
            :type resp: requests.Response
            """
            resp.raise_for_status()
            file_object.write(result.value)

        self.context.after_execute(_content_downloaded)
        return self

    def download_session(self, file_object, chunk_downloaded=None, chunk_size=1024 * 1024):
        """
        :type file_object: typing.IO
        :type chunk_downloaded: (int)->None or None
        :type chunk_size: int
        """
        from office365.onedrive.internal.queries.download_content import create_download_session_content_query
        qry = create_download_session_content_query(self)

        def _construct_download_request(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            request.stream = True
            request.method = HttpMethod.Get

        def _process_download_response(response):
            bytes_read = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                bytes_read += len(chunk)
                if callable(chunk_downloaded):
                    chunk_downloaded(bytes_read)
                file_object.write(chunk)

        self.context.before_execute(_construct_download_request)
        self.context.after_execute(_process_download_response)
        self.context.add_query(qry)
        return self

    def create_folder(self, name):
        """Create a new folder or DriveItem in a Drive with a specified parent item or path.

        :param str name: Folder name
        """
        return_type = DriveItem(self.context)
        self.children.add_child(return_type)
        payload = {
            "name": name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": ConflictBehavior.Rename
        }
        qry = CreateEntityQuery(self.children, payload, return_type)
        self.context.add_query(qry)
        return return_type

    def convert(self, format_name):
        """Converts the contents of an item in a specific format

        :param format_name: Specify the format the item's content should be downloaded as.
        :type format_name: str
        :rtype: ClientResult
        """
        from office365.onedrive.internal.queries.download_content import create_download_content_query
        qry = create_download_content_query(self, format_name)
        self.context.add_query(qry)
        return qry.return_type

    def copy(self, name, parent_reference=None):
        """Asynchronously creates a copy of an driveItem (including any children), under a new parent item or with a
        new name.

        :type name: str
        :type parent_reference: office365.onedrive.listitems.item_reference.ItemReference or None
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
        :type parent_reference: office365.onedrive.listitems.item_reference.ItemReference
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
        """
        return_type = EntityCollection(self.context, DriveItem, ResourcePath("items", self.resource_path))
        qry = FunctionQuery(self, "search", {"q": query_text}, return_type)
        self.context.add_query(qry)
        return return_type

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
        return_type = EntityCollection(self.context, Permission)
        payload = {
            "requireSignIn": require_sign_in,
            "sendInvitation": send_invitation,
            "roles": roles,
            "recipients": recipients,
            "message": message
        }
        qry = ServiceOperationQuery(self, "invite", payload, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_activities_by_interval(self, start_dt=None, end_dt=None, interval=None):
        """
        Get a collection of itemActivityStats resources for the activities that took place on this resource
        within the specified time interval.

        :param datetime.datetime start_dt: The start time over which to aggregate activities.
        :param datetime.datetime end_dt: The end time over which to aggregate activities.
        :param str interval: The aggregation interval.
        """
        params = {
            "startDateTime": start_dt.strftime('%m-%d-%Y') if start_dt else None,
            "endDateTime": end_dt.strftime('%m-%d-%Y') if end_dt else None,
            "interval": interval
        }
        return_type = EntityCollection(self.context, ItemActivityStat, self.resource_path)
        qry = FunctionQuery(self, "getActivitiesByInterval", params, return_type)
        self.context.add_query(qry)
        return return_type

    def restore(self, parent_reference, name):
        """
        Restore a driveItem that has been deleted and is currently in the recycle bin.
        NOTE: This functionality is currently only available for OneDrive Personal.

        :type name: str
        :type parent_reference: office365.onedrive.listitems.item_reference.ItemReference or None
        """
        payload = {
            "name": name,
            "parentReference": parent_reference
        }
        return_type = DriveItem(self.context)
        self.children.add_child(return_type)
        qry = ServiceOperationQuery(self, "restore", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def preview(self, page, zoom=None):
        """
        This action allows you to obtain a short-lived embeddable URL for an item in order
        to render a temporary preview.

        :param str or int page: Optional. Page number of document to start at, if applicable.
            Specified as string for future use cases around file types such as ZIP.
        :param int zoom: Optional. Zoom level to start at, if applicable.

        """
        payload = {
            "page": page,
            "zoom": zoom
        }
        result = ClientResult(self.context, ItemPreviewInfo())
        qry = ServiceOperationQuery(self, "preview", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def validate_permission(self, challenge_token=None, password=None):
        """
        :type challenge_token: str
        :type password: str
        """
        payload = {
            "challengeToken": challenge_token,
            "password": password
        }
        qry = ServiceOperationQuery(self, "validatePermission", None, payload)
        self.context.add_query(qry)
        return self

    @property
    def audio(self):
        """
        Audio metadata, if the item is an audio file. Read-only.
        """
        return self.properties.get("audio", Audio())

    @property
    def image(self):
        """
        Image metadata, if the item is an image. Read-only.
        """
        return self.properties.get("image", Image())

    @property
    def photo(self):
        """
        Photo metadata, if the item is a photo. Read-only.
        """
        return self.properties.get("photo", Photo())

    @property
    def location(self):
        """
        Location metadata, if the item has location data. Read-only.
        """
        return self.properties.get("location", GeoCoordinates())

    @property
    def file_system_info(self):
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
        """Determines whether the provided drive item is folder facet"""
        return self.is_property_available("folder")

    @property
    def is_file(self):
        """Determines whether the provided drive item is file facet"""
        return self.is_property_available("file")

    @property
    def shared(self):
        """Indicates that the item has been shared with others and provides information about the shared state
        of the item. Read-only."""
        return self.properties.get('shared', Shared())

    @property
    def web_dav_url(self):
        """
        WebDAV compatible URL for the item.

        :rtype: str or None
        """
        return self.properties.get("webDavUrl", None)

    @property
    def children(self):
        """Collection containing Item objects for the immediate children of Item. Only items representing folders
        have children.

        :rtype: EntityCollection
        """
        return self.get_property('children',
                                 EntityCollection(self.context, DriveItem, ChildrenPath(self.resource_path)))

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
                                   EntityCollection(self.context, Permission,
                                                    ResourcePath("permissions", self.resource_path)))

    @property
    def publication(self):
        """Provides information about the published or checked-out state of an item,
        in locations that support such actions. This property is not returned by default. Read-only."""
        return self.properties.get('publication', PublicationFacet())

    @property
    def special_folder(self):
        """If the current item is also available as a special folder, this facet is returned. Read-only."""
        return self.properties.get('specialFolder', SpecialFolder())

    @property
    def versions(self):
        """The list of previous versions of the item. For more info, see getting previous versions.
        Read-only. Nullable."""
        return self.properties.get('versions',
                                   EntityCollection(self.context, DriveItemVersion,
                                                    ResourcePath("versions", self.resource_path)))

    @property
    def thumbnails(self):
        """Collection containing ThumbnailSet objects associated with the item. For more info, see getting thumbnails.
        Read-only. Nullable."""
        return self.properties.get('thumbnails',
                                   EntityCollection(self.context, ThumbnailSet,
                                                    ResourcePath("thumbnails", self.resource_path)))

    @property
    def analytics(self):
        """Analytics about the view activities that took place on this item."""
        return self.properties.get('analytics',
                                   ItemAnalytics(self.context, ResourcePath("analytics", self.resource_path)))

    @property
    def delta(self):
        """This method allows your app to track changes to a drive item and its children over time."""
        return self.properties.get('delta',
                                   EntityCollection(self.context, DriveItem, ResourcePath("delta", self.resource_path)))

    @property
    def subscriptions(self):
        """The set of subscriptions on the driveItem.
        """
        return self.properties.get('subscriptions',
                                   EntityCollection(self.context, Subscription,
                                                    ResourcePath("subscriptions", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "fileSystemInfo": self.file_system_info,
            }
            default_value = property_mapping.get(name, None)
        return super(DriveItem, self).get_property(name, default_value)
