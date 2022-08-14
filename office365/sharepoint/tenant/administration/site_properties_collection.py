from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.tenant.administration.site_properties import SiteProperties


class SitePropertiesCollection(BaseEntityCollection):
    """SiteProperties resource collection"""
    def __init__(self, context, resource_path=None):
        super(SitePropertiesCollection, self).__init__(context, SiteProperties, resource_path)

    def get_by_id(self, site_id):
        """
        :param str site_id: Site identifier
        """
        return_type = SiteProperties(self.context)
        qry = ServiceOperationQuery(self, "GetById", [site_id], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_lock_state_by_id(self, site_id):
        """
        :param str site_id: Site identifier
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "GetLockStateById", [site_id], None, None, result)
        self.context.add_query(qry)
        return result

    def check_site_is_archived_by_id(self, site_id):
        """
        :param str site_id: Site identifier
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "CheckSiteIsArchivedById", [site_id], None, None, result)
        self.context.add_query(qry)
        return result
