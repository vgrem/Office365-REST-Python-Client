from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class SharingPermissionInformation(Entity):
    """
    Contains information about a sharing permission entity such as group or role.
    """

    @property
    def is_default_permission(self) -> Optional[bool]:
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
        """
        return self.properties.get("IsDefaultPermission", None)

    @property
    def permission_id(self) -> Optional[str]:
        """Gets the ID of this permission in the following formats: group:x, role: xxxxxx."""
        return self.properties.get("PermissionId", None)

    @property
    def entity_type_name(self):
        return "SP.SharingPermissionInformation"

    @property
    def permission_description(self) -> Optional[str]:
        """Gets the PermissionDescription property"""
        return self.properties.get("PermissionDescription", None)

    @property
    def permission_kind(self) -> Optional[int]:
        """Gets the PermissionKind property"""
        return self.properties.get("PermissionKind", None)

    @property
    def permission_name(self) -> Optional[str]:
        """Gets the PermissionName property"""
        return self.properties.get("PermissionName", None)

    @property
    def permission_role_type(self) -> Optional[int]:
        """Gets the PermissionRoleType property"""
        return self.properties.get("PermissionRoleType", None)
