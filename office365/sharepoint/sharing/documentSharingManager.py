from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.permissions.roleDefinition import RoleDefinition


class DocumentSharingManager(BaseEntity):
    """Specifies document sharing related methods."""

    def get_role_definition(self, role):
        """his method returns a role definition in the current web that is associated with a given Role
        (section 3.2.5.188) value.

        :param int role: A Role value for which to obtain the associated role definition object.
        """
        role_def = RoleDefinition(self.context)
        qry = ServiceOperationQuery(self, "GetRoleDefinition", [role], None, None, role_def)
        qry.static = True
        self.context.add_query(qry)
        return role_def

    @property
    def entity_type_name(self):
        return "SP.Sharing.DocumentSharingManager"
