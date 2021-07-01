from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.tenant.administration.hub_site_collection import HubSiteCollection


class SPHubSitesUtility(BaseEntity):

    def __init__(self, context):
        super(SPHubSitesUtility, self).__init__(context, ResourcePath("Microsoft.SharePoint.Portal.SPHubSitesUtility"))

    def get_hub_sites(self):
        hub_sites = HubSiteCollection(self.context)
        qry = ServiceOperationQuery(self, "GetHubSites", None, None, None, hub_sites)
        self.context.add_query(qry)
        return hub_sites
