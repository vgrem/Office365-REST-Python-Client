import urllib

from office365.runtime.client_object import ClientObject
from office365.runtime.resource_path_entry import ResourcePathEntry
from office365.runtime.utilities.http_method import HttpMethod
from office365.runtime.utilities.request_options import RequestOptions
from office365.sharepoint.listitem import ListItem


class File(ClientObject):
    """Represents a file in a SharePoint Web site that can be a Web Part Page, an item in a document library,
    or a file in a folder."""

    @staticmethod
    def save_binary(ctx, server_relative_url, content):
        server_relative_url = urllib.quote(server_relative_url)
        url = "{0}web/getfilebyserverrelativeurl('{1}')/\$value".format(ctx.service_root_url, server_relative_url)
        request = RequestOptions(url)
        request.method = HttpMethod.Post
        request.set_header('X-HTTP-Method', 'PUT')
        request.data = content
        ctx.execute_query_direct(request)

    @staticmethod
    def open_binary(ctx, server_relative_url):
        server_relative_url = urllib.quote(server_relative_url)
        url = "{0}web/getfilebyserverrelativeurl('{1}')/\$value".format(ctx.service_root_url, server_relative_url)
        request = RequestOptions(url)
        request.method = HttpMethod.Get
        response = ctx.execute_query_direct(request)
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
                                     "GetFileByServerRelativeUrl('{0}')".format(self.properties["ServerRelativeUrl"]))
        elif self.is_property_available("UniqueId") and orig_path is None:
            path = ResourcePathEntry(self.context,
                                     ResourcePathEntry(self.context, None, "Web"),
                                     "GetFileById(guid'{0}')".format(self.properties["UniqueId"]))
            return path
        return orig_path
