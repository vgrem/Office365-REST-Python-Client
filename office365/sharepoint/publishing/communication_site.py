from office365.runtime.client_result import ClientResult
from office365.runtime.client_value import ClientValue
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class CommunicationSiteCreationRequest(ClientValue):
    pass


class CommunicationSiteCreationResponse(ClientValue):
    pass


class CommunicationSite(BaseEntity):
    """Represents a Communication Site."""

    def create(self, request):
        """
        :type request: CommunicationSiteCreationRequest
        """
        result = ClientResult(self.context, CommunicationSiteCreationResponse())
        qry = ServiceOperationQuery(self, "Create", None, request, "request", result)
        self.context.add_query(qry)
        return result

    @property
    def entity_type_name(self):
        return "SP.Publishing.CommunicationSite"
