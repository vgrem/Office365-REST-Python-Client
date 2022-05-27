from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.search.query.configuration import QueryConfiguration


class SearchSetting(BaseEntity):
    """This object provides the REST operations defined under search settings."""

    def get_query_configuration(self, call_local_search_farms_only=True):
        """
        This REST operation gets the query configuration. See section 3.1.5.18.2.1.6.

        :param bool call_local_search_farms_only: This is a flag that indicates to only call the local search farm.
        """
        result = ClientResult(self.context, QueryConfiguration())
        payload = {
            "callLocalSearchFarmsOnly": call_local_search_farms_only
        }
        qry = ServiceOperationQuery(self, "getqueryconfiguration", None, payload, None, result)
        self.context.add_query(qry)
        return result
