from office365.onedrive.list import List
from office365.runtime.client_object import ClientObject
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.webs.web import Web


class RemoteWeb(ClientObject):
    """Specifies a remote web that might be on a different domain."""

    def get_list_by_server_relative_url(self, serverRelativeUrl):
        target_list = List(self.context)
        qry = ServiceOperationQuery(self, "GetListByServerRelativeUrl", [serverRelativeUrl], None, None, target_list)
        self.context.add_query(qry)
        return target_list

    @staticmethod
    def create(context, requestUrl):
        remote_web = RemoteWeb(context)
        qry = ServiceOperationQuery(context, None, [requestUrl], None, None, remote_web)
        qry.static = True
        context.add_query(qry)
        return remote_web

    @property
    def web(self):
        """Gets the SPWeb."""
        return self.properties.get('Web', Web(self.context, ResourcePath("Web", self.resource_path)))
