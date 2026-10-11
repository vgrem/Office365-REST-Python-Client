from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.identitygovernance.entitlementmanagement.custom_extension_behavior_on_error import (
        CustomExtensionBehaviorOnError,
    )


class CustomAuthenticationExtension(Entity):
    @property
    def behavior_on_error(self) -> CustomExtensionBehaviorOnError:
        """Gets the behaviorOnError property"""
        from office365.directory.identitygovernance.entitlementmanagement.custom_extension_behavior_on_error import (
            CustomExtensionBehaviorOnError,
        )

        return self.properties.get("behaviorOnError", CustomExtensionBehaviorOnError())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CustomAuthenticationExtension"
