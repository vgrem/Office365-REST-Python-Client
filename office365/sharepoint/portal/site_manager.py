from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.portal.site_creation_response import SPSiteCreationResponse
from office365.sharepoint.teams.site_owner_response import GetTeamChannelSiteOwnerResponse


class SPSiteManager(BaseEntity):
    """Provides REST methods for creating and managing SharePoint sites."""

    def __init__(self, context, resource_path=None):
        if resource_path is None:
            resource_path = ResourcePath("SPSiteManager")
        super(SPSiteManager, self).__init__(context, resource_path)

    def create(self, request):
        """
        When executing this method server MUST create a SharePoint site according to the parameters passed in the
        SPSiteCreationRequest and return the information about the site it created in the format of a
        SPSiteCreationResponse.

        :param SPSiteCreationRequest request: The entity data object for sites creation request, which include
            information for the site to be created.
        """
        result = ClientResult(self.context, SPSiteCreationResponse())
        qry = ServiceOperationQuery(self, "Create", None, request, "request", result)
        self.context.add_query(qry)
        return result

    def delete(self, site_id):
        """When executing this method server MUST put the SharePoint site into recycle bin according to
        the parameter passed in the siteId, if the SharePoint site of giving siteId exists and the site has
        no attached AD group.

        :param str site_id: The GUID to uniquely identify a SharePoint site.
        """
        payload = {
            "siteId": site_id
        }
        qry = ServiceOperationQuery(self, "Delete", None, payload)
        self.context.add_query(qry)
        return self

    def get_status(self, site_url):
        """When executing this method server SHOULD return a SharePoint site status in the format
        of a SPSiteCreationRespnse according to the parameter passed in the url.

        :param str site_url: URL of the site to return status for
        """
        response = ClientResult(self.context, SPSiteCreationResponse())
        qry = ServiceOperationQuery(self, "Status", None, {'url': site_url}, None, response)
        self.context.add_query(qry)

        def _construct_status_request(request):
            request.method = HttpMethod.Get
            request.url += "?url='{0}'".format(site_url)

        self.context.before_execute(_construct_status_request)
        return response

    def get_site_url(self, site_id):
        response = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "SiteUrl", None, {'siteId': site_id}, None, response)
        self.context.add_query(qry)
        return response

    def get_team_channel_site_owner(self, site_id):
        response = ClientResult(self.context, GetTeamChannelSiteOwnerResponse())
        qry = ServiceOperationQuery(self, "GetTeamChannelSiteOwner", None, {'siteId': site_id}, None, response)
        self.context.add_query(qry)
        return response
