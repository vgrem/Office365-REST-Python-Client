from office365.entity import Entity
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.search.search_query import SearchQuery
from office365.search.search_request import SearchRequest
from office365.search.search_response import SearchResponse


class SearchEntity(Entity):

    def query(self, query_string, entity_types=None):
        """
        Runs the query specified in the request body. Search results are provided in the response.

        :param str query_string: Contains the query terms.
        :param list[str] entity_types: One or more types of resources expected in the response.
            Possible values are: list, site, listItem, message, event, drive, driveItem, externalItem.
        """
        search_request = SearchRequest(query=SearchQuery(query_string), entity_types=entity_types)
        payload = {
            "requests": ClientValueCollection(SearchRequest, [search_request])
        }
        return_type = ClientResult(self.context, ClientValueCollection(SearchResponse))
        qry = ServiceOperationQuery(self, "query", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

