from office365.runtime.client_object import ClientObject
from office365.runtime.serviceOperationQuery import ServiceOperationQuery
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.portal.SPSiteCreationResponse import SPSiteCreationResponse


class SPSiteManager(ClientObject):

    def __init__(self, context):
        super(SPSiteManager, self).__init__(context, ResourcePath("SPSiteManager"), None)

    def create(self, request):
        """Create a modern site"""
        response = SPSiteCreationResponse()
        qry = ServiceOperationQuery(self, "Create", None, request, "request", response)
        self.context.add_query(qry)
        return response

    def delete(self, site_id):
        """Deletes a SharePoint site"""
        payload = {
            "siteId": site_id
        }
        qry = ServiceOperationQuery(self, "Delete", None, payload)
        self.context.add_query(qry)

    def get_status(self, url):
        """Get the status of a SharePoint site"""
        response = SPSiteCreationResponse()
        qry = ServiceOperationQuery(self, "Status", None, {'url': url}, None, response)
        self.context.add_query(qry)
        self.context.get_pending_request().beforeExecute += self._construct_status_request
        return response

    def _construct_status_request(self, request):
        query = self.context.get_pending_request().current_query
        request.method = HttpMethod.Get
        request.url += "?url='{0}'".format(query.parameter_type['url'])
        self.context.get_pending_request().beforeExecute -= self._construct_status_request
