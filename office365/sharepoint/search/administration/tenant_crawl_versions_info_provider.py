from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class TenantCrawlVersionsInfoProvider(BaseEntity):
    """

    """

    def disable_crawl_versions(self, site_id):
        """
        :param str site_id:
        """
        return_type = ClientResult(self.context, bool())
        payload = {
            "siteId": site_id
        }
        qry = ServiceOperationQuery(self, "DisableCrawlVersions", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type


    def is_crawl_versions_enabled(self, site_id):
        """
        :param str site_id:
        """
        return_type = ClientResult(self.context, bool())
        payload = {
            "siteId": site_id
        }
        qry = ServiceOperationQuery(self, "IsCrawlVersionsEnabled", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Client.Search.Administration.TenantCrawlVersionsInfoProvider"
