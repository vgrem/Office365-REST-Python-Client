from office365.runtime.queries.service_operation_query import ServiceOperationQuery


class SearchQuery(ServiceOperationQuery):
    def __init__(self, entity_type, query_text, return_type):
        super(SearchQuery, self).__init__(entity_type, "search", {"q": query_text}, None, None, return_type)
