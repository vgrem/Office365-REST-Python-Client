from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.search.simpleDataTable import SimpleDataTable


class DocumentCrawlLog(BaseEntity):
    """This object contains methods that can be used by the protocol client to retrieve information
    about items that were crawled."""

    def __init__(self, site):
        super(DocumentCrawlLog, self).__init__(site.context,
                                               ResourcePath(
                                                   "Microsoft.SharePoint.Client.Search.Administration.DocumentCrawlLog"))

    def get_crawled_urls(self, get_count_only=False):
        """
        Retrieves information about all the contents that were crawled.

        :type get_count_only: bool
        """
        result = SimpleDataTable()
        payload = {
            "getCountOnly": get_count_only
        }
        qry = ServiceOperationQuery(self, "GetCrawledUrls", None, payload, None, result)
        self.context.add_query(qry)
        return result
