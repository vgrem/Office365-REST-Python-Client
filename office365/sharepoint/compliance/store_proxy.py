from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.compliance.tag import ComplianceTag


class SPPolicyStoreProxy(BaseEntity):

    @staticmethod
    def get_available_tags_for_site(context, site_url, return_type=None):
        """
        :param office365.sharepoint.client_context.ClientContext context: SharePoint client context
        :param str site_url:
        :param ClientResult return_type:
        """
        if return_type is None:
            return_type = ClientResult(context, ClientValueCollection(ComplianceTag))
        payload = {
            "siteUrl": site_url
        }
        qry = ServiceOperationQuery(SPPolicyStoreProxy(context), "GetAvailableTagsForSite", None, payload,
                                    None, return_type, True)
        context.add_query(qry)
        return return_type

    def get_dynamic_scope_binding_by_site_id(self, site_id):
        """
        :param str site_id:
        """
        return_type = ClientResult(self.context, StringCollection())
        payload = {
            "siteId": site_id
        }
        qry = ServiceOperationQuery(self, "GetDynamicScopeBindingBySiteId", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "SP.CompliancePolicy.SPPolicyStoreProxy"
