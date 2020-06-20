from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.queries.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.tenant.administration.siteProperties import SiteProperties


class SitePropertiesCollection(ClientObjectCollection):
    """CSiteProperties resource collection"""
    def __init__(self, context, resource_path=None):
        super(SitePropertiesCollection, self).__init__(context, SiteProperties, resource_path)

    def get_by_id(self, site_id):
        site_props = SiteProperties(self.context)
        qry = ServiceOperationQuery(self, "GetById", [site_id], None, None, site_props)
        self.context.add_query(qry)
        return site_props
