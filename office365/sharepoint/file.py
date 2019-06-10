from office365.runtime.action_type import ActionType
from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import ClientQuery
from office365.runtime.odata.odata_path_parser import ODataPathParser
from office365.runtime.resource_path_entry import ResourcePathEntry
from office365.runtime.utilities.http_method import HttpMethod
from office365.runtime.utilities.request_options import RequestOptions
from office365.sharepoint.listitem import ListItem


class AbstractFile(ClientObject):
    def read(self, response_object=False):
        """Immediately read content of file"""
        if not self.is_property_available("ServerRelativeUrl"):
            raise ValueError
        response = File.open_binary(self.context, self.properties["ServerRelativeUrl"])
        if not response_object:
            return response.content
        return response

    def write(self, content):
        """Immediately writes content of file"""
        if not self.is_property_available("ServerRelativeUrl"):
            raise ValueError
        response = File.save_binary(self.context, self.properties["ServerRelativeUrl"], content)
        return response

    def delete_object(self):
        """Deletes the file."""
        qry = ClientQuery.delete_entry_query(self)
        self.context.add_query(qry)


class File(AbstractFile):
    """Represents a file in a SharePoint Web site that can be a Web Part Page, an item in a document library,
    or a file in a folder."""

    def copyto(self, new_relative_url, overwrite):
        qry = ClientQuery.service_operation_query(self,
                                                  ActionType.PostMethod,
                                                  "moveto",
                                                  {
                                                      "newurl": new_relative_url,
                                                      "boverwrite": overwrite
                                                  },
                                                  None)
        self.context.add_query(qry)

    def moveto(self, new_relative_url, flag):
        qry = ClientQuery.service_operation_query(self,
                                                  ActionType.PostMethod,
                                                  "moveto",
                                                  {
                                                      "newurl": new_relative_url,
                                                      "flags": flag
                                                  },
                                                  None)
        self.context.add_query(qry)

    @staticmethod
    def save_binary(ctx, server_relative_url, content):
        try:
            from urllib import quote  # Python 2.X
        except ImportError:
            from urllib.parse import quote  # Python 3+
        server_relative_url = quote(server_relative_url)
        url = "{0}web/getfilebyserverrelativeurl('{1}')/\$value".format(ctx.service_root_url, server_relative_url)
        request = RequestOptions(url)
        request.method = HttpMethod.Post
        request.set_header('X-HTTP-Method', 'PUT')
        request.data = content
        response = ctx.execute_request_direct(request)
        return response

    @staticmethod
    def open_binary(ctx, server_relative_url):
        try:
            from urllib import quote  # Python 2.X
        except ImportError:
            from urllib.parse import quote  # Python 3+
        server_relative_url = quote(server_relative_url)
        url = "{0}web/getfilebyserverrelativeurl('{1}')/\$value".format(ctx.service_root_url, server_relative_url)
        request = RequestOptions(url)
        request.method = HttpMethod.Get
        response = ctx.execute_request_direct(request)
        return response

    @property
    def listitem_allfields(self):
        """Gets a value that specifies the list item field values for the list item corresponding to the file."""
        if self.is_property_available('ListItemAllFields'):
            return self.properties['ListItemAllFields']
        else:
            return ListItem(self.context, ResourcePathEntry(self.context, self.resource_path, "listItemAllFields"))

    @property
    def resource_path(self):
        orig_path = ClientObject.resource_path.fget(self)
        if self.is_property_available("ServerRelativeUrl") and orig_path is None:
            return ResourcePathEntry(self.context,
                                     self.context.web.resource_path,
                                     ODataPathParser.from_method("GetFileByServerRelativeUrl",
                                                                 [self.properties["ServerRelativeUrl"]]))
        elif self.is_property_available("UniqueId") and orig_path is None:
            path = ResourcePathEntry(self.context,
                                     ResourcePathEntry(self.context, None, "Web"),
                                     ODataPathParser.from_method("GetFileById",
                                                                 [{'guid': self.properties["UniqueId"]}]))
            return path
        return orig_path
