from office365.sharepoint.base_entity import BaseEntity


class SharingPermissionInformation(BaseEntity):
    """
    Contains information about a sharing permission entity such as group or role.
    """

    @property
    def is_default_permission(self):
        """
        Identifies whether or not the permission entity is a default SP.Group or role (meaning it is recommended
        for granting permissions).

        A value of true specifies the current permission is a default SP.Group for granting permissions to a site
        (site owner, member, or visitor SP.Group) or a default role for granting permission to a file or other
        non-site object (edit or view). A value of false specifies otherwise.

        For SPSites & SPWebs, there can be three default permission entities: owners, members, or visitors SPGroups.
        For granting permissions to a file or other non-site object, there can be two default permission entities:
        a role for view permissions (StandardViewerRoleDefinitionID) and a role for edit permissions
        (StandardEditorRoleDefinitionID).

        :rtype: bool or None
        """
        return self.properties.get("IsDefaultPermission", None)

    @property
    def permission_id(self):
        """Gets the ID of this permission in the following formats: group:x, role: xxxxxx.
        :rtype: str or None
        """
        return self.properties.get("PermissionId", None)

    @property
    def entity_type_name(self):
        return "SP.SharingPermissionInformation"
