from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.usercustomactions.user_custom_action import UserCustomAction


class UserCustomActionCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(UserCustomActionCollection, self).__init__(context, UserCustomAction, resource_path)

    def clear(self):
        qry = ServiceOperationQuery(self, "Clear")
        self.context.add_query(qry)
        return self
