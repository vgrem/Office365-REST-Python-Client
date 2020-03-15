from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import ServiceOperationQuery
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.portal.SPSiteCreationResponse import SPSiteCreationResponse


def _construct_status_request(request, query):
    request.method = HttpMethod.Get
    request.url += "?url='{0}'".format(query.parameters['url'])


class SPSiteManager(ClientObject):

    def __init__(self, context):
        super(SPSiteManager, self).__init__(context, ResourcePath("SPSiteManager"), None)

    def create(self, request):
        """Create a modern site"""
        response = SPSiteCreationResponse()
        qry = ServiceOperationQuery(self, "Create", None, request)
        self.context.add_query(qry, response)
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
        qry = ServiceOperationQuery(self, "Status", None, {'url': url})
        self.context.add_query(qry, response)
        self.context.pending_request.before_execute_request(_construct_status_request)
        return response
