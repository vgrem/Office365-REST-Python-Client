from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.permissions.role_definition import RoleDefinition


class RoleDefinitionCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(RoleDefinitionCollection, self).__init__(context, RoleDefinition, resource_path)

    def get_by_type(self, role_type):
        """Returns role definition of the specified type from the collection.

        :param int role_type: Specifies the role type. Role type MUST NOT be None.
        """

        role_def = RoleDefinition(self.context)
        self.add_child(role_def)
        qry = ServiceOperationQuery(self, "GetByType", [role_type], None, None, role_def)
        self.context.add_query(qry)
        return role_def
