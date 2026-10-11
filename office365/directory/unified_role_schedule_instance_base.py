from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.objects.object import DirectoryObject
    from office365.directory.rolemanagement.app_scope import AppScope
    from office365.directory.rolemanagement.unifiedrole.definition import (
        UnifiedRoleDefinition,
    )


class UnifiedRoleScheduleInstanceBase(Entity):
    @property
    def app_scope_id(self) -> Optional[str]:
        """Gets the appScopeId property"""
        return self.properties.get("appScopeId", None)

    @property
    def directory_scope_id(self) -> Optional[str]:
        """Gets the directoryScopeId property"""
        return self.properties.get("directoryScopeId", None)

    @property
    def principal_id(self) -> Optional[str]:
        """Gets the principalId property"""
        return self.properties.get("principalId", None)

    @property
    def role_definition_id(self) -> Optional[str]:
        """Gets the roleDefinitionId property"""
        return self.properties.get("roleDefinitionId", None)

    @property
    def app_scope(self) -> AppScope:
        """Gets the appScope property"""
        from office365.directory.rolemanagement.app_scope import AppScope

        return self.properties.get("appScope", AppScope(self.context, ResourcePath("appScope", self.resource_path)))

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
    def role_definition(self) -> UnifiedRoleDefinition:
        """Gets the roleDefinition property"""
        from office365.directory.rolemanagement.unifiedrole.definition import (
            UnifiedRoleDefinition,
        )

        return self.properties.get(
            "roleDefinition", UnifiedRoleDefinition(self.context, ResourcePath("roleDefinition", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleScheduleInstanceBase"
