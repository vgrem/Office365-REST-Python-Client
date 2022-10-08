from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.translation.resource_entry import SPResourceEntry


class UserResource(BaseEntity):
    """An object representing user-defined localizable resources."""

    def get_resource_entries(self):
        """

        """
        return_type = ClientResult(self.context, ClientValueCollection(SPResourceEntry))
        qry = ServiceOperationQuery(self, "GetResourceEntries", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type
