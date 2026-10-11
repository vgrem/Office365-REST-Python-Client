from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.directory.rolemanagement.app_scope import AppScope
from office365.directory.rolemanagement.unifiedrole.definition import (
    UnifiedRoleDefinition,
)
from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.objects.object import DirectoryObject


class UnifiedRoleAssignment(Entity):
    """
    A role assignment is used to grant access to resources. It represents a role definition assigned to a principal
    (for example, a user or a role-assignable group) at a particular scope.
    """

    @property
    def app_scope_id(self) -> Optional[str]:
        """
        Identifier of the app-specific scope when the assignment scope is app-specific. Either this property or
        directoryScopeId is required. App scopes are scopes that are defined and understood by this application only.
        Use / for tenant-wide app scopes. Use directoryScopeId to limit the scope to particular directory objects,
        for example, administrative units. Supports $filter (eq, in).
        """
        return self.properties.get("appScopeId", None)

    @property
    def condition(self) -> Optional[str]:
        """ """
        return self.properties.get("condition", None)

    @property
    def principal_id(self) -> Optional[str]:
        """Identifier of the principal to which the assignment is granted. Supported principals are users,
        role-assignable groups, and service principals. Supports $filter (eq, in)."""
        return self.properties.get("principalId", None)

    @property
    def role_definition_id(self) -> Optional[str]:
        """Identifier of the unifiedRoleDefinition the assignment is for. Read-only. Supports $filter (eq, in)."""
        return self.properties.get("roleDefinitionId", None)

    @property
    def directory_scope_id(self) -> Optional[str]:
        """Identifier of the directory object representing the scope of the assignment.
        The scope of an assignment determines the set of resources for which the principal has been granted access.
        Directory scopes are shared scopes stored in the directory that are understood by multiple applications,
        unlike app scopes that are defined and understood by a resource application only. Supports $filter (eq, in).
        """
        return self.properties.get("directoryScopeId", None)

    @odata(name="roleDefinition")
    @property
    def role_definition(self) -> UnifiedRoleDefinition:
        """
        The roleDefinition the assignment is for. Supports $expand. roleDefinition.Id will be auto expanded.
        """
        return self.properties.get(
            "roleDefinition",
            UnifiedRoleDefinition(self.context, ResourcePath("roleDefinition", self.resource_path)),
        )

    @odata(name="appScope")
    @property
    def app_scope(self) -> AppScope:
        """
        Read-only property with details of the app specific scope when the assignment scope is app specific.
        Containment entity. Supports $expand for the entitlement provider only.
        """
        return self.properties.get(
            "appScope",
            AppScope(self.context, ResourcePath("appScope", self.resource_path)),
        )

    @property
    def principal_organization_id(self) -> Optional[str]:
        """Gets the principalOrganizationId property"""
        return self.properties.get("principalOrganizationId", None)

    @property
    def directory_scope(self) -> DirectoryObject:
        """Gets the directoryScope property"""
        from office365.directory.objects.object import DirectoryObject

        return self.properties.get(
            "directoryScope", DirectoryObject(self.context, ResourcePath("directoryScope", self.resource_path))
        )

    @property
    def principal(self) -> DirectoryObject:
        """Gets the principal property"""
        from office365.directory.objects.object import DirectoryObject

        return self.properties.get(
            "principal", DirectoryObject(self.context, ResourcePath("principal", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleAssignment"
