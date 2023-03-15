from office365.entity import Entity
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.search.entity_type import EntityType
from office365.search.query import SearchQuery
from office365.search.request import SearchRequest
from office365.search.response import SearchResponse


class SearchEntity(Entity):
    """
    A top level object representing the Microsoft Search API endpoint. It does not behave as any other resource
    in Graph, but serves as an anchor to the query action.
    """

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

    def query_messages(self, query_string):
        """Searches Outlook messages.
        Alias to query method

        :param str query_string: Contains the query terms.
        """
        return self.query(query_string, entity_types=[EntityType.message])

    def query_events(self, query_string):
        """Searches Outlook calendar events. Alias to query method

        :param str query_string: Contains the query terms.
        """
        return self.query(query_string, entity_types=[EntityType.event])

    def query_drive_items(self, query_string):
        """Searches OneDrive items.
        Alias to query method

        :param str query_string: Contains the query terms.
        """
        return self.query(query_string, entity_types=[EntityType.driveItem])

