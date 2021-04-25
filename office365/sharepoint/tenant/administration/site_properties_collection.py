from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.tenant.administration.site_properties import SiteProperties


class SitePropertiesCollection(BaseEntityCollection):
    """CSiteProperties resource collection"""
    def __init__(self, context, resource_path=None):
        super(SitePropertiesCollection, self).__init__(context, SiteProperties, resource_path)

    def get_by_id(self, site_id):
        site_props = SiteProperties(self.context)
        qry = ServiceOperationQuery(self, "GetById", [site_id], None, None, site_props)
        self.context.add_query(qry)
        return site_props

    def get_lock_state_by_id(self, site_id):
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "GetLockStateById", [site_id], None, None, result)
        self.context.add_query(qry)
        return result
