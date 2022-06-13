from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.permissions.role_definition import RoleDefinition


class RoleDefinitionCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(RoleDefinitionCollection, self).__init__(context, RoleDefinition, resource_path)

    def get_by_type(self, role_type):
        """Returns role definition of the specified type from the collection.

        :param int role_type: Specifies the role type. Role type MUST NOT be None.
        """
        return RoleDefinition(self.context,
                              ServiceOperationPath("GetByType", [role_type], self.resource_path))
