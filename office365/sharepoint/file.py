from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import DeleteEntityQuery, ServiceOperationQuery
from office365.runtime.client_result import ClientResult
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.sharepoint.listitem import ListItem
from office365.sharepoint.webparts.limited_webpart_manager import LimitedWebPartManager


class AbstractFile(ClientObject):
    def read(self, response_object=False):
        """Immediately read content of file"""
        if not self.is_property_available("ServerRelativeUrl"):
            raise ValueError
        response = File.open_binary(
            self.context, self.properties["ServerRelativeUrl"])
        if not response_object:
            return response.content
        return response

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
        """Approves the file submitted for content approval with the specified comment."""
        qry = ServiceOperationQuery(self,
                                    "approve",
                                    {
                                        "comment": comment
                                    })
        self.context.add_query(qry)

    def deny(self, comment):
        """Denies approval for a file that was submitted for content approval."""
        qry = ServiceOperationQuery(self,
                                    "deny",
                                    {
                                        "comment": comment
                                    })
        self.context.add_query(qry)

    def copyto(self, new_relative_url, overwrite):
        """Copies the file to the destination URL."""
        qry = ServiceOperationQuery(self,
                                    "copyto",
                                    {
                                        "strNewUrl": new_relative_url,
                                        "boverwrite": overwrite
                                    },
                                    None)
        self.context.add_query(qry)

    def moveto(self, new_relative_url, flag):
        """Moves the file to the specified destination URL."""
        qry = ServiceOperationQuery(self,
                                    "moveto",
                                    {
                                        "newurl": new_relative_url,
                                        "flags": flag
                                    },
                                    None)
        self.context.add_query(qry)

    def publish(self, comment):
        """Submits the file for content approval with the specified comment."""
        qry = ServiceOperationQuery(self,
                                    "publish",
                                    {
                                        "comment": comment,
                                    }
                                    )
        self.context.add_query(qry)

    def unpublish(self, comment):
        """Removes the file from content approval or unpublish a major version."""
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
                                         self.resourcePath
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
        """Uploads a file"""
        url = r"{0}web/getfilebyserverrelativeurl('{1}')/\$value".format(
            ctx.serviceRootUrl, server_relative_url)
        request = RequestOptions(url)
        request.method = HttpMethod.Post
        request.set_header('X-HTTP-Method', 'PUT')
        request.data = content
        response = ctx.execute_request_direct(request)
        return response

    @staticmethod
    def open_binary(ctx, server_relative_url):
        url = r"{0}web/getfilebyserverrelativeurl('{1}')/\$value".format(ctx.serviceRootUrl, server_relative_url)
        request = RequestOptions(url)
        request.method = HttpMethod.Get
        response = ctx.execute_request_direct(request)
        return response

    @property
    def listItemAllFields(self):
        """Gets a value that specifies the list item field values for the list item corresponding to the file."""
        if self.is_property_available('ListItemAllFields'):
            return self.properties['ListItemAllFields']
        else:
            return ListItem(self.context, ResourcePath("listItemAllFields", self.resourcePath))

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

