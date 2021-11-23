from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.tenant.administration.hub_site_collection import HubSiteCollection


class SPHubSitesUtility(BaseEntity):
    """You can use the class to register sites as hub sites,
    associate existing sites with hub sites, and obtain or update information about hub sites.
    """

    def __init__(self, context):
        super(SPHubSitesUtility, self).__init__(context, ResourcePath("Microsoft.SharePoint.Portal.SPHubSitesUtility"))

    def get_hub_sites(self):
        """Gets information about all hub sites that the current user can access."""
        hub_sites = HubSiteCollection(self.context)
        qry = ServiceOperationQuery(self, "GetHubSites", None, None, None, hub_sites)
        self.context.add_query(qry)
        return hub_sites
