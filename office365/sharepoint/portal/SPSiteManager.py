from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.portal.SPSiteCreationResponse import SPSiteCreationResponse


class SPSiteManager(BaseEntity):

    def __init__(self, context):
        super(SPSiteManager, self).__init__(context, ResourcePath("SPSiteManager"))

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

    def get_status(self, site_url):
        """Get the status of a SharePoint site"""
        response = SPSiteCreationResponse()
        qry = ServiceOperationQuery(self, "Status", None, {'url': site_url}, None, response)
        self.context.add_query(qry)

        def _construct_status_request(request):
            request.method = HttpMethod.Get
            request.url += "?url='{0}'".format(site_url)

        self.context.before_execute(_construct_status_request)
        return response
