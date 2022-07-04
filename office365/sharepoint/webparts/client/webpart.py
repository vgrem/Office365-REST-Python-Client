from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class ClientWebPart(BaseEntity):
    """Representation of a ClientWebPart. It provides with ClientWebPart metadata and methods to render it."""

    def render(self, properties=None):
        """
        :param dict properties:
        """
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "Render", None, properties, None, return_type)
        self.context.add_query(qry)
        return return_type
