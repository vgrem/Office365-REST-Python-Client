from functools import partial
from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import DeleteEntityQuery
from office365.runtime.client_result import ClientResult
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.fileVersionCollection import FileVersionCollection
from office365.sharepoint.listitem import ListItem
from office365.sharepoint.webparts.limited_webpart_manager import LimitedWebPartManager


class DownloadFileQuery(ServiceOperationQuery):

    def __init__(self, web, file_url, file_object):
        self.file_object = file_object
        web.context.get_pending_request().beforeExecute += self._construct_download_query
        web.context.get_pending_request().afterExecute += self._process_response
        super(DownloadFileQuery, self).__init__(web, r"getFileByServerRelativeUrl('{0}')/\$value".format(file_url))

    def _construct_download_query(self, request):
        self.binding_type.context.get_pending_request().beforeExecute -= self._construct_download_query
        request.method = HttpMethod.Get

    def _process_response(self, response):
        self.binding_type.context.get_pending_request().afterExecute -= self._process_response
        self.file_object.write(response.content)


class AbstractFile(ClientObject):
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

    def delete_object(self):
        """Deletes the file."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)


class File(AbstractFile):
    """Represents a file in a SharePoint Web site that can be a Web Part Page, an item in a document library,
    or a file in a folder."""

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

    def copyto(self, new_relative_url, overwrite):
        """Copies the file to the destination URL.

        :type new_relative_url: str
        :type overwrite: bool
        """
        qry = ServiceOperationQuery(self,
                                    "copyto",
                                    {
                                        "strNewUrl": new_relative_url,
                                        "boverwrite": overwrite
                                    },
                                    None)
        self.context.add_query(qry)

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

    def checkout(self):
        """Checks out the file from a document library based on the check-out type."""
        qry = ServiceOperationQuery(self,
                                    "checkout",
                                    )
        self.context.add_query(qry)

    def checkin(self, comment, checkin_type):
        """Checks the file in to a document library based on the check-in type."""
        qry = ServiceOperationQuery(self,
                                    "checkin",
                                    {
                                        "comment": comment,
                                        "checkInType": checkin_type
                                    }
                                    )
        self.context.add_query(qry)

    def undocheckout(self):
        """Reverts an existing checkout for the file."""
        qry = ServiceOperationQuery(self,
                                    "undocheckout"
                                    )
        self.context.add_query(qry)

    def recycle(self):
        """Moves the file to the Recycle Bin and returns the identifier of the new Recycle Bin item."""
        qry = ServiceOperationQuery(self,
                                    "recycle"
                                    )
        self.context.add_query(qry)

    def get_limited_webpart_manager(self, scope):
        """Specifies the control set used to access, modify, or add Web Parts associated with this Web Part Page and
        view. """
        return LimitedWebPartManager(self.context,
                                     ResourcePathServiceOperation(
                                         "getlimitedwebpartmanager",
                                         [scope],
                                         self.resource_path
                                     ))

    def start_upload(self, upload_id, content):
        """Starts a new chunk upload session and uploads the first fragment."""
        result = ClientResult(None)
        qry = ServiceOperationQuery(self,
                                    "startupload",
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
        """Continues the chunk upload session with an additional fragment. The current file content is not changed."""
        result = ClientResult(None)
        qry = ServiceOperationQuery(self,
                                    "continueupload",
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
        completes. """
        qry = ServiceOperationQuery(self,
                                    "finishupload",
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
        url = r"{0}web/getfilebyserverrelativeurl('{1}')/\$value".format(
            ctx.service_root_url, server_relative_url)
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
        """
        url = r"{0}web/getfilebyserverrelativeurl('{1}')/\$value".format(ctx.service_root_url, server_relative_url)
        request = RequestOptions(url)
        request.method = HttpMethod.Get
        response = ctx.execute_request_direct(request)
        return response

    def download(self, file_object):
        """Download a file content"""
        self.ensure_property("ServerRelativeUrl", partial(self._download_inner, file_object))

    def _download_inner(self, file_object, target_file):
        file_url = target_file.properties['ServerRelativeUrl']
        qry = DownloadFileQuery(self.context.web, file_url, file_object)
        self.context.add_query(qry)

    @property
    def listItemAllFields(self):
        """Gets a value that specifies the list item field values for the list item corresponding to the file."""
        if self.is_property_available('ListItemAllFields'):
            return self.properties['ListItemAllFields']
        else:
            return ListItem(self.context, ResourcePath("listItemAllFields", self.resource_path))

    @property
    def versions(self):
        """Gets a value that returns a collection of file version objects that represent the versions of the file."""
        if self.is_property_available('Versions'):
            return self.properties['Versions']
        else:
            return FileVersionCollection(self.context, ResourcePath("versions", self.resource_path))

    @property
    def serverRelativeUrl(self):
        """Gets the relative URL of the file based on the URL for the server."""
        if self.is_property_available('ServerRelativeUrl'):
            return self.properties["ServerRelativeUrl"]
        else:
            return None

    def set_property(self, name, value, persist_changes=True):
        super(File, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "ServerRelativeUrl":
                self._resource_path = ResourcePathServiceOperation(
                    "GetFileByServerRelativeUrl",
                    [value],
                    ResourcePath("Web"))
            elif name == "UniqueId":
                self._resource_path = ResourcePathServiceOperation(
                    "GetFileById",
                    [value],
                    ResourcePath("Web"))
