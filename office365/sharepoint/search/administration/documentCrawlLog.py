from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.search.simpleDataTable import SimpleDataTable


class DocumentCrawlLog(BaseEntity):

    def __init__(self, site):
        super().__init__(site.context,
                         ResourcePath("Microsoft.SharePoint.Client.Search.Administration.DocumentCrawlLog"))

    def get_crawled_urls(self, getCountOnly=False):
        """
        Retrieves information about all the contents that were crawled.

        :type getCountOnly: bool"""
        result = SimpleDataTable()
        payload = {
            "getCountOnly": getCountOnly
        }
        qry = ServiceOperationQuery(self, "GetCrawledUrls", None, payload, None, result)
        self.context.add_query(qry)
        return result
