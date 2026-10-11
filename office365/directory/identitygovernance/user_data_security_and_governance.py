from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.activities_container import (
        ActivitiesContainer,
    )
    from office365.directory.identitygovernance.user_protection_scope_container import (
        UserProtectionScopeContainer,
    )


class UserDataSecurityAndGovernance(Entity):
    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserDataSecurityAndGovernance"

    @property
    def activities(self) -> ActivitiesContainer:
        """Gets the activities property"""
        from office365.directory.identitygovernance.activities_container import (
            ActivitiesContainer,
        )

        return self.properties.get(
            "activities", ActivitiesContainer(self.context, ResourcePath("activities", self.resource_path))
        )

    @property
    def protection_scopes(self) -> UserProtectionScopeContainer:
        """Gets the protectionScopes property"""
        from office365.directory.identitygovernance.user_protection_scope_container import (
            UserProtectionScopeContainer,
        )

        return self.properties.get(
            "protectionScopes",
            UserProtectionScopeContainer(self.context, ResourcePath("protectionScopes", self.resource_path)),
        )
