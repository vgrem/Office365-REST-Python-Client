from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.files.file_version_event import FileVersionEvent
from office365.sharepoint.internal.queries.download_file import create_download_file_query
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.directory.user import User
from office365.sharepoint.files.file_version_collection import FileVersionCollection
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.permissions.information_rights_management_settings import InformationRightsManagementSettings
from office365.sharepoint.webparts.limited_webpart_manager import LimitedWebPartManager
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath


class AbstractFile(BaseEntity):
    def read(self):
        """Immediately read content of file"""
        if not self.is_property_available("ServerRelativeUrl"):
            raise ValueError
        response = File.open_binary(
            self.context, self.properties["ServerRelativeUrl"])
        return response.content

    def write(self, content):
        """Immediately writes content of file"""
        if not self.is_property_available("ServerRelativeUrl"):
            raise ValueError
        response = File.save_binary(
            self.context, self.properties["ServerRelativeUrl"], content)
        return response


class File(AbstractFile):
    """Represents a file in a SharePoint Web site that can be a Web Part Page, an item in a document library,
    or a file in a folder."""

    @staticmethod
    def from_url(abs_url):
        """
        Retrieves a File from absolute url

        :type abs_url: str
        """
        from office365.sharepoint.client_context import ClientContext
        ctx = ClientContext.from_url(abs_url)
        file_relative_url = abs_url.replace(ctx.base_url, "")
        file = ctx.web.get_file_by_server_relative_url(file_relative_url)
        return file

    def get_image_preview_uri(self, width, height, client_type=None):
        """
        :param int width:
        :param int height:
        :param str client_type:
        """
        result = ClientResult(self.context)
        payload = {
            "width": width,
            "height": height,
            "clientType": client_type
        }
        qry = ServiceOperationQuery(self, "GetImagePreviewUri", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def get_image_preview_url(self, width, height, client_type=None):
        """
        :param int width:
        :param int height:
        :param str client_type:
        """
        result = ClientResult(self.context)
        payload = {
            "width": width,
            "height": height,
            "clientType": client_type
        }
        qry = ServiceOperationQuery(self, "GetImagePreviewUrl", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def recycle(self):
        """Moves the file to the Recycle Bin and returns the identifier of the new Recycle Bin item."""

        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "Recycle", None, None, None, result)
        self.context.add_query(qry)
        return result

    def approve(self, comment):
        """Approves the file submitted for content approval with the specified comment.

        :type comment: str
        """
        qry = ServiceOperationQuery(self,
                                    "approve",
                                    {
                                        "comment": comment
                                    })
        self.context.add_query(qry)
        return self

    def deny(self, comment):
        """Denies approval for a file that was submitted for content approval.

        :type comment: str
        """
        qry = ServiceOperationQuery(self,
                                    "deny",
                                    {
                                        "comment": comment
                                    })
        self.context.add_query(qry)
        return self

    def copyto(self, new_relative_url, overwrite):
        """Copies the file to the destination URL.

        :type new_relative_url: str
        :type overwrite: bool
        """
        qry = ServiceOperationQuery(self,
                                    "CopyTo",
                                    {
                                        "strNewUrl": new_relative_url,
                                        "boverwrite": overwrite
                                    },
                                    None)
        self.context.add_query(qry)
        return self

    def copyto_using_path(self, decoded_url, overwrite):
        """Copies the file to the destination URL.

        :type decoded_url: str
        :type overwrite: bool
        """
        qry = ServiceOperationQuery(self,
                                    "CopyToUsingPath",
                                    {
                                        "DecodedUrl": decoded_url,
                                        "bOverWrite": overwrite
                                    },
                                    None)
        self.context.add_query(qry)
        return self

    def moveto(self, new_relative_url, flag):
        """Moves the file to the specified destination URL.

        :type new_relative_url: str
        :type flag: int
        """
        qry = ServiceOperationQuery(self,
                                    "moveto",
                                    {
                                        "newurl": new_relative_url,
                                        "flags": flag
                                    },
                                    None)
        self.context.add_query(qry)
        return self

    def publish(self, comment):
        """Submits the file for content approval with the specified comment.
        :type comment: str
        """
        qry = ServiceOperationQuery(self,
                                    "publish",
                                    {
                                        "comment": comment,
                                    }
                                    )
        self.context.add_query(qry)

    def unpublish(self, comment):
        """Removes the file from content approval or unpublish a major version.
        :type comment: str
        """
        qry = ServiceOperationQuery(self,
                                    "unpublish",
                                    {
                                        "comment": comment,
                                    }
                                    )
        self.context.add_query(qry)
        return self

    def checkout(self):
        """Checks out the file from a document library based on the check-out type."""
        qry = ServiceOperationQuery(self,
                                    "checkout",
                                    )
        self.context.add_query(qry)
        return self

    def checkin(self, comment, checkin_type):
        """
        Checks the file in to a document library based on the check-in type.

        :param comment: comment to the new version of the file
        :param checkin_type: 0 (minor), or 1 (major) or 2 (overwrite)
            For more information on checkin types, please see
            https://docs.microsoft.com/en-us/previous-versions/office/sharepoint-csom/ee542953(v%3Doffice.15)
        :type checkin_type: int
        """
        qry = ServiceOperationQuery(self,
                                    "checkin",
                                    {
                                        "comment": comment,
                                        "checkInType": checkin_type
                                    }
                                    )
        self.context.add_query(qry)
        return self

    def undocheckout(self):
        """Reverts an existing checkout for the file."""
        qry = ServiceOperationQuery(self,
                                    "undocheckout"
                                    )
        self.context.add_query(qry)
        return self

    def get_limited_webpart_manager(self, scope):
        """Specifies the control set used to access, modify, or add Web Parts associated with this Web Part Page and
        view. """
        return LimitedWebPartManager(self.context,
                                     ServiceOperationPath(
                                         "getlimitedwebpartmanager",
                                         [scope],
                                         self.resource_path
                                     ))

    def open_binary_stream(self):
        """Opens the file as a stream."""
        return_stream = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "OpenBinaryStream", None, None, None, return_stream)
        self.context.add_query(qry)
        return return_stream

    def save_binary_stream(self, stream):
        """Saves the file."""
        qry = ServiceOperationQuery(self, "SaveBinaryStream", None, {"file": stream})
        self.context.add_query(qry)
        return self

    def get_upload_status(self, upload_id):
        payload = {
            "uploadId": upload_id,
        }
        qry = ServiceOperationQuery(self, "GetUploadStatus", None, payload)
        self.context.add_query(qry)
        return self

    def upload_with_checksum(self, upload_id, checksum, stream):
        """
        :param str upload_id:
        :param str checksum:
        :param bytes stream:
        """
        return_type = File(self.context)
        payload = {
            "uploadId": upload_id,
            "checksum": checksum,
            "stream": stream
        }
        qry = ServiceOperationQuery(self, "UploadWithChecksum", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def cancel_upload(self, upload_id):
        payload = {
            "uploadId": upload_id,
        }
        qry = ServiceOperationQuery(self, "CancelUpload", None, payload)
        self.context.add_query(qry)
        return self

    def start_upload(self, upload_id, content):
        """Starts a new chunk upload session and uploads the first fragment.

        :param bytes content: File content
        :param str upload_id: Upload session id
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self,
                                    "startUpload",
                                    {
                                        "uploadID": upload_id
                                    },
                                    content,
                                    None,
                                    result
                                    )
        self.context.add_query(qry)
        return result

    def continue_upload(self, upload_id, file_offset, content):
        """
        Continues the chunk upload session with an additional fragment. The current file content is not changed.

        :param str upload_id: Upload session id
        :param int file_offset: File offset
        :param bytes content: File content
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self,
                                    "continueUpload",
                                    {
                                        "uploadID": upload_id,
                                        "fileOffset": file_offset,
                                    },
                                    content,
                                    None,
                                    result
                                    )
        self.context.add_query(qry)
        return result

    def finish_upload(self, upload_id, file_offset, content):
        """Uploads the last file fragment and commits the file. The current file content is changed when this method
        completes.

        :param str upload_id: Upload session id
        :param int file_offset: File offset
        :param bytes content: File content
        """
        qry = ServiceOperationQuery(self,
                                    "finishUpload",
                                    {
                                        "uploadID": upload_id,
                                        "fileOffset": file_offset,
                                    },
                                    content,
                                    None,
                                    self
                                    )
        self.context.add_query(qry)
        return self

    @staticmethod
    def save_binary(ctx, server_relative_url, content):
        """Uploads a file

        :type ctx: ClientContext
        :type server_relative_url: str
        :type content: str
        """
        url = r"web/getFileByServerRelativePath(DecodedUrl='{0}')/\$value".format(server_relative_url)
        request = RequestOptions(url)
        request.method = HttpMethod.Post
        request.set_header('X-HTTP-Method', 'PUT')
        request.data = content
        response = ctx.execute_request_direct(request)
        return response

    @staticmethod
    def open_binary(ctx, server_relative_url):
        """
        Returns the file object located at the specified server-relative URL.

        :type ctx: ClientContext
        :type server_relative_url: str
        :return Response
        """
        url = r"web/getFileByServerRelativePath(DecodedUrl='{0}')/\$value".format(server_relative_url)
        request = RequestOptions(url)
        request.method = HttpMethod.Get
        response = ctx.execute_request_direct(request)
        return response

    def download(self, file_object):
        """
        Download a file content

        :type file_object: typing.IO
        """

        def _download_inner():
            qry = create_download_file_query(self, file_object)
            self.context.add_query(qry)

        self.ensure_property("ServerRelativePath", _download_inner)
        return self

    def download_session(self, file_object, chunk_downloaded=None, chunk_size=1024 * 1024):
        """
        :type file_object: typing.IO
        :type chunk_downloaded: (int)->None or None
        :type chunk_size: int
        """

        def _download_as_stream():
            qry = ServiceOperationQuery(self, "$value")

            def _construct_download_request(request):
                """
                :type request: office365.runtime.http.request_options.RequestOptions
                """
                request.stream = True
                request.method = HttpMethod.Get

            self.context.before_execute(_construct_download_request)

            def _process_download_response(response):
                """
                :type response: requests.Response
                """
                response.raise_for_status()
                bytes_read = 0
                for chunk in response.iter_content(chunk_size=chunk_size):
                    bytes_read += len(chunk)
                    if callable(chunk_downloaded):
                        chunk_downloaded(bytes_read)
                    file_object.write(chunk)

            self.context.after_execute(_process_download_response)

            self.context.add_query(qry)

        self.ensure_property("ServerRelativeUrl", _download_as_stream)
        return self

    @property
    def checked_out_by_user(self):
        """Gets an object that represents the user who has checked out the file."""
        return self.properties.get('CheckedOutByUser',
                                   User(self.context, ResourcePath("CheckedOutByUser", self.resource_path)))

    @property
    def version_events(self):
        return self.properties.get("VersionEvents",
                                   BaseEntityCollection(self.context,
                                                        FileVersionEvent,
                                                        ResourcePath("VersionEvents", self.resource_path)))

    @property
    def information_rights_management_settings(self):
        """
        Returns the effective Information Rights Management (IRM) settings for the file.

        A file can be IRM-protected based on the IRM settings for the file itself, based on the IRM settings
        for the list which contains the file, or based on a rule.
        From greatest to least, IRM settings take precedence in the following order: rule, list, then file.
        """
        return self.properties.get('InformationRightsManagementSettings',
                                   InformationRightsManagementSettings(self.context,
                                                                       ResourcePath(
                                                                           "InformationRightsManagementSettings",
                                                                           self.resource_path)))

    @property
    def listItemAllFields(self):
        """Gets a value that specifies the list item fields values for the list item corresponding to the file."""
        return self.properties.get('ListItemAllFields',
                                   ListItem(self.context, ResourcePath("listItemAllFields", self.resource_path)))

    @property
    def versions(self):
        """Gets a value that returns a collection of file version objects that represent the versions of the file."""
        return self.properties.get('Versions',
                                   FileVersionCollection(self.context, ResourcePath("versions", self.resource_path)))

    @property
    def modified_by(self):
        """
        Gets a value that returns the user who last modified the file.

        :rtype: office365.sharepoint.directory.user.User
        """
        return self.properties.get("ModifiedBy", User(self.context, ResourcePath("ModifiedBy", self.resource_path)))

    @property
    def locked_by_user(self):
        """
        Gets a value that returns the user that owns the current lock on the file.

        :rtype: office365.sharepoint.directory.user.User
        """
        return self.properties.get("LockedByUser", User(self.context, ResourcePath("LockedByUser", self.resource_path)))

    @property
    def serverRelativeUrl(self):
        """Gets the relative URL of the file based on the URL for the server.

        :rtype: str or None
        """
        return self.properties.get("ServerRelativeUrl", None)

    @property
    def server_relative_path(self):
        """Gets the server-relative Path of the list folder.
        :rtype: SPResPath or None
        """
        return self.properties.get("ServerRelativePath", SPResPath())

    @property
    def length(self):
        """Gets the file size.

        :rtype: int or None
        """
        return int(self.properties.get("Length", -1))

    @property
    def exists(self):
        """Specifies whether the file exists.

        :rtype: bool or None
        """
        return self.properties.get("Exists", None)

    @property
    def name(self):
        """Specifies the file name including the extension.
            It MUST NOT be NULL. Its length MUST be equal to or less than 260.

        :rtype: str or None
        """
        return self.properties.get("Name", None)

    @property
    def list_id(self):
        """Gets the GUID that identifies the List containing the file.

        :rtype: str or None
        """
        return self.properties.get("ListId", None)

    @property
    def site_id(self):
        """Gets the GUID that identifies the site collection containing the file.

        :rtype: str or None
        """
        return self.properties.get("SiteId", None)

    @property
    def web_id(self):
        """Gets the GUID for the site containing the file.

        :rtype: str or None
        """
        return self.properties.get("WebId", None)

    @property
    def time_created(self):
        """Gets a value that specifies when the file was created.

        :rtype: str or None
        """
        return self.properties.get("TimeCreated", None)

    @property
    def time_last_modified(self):
        """Specifies when the file was last modified.

        :rtype: str or None
        """
        return self.properties.get("TimeLastModified", None)

    @property
    def minor_version(self):
        """
        Gets a value that specifies the minor version of the file.
        """
        return int(self.properties.get("MinorVersion", -1))

    @property
    def major_version(self):
        """
        Gets a value that specifies the major version of the file.

        :rtype: int or None
        """
        return int(self.properties.get("MajorVersion", -1))

    @property
    def unique_id(self):
        """
        Gets a value that specifies the a file unique identifier

        :rtype: str or None
        """
        return self.properties.get("UniqueId", None)

    @property
    def customized_page_status(self):
        """Specifies the customization status of the file.

        :rtype: int or None
        """
        return self.properties.get("CustomizedPageStatus", None)

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "CheckedOutByUser": self.checked_out_by_user,
                "VersionEvents": self.version_events,
                "InformationRightsManagementSettings": self.information_rights_management_settings,
                "LockedByUser": self.locked_by_user,
                "ModifiedBy": self.modified_by
            }
            default_value = property_mapping.get(name, None)
        return super(File, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super(File, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "ServerRelativeUrl":
                self._resource_path = ServiceOperationPath("GetFileByServerRelativeUrl", [value],
                                                           ResourcePath("Web"))
            elif name == "ServerRelativePath":
                self._resource_path = ServiceOperationPath("getFolderByServerRelativePath", [value],
                                                           ResourcePath("Web"))
            elif name == "UniqueId":
                self._resource_path = ServiceOperationPath("GetFileById", [value], ResourcePath("Web"))
        return self
