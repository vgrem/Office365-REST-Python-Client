from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.publishing.site_page import SitePage


class SitePageCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        """Specifies a collection of site pages."""
        super(SitePageCollection, self).__init__(context, SitePage, resource_path)

    def is_site_page(self, url):
        """
        :type url: str
        """
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "IsSitePage", [url], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_page_column_state(self, url):
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "GetPageColumnState", [url], None, None, return_type)
        self.context.add_query(qry)
        return return_type
