from office365.runtime.client_result import ClientResult
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.permissions.role_definition import RoleDefinition
from office365.sharepoint.sharing.user_sharing_result import UserSharingResult


class SharedWithMeViewItemRemovalResult(ClientValue):
    pass


class DocumentSharingManager(BaseEntity):
    """Specifies document sharing related methods."""

    def get_role_definition(self, role):
        """This method returns a role definition in the current web that is associated with a given Role
        (section 3.2.5.188) value.

        :param int role: A Role value for which to obtain the associated role definition object.
        """
        role_def = RoleDefinition(self.context)
        self.context.web.role_definitions.add_child(role_def)
        qry = ServiceOperationQuery(self, "GetRoleDefinition", [role], None, None, role_def)
        qry.static = True
        self.context.add_query(qry)
        return role_def

    def remove_items_from_shared_with_me_view(self, item_urls):
        """
        :type item_urls: list[str]
        """
        result = ClientResult(self.context, ClientValueCollection(SharedWithMeViewItemRemovalResult))
        qry = ServiceOperationQuery(self, "RemoveItemsFromSharedWithMeView", [item_urls], None, None, result)
        qry.static = True
        self.context.add_query(qry)
        return result

    def update_document_sharing_info(self, resource_address, userRoleAssignments, validateExistingPermissions,
                                     additiveMode, sendServerManagedNotification, customMessage,
                                     includeAnonymousLinksInNotification, propagateAcl):
        """

        :param str resource_address:
        :param ClientValueCollection userRoleAssignments:
        :param bool validateExistingPermissions:
        :param bool additiveMode:
        :param bool sendServerManagedNotification:
        :param str customMessage:
        :param bool includeAnonymousLinksInNotification:
        :param bool propagateAcl:
        """
        result = ClientResult(self.context, ClientValueCollection(UserSharingResult))
        payload = {
            "resourceAddress": resource_address,
            "userRoleAssignments": userRoleAssignments,
            "validateExistingPermissions": validateExistingPermissions,
            "additiveMode": additiveMode,
            "sendServerManagedNotification": sendServerManagedNotification,
            "customMessage": customMessage,
            "includeAnonymousLinksInNotification": includeAnonymousLinksInNotification,
            "propagateAcl": propagateAcl
        }
        qry = ServiceOperationQuery(self, "UpdateDocumentSharingInfo", None, payload, None, result)
        qry.static = True
        self.context.add_query(qry)
        return result

    @property
    def entity_type_name(self):
        return "SP.Sharing.DocumentSharingManager"
