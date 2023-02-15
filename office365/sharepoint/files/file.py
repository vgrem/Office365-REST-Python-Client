from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.update_entity import UpdateEntityQuery
from office365.sharepoint.activities.capabilities import ActivityCapabilities
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.files.version_event import FileVersionEvent
from office365.sharepoint.internal.queries.download_file import create_download_file_query
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.permissions.irm.effective_settings import EffectiveInformationRightsManagementSettings
from office365.sharepoint.permissions.irm.settings import InformationRightsManagementSettings
from office365.sharepoint.principal.users.user import User
from office365.sharepoint.files.version_collection import FileVersionCollection
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.utilities.wopi_frame_action import SPWOPIFrameAction
from office365.sharepoint.webparts.limited_manager import LimitedWebPartManager
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath
from office365.sharepoint.webparts.personalization_scope import PersonalizationScope


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

    def get_sharing_information(self):
        """Gets the sharing information for a file."""
        return self.listItemAllFields.get_sharing_information()

    def get_wopi_frame_url(self, action=SPWOPIFrameAction.View):
        """
        Returns the full URL to the SharePoint frame page that will initiate the specified WOPI frame action with the
        file's associated WOPI application. If there is no associated WOPI application or associated action,
        the return value is an empty string.

        :param str action: The full URL to the WOPI frame.
        """
        return_type = ClientResult(self.context, str())
        params = {
            "action": action
        }
        qry = ServiceOperationQuery(self, "GetWOPIFrameUrl", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def share_link(self, link_kind, expiration=None):
        """Creates a tokenized sharing link for a file based on the specified parameters and optionally
        sends an email to the people that are listed in the specified parameters.

        :param int link_kind: The kind of the tokenized sharing link to be created/updated or retrieved.
        :param datetime or None expiration: A date/time string for which the format conforms to the ISO 8601:2004(E)
            complete representation for calendar date and time of day and which represents the time and date of expiry
            for the tokenized sharing link. Both the minutes and hour value MUST be specified for the difference
            between the local and UTC time. Midnight is represented as 00:00:00. A null value indicates no expiry.
            This value is only applicable to tokenized sharing links that are anonymous access links.
        """
        return self.listItemAllFields.share_link(link_kind, expiration)

    def unshare_link(self, link_kind, share_id=None):
        """
        Removes the specified tokenized sharing link of the file.

        :param int link_kind: This optional value specifies the globally unique identifier (GUID) of the tokenized
            sharing link that is intended to be removed.
        :param str or None share_id: The kind of tokenized sharing link that is intended to be removed.
        """
        return self.listItemAllFields.unshare_link(link_kind, share_id)

    def get_image_preview_uri(self, width, height, client_type=None):
        """
        Returns the uri where the thumbnail with the closest size to the desired can be found.
        The actual resolution of the thumbnail might not be the same as the desired values.


        :param int width: The desired width of the resolution.
        :param int height: The desired height of the resolution.
        :param str client_type: The client type. Used for logging.
        """
        result = ClientResult(self.context, str())
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
        Returns the url where the thumbnail with the closest size to the desired can be found.
        The actual resolution of the thumbnail might not be the same as the desired values.

        :param int width: The desired width of the resolution.
        :param int height: The desired height of the resolution.
        :param str client_type: The client type. Used for logging.
        """
        return_type = ClientResult(self.context, str())
        payload = {
            "width": width,
            "height": height,
            "clientType": client_type
        }
        qry = ServiceOperationQuery(self, "GetImagePreviewUrl", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def recycle(self):
        """Moves the file to the Recycle Bin and returns the identifier of the new Recycle Bin item."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "Recycle", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def approve(self, comment):
        """
        Approves the file submitted for content approval with the specified comment.

        :param str comment: A string containing the comment.
        """
        qry = ServiceOperationQuery(self, "Approve", {"comment": comment})
        self.context.add_query(qry)
        return self

    def deny(self, comment):
        """Denies approval for a file that was submitted for content approval.

        :param str comment: A string containing the comment.
        """
        qry = ServiceOperationQuery(self, "Deny", {"comment": comment})
        self.context.add_query(qry)
        return self

    def copyto(self, new_relative_url, overwrite):
        """Copies the file to the destination URL.

        :param str new_relative_url: Specifies the destination URL.
        :param bool overwrite: Specifies whether a file with the same name is overwritten.
        """
        params = {
            "strNewUrl": new_relative_url,
            "boverwrite": overwrite
        }
        qry = ServiceOperationQuery(self, "CopyTo", params)
        self.context.add_query(qry)
        return self

    def copyto_using_path(self, decoded_url, overwrite):
        """
        Copies the file to the destination path. Server MUST overwrite an existing file of the same name
        if bOverwrite is true.
        Exceptions:
           Error Code, Error Type Name, Condition
           2147024729, Microsoft.SharePoint.SPFileLockException, The file is not locked
           2147018894, Microsoft.SharePoint.SPFileLockException, There is a shared lock on the file
           2147018887, Microsoft.SharePoint.SPFileLockException, There is an exclusive lock on the file

        :param str decoded_url: Specifies the destination path.
        :param bool overwrite: Specifies whether a file with the same name is overwritten.
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

        :param str new_relative_url: Specifies the destination URL.
        :param int flag: Specifies the kind of move operation.
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

        :param str comment: Specifies the comment.
        """
        qry = ServiceOperationQuery(self, "Publish", {"comment": comment})
        self.context.add_query(qry)

    def unpublish(self, comment):
        """Removes the file from content approval or unpublish a major version.

        :type comment: str
        """
        qry = ServiceOperationQuery(self, "unpublish", {"comment": comment})
        self.context.add_query(qry)
        return self

    def checkout(self):
        """Checks out the file from a document library based on the check-out type."""
        qry = ServiceOperationQuery(self, "checkout")
        self.context.add_query(qry)
        return self

    def checkin(self, comment, checkin_type):
        """
        Checks the file in to a document library based on the check-in type.

        :param comment: comment to the new version of the file
        :param checkin_type: 0 (minor), or 1 (major) or 2 (overwrite)
            For more information on checkin types, please see
            https://docs.microsoft.com/en-us/previous-versions/office/sharepoint-csom/ee542953(v%3Doffice.15)
        :param int checkin_type: Specifies the type of check-in.
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
        qry = ServiceOperationQuery(self, "UndoCheckout")
        self.context.add_query(qry)
        return self

    def get_limited_webpart_manager(self, scope=PersonalizationScope.User):
        """Specifies the control set used to access, modify, or add Web Parts associated with this Web Part Page and
        view.

        :param int scope:  Specifies the personalization scope value that depicts how Web Parts are viewed on the
            Web Part Page.
        """
        return LimitedWebPartManager(self.context,
                                     ServiceOperationPath("GetLimitedWebPartManager", [scope], self.resource_path))

    def open_binary_stream(self):
        """Opens the file as a stream."""
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(self, "OpenBinaryStream", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def save_binary_stream(self, stream):
        """Saves the file in binary format.

        :param str or bytes stream: A stream containing the contents of the specified file.
        """
        qry = ServiceOperationQuery(self, "SaveBinaryStream", None, {"file": stream})
        self.context.add_query(qry)
        return self

    def get_upload_status(self, upload_id):
        """Gets the status of a chunk upload session.

        :param str upload_id:  The upload session ID.
        """
        payload = {
            "uploadId": upload_id,
        }
        return_type = File(self.context)
        qry = ServiceOperationQuery(self, "GetUploadStatus", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def upload_with_checksum(self, upload_id, checksum, stream):
        """
        :param str upload_id: The upload session ID.
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
        """
        Aborts the chunk upload session without saving the uploaded data. If StartUpload (section 3.2.5.64.2.1.22)
        created the file, the file will be deleted.

        :param str upload_id:  The upload session ID.
        """
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
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self,
                                    "startUpload",
                                    {
                                        "uploadID": upload_id
                                    },
                                    content,
                                    None,
                                    return_type
                                    )
        self.context.add_query(qry)
        return return_type

    def continue_upload(self, upload_id, file_offset, content):
        """
        Continues the chunk upload session with an additional fragment. The current file content is not changed.

        :param str upload_id: Upload session id
        :param int file_offset: File offset
        :param bytes content: File content
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self,
                                    "continueUpload",
                                    {
                                        "uploadID": upload_id,
                                        "fileOffset": file_offset,
                                    },
                                    content,
                                    None,
                                    return_type
                                    )
        self.context.add_query(qry)
        return return_type

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
    def save_binary(context, server_relative_url, content):
        """Uploads a file

        :type context: office365.sharepoint.client_context.ClientContext
        :type server_relative_url: str
        :type content: str
        """
        url = r"{0}/web/getFileByServerRelativePath(DecodedUrl='{1}')/\$value".format(context.service_root_url(),
                                                                                      server_relative_url)
        request = RequestOptions(url)
        request.method = HttpMethod.Post
        request.set_header('X-HTTP-Method', 'PUT')
        request.data = content
        response = context.pending_request().execute_request_direct(request)
        return response

    @staticmethod
    def open_binary(context, server_relative_url):
        """
        Returns the file object located at the specified server-relative URL.

        :type context: office365.sharepoint.client_context.ClientContext
        :type server_relative_url: str
        :return Response
        """
        url = r"{0}/web/getFileByServerRelativePath(DecodedUrl='{1}')/\$value".format(context.service_root_url(),
                                                                                      server_relative_url)
        request = RequestOptions(url)
        request.method = HttpMethod.Get
        response = context.pending_request().execute_request_direct(request)
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

    def download_session(self, file_object, chunk_downloaded=None, chunk_size=1024 * 1024, use_path=True):
        """
        :type file_object: typing.IO
        :type chunk_downloaded: (int)->None or None
        :type chunk_size: int
        :param bool use_path: Use Path instead of Url for addressing files
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

        if use_path:
            self.ensure_property("ServerRelativePath", _download_as_stream)
        else:
            self.ensure_property("ServerRelativeUrl", _download_as_stream)
        return self

    def rename(self, new_file_name):
        """
        Rename a file

        :param str new_file_name: A new file name
        """
        item = self.listItemAllFields
        item.set_property('FileLeafRef', new_file_name)
        qry = UpdateEntityQuery(item)
        self.context.add_query(qry)
        return self

    @property
    def activity_capabilities(self):
        return self.properties.get("ActivityCapabilities", ActivityCapabilities())

    @property
    def author(self):
        """Specifies the user who added the file."""
        return self.properties.get('Author',
                                   User(self.context, ResourcePath("Author", self.resource_path)))

    @property
    def checked_out_by_user(self):
        """Gets an object that represents the user who has checked out the file."""
        return self.properties.get('CheckedOutByUser',
                                   User(self.context, ResourcePath("CheckedOutByUser", self.resource_path)))

    @property
    def version_events(self):
        """Gets the history of events on this version object."""
        return self.properties.get("VersionEvents",
                                   BaseEntityCollection(self.context,
                                                        FileVersionEvent,
                                                        ResourcePath("VersionEvents", self.resource_path)))

    @property
    def effective_information_rights_management_settings(self):
        """
        Returns the effective Information Rights Management (IRM) settings for the file.

        A file can be IRM-protected based on the IRM settings for the file itself, based on the IRM settings for the
        list which contains the file, or based on a rule. From greatest to least, IRM settings take precedence in the
        following order: rule, list, then file.
        """
        path = ResourcePath("EffectiveInformationRightsManagementSettings", self.resource_path)
        return self.properties.get('EffectiveInformationRightsManagementSettings',
                                   EffectiveInformationRightsManagementSettings(self.context, path))

    @property
    def information_rights_management_settings(self):
        """
        Returns the Information Rights Management (IRM) settings for the file.
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
        """
        return self.properties.get("ModifiedBy", User(self.context, ResourcePath("ModifiedBy", self.resource_path)))

    @property
    def locked_by_user(self):
        """
        Gets a value that returns the user that owns the current lock on the file.
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
                "EffectiveInformationRightsManagementSettings": self.effective_information_rights_management_settings,
                "InformationRightsManagementSettings": self.information_rights_management_settings,
                "LockedByUser": self.locked_by_user,
                "ModifiedBy": self.modified_by
            }
            default_value = property_mapping.get(name, None)
        return super(File, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super(File, self).set_property(name, value, persist_changes)

        # prioritize using UniqueId
        if name == "UniqueId":
            self._resource_path = self.context.web.get_file_by_id(value).resource_path

        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "ServerRelativeUrl":
                self._resource_path = self.context.web.get_file_by_server_relative_url(value).resource_path
            elif name == "ServerRelativePath":
                self._resource_path = self.context.web.get_file_by_server_relative_path(value).resource_path
        return self
