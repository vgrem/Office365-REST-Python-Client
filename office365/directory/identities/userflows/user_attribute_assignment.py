from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identities.userflows.attribute import (
        IdentityUserFlowAttribute,
    )
    from office365.directory.identities.userflows.attributeinputtype import (
        IdentityUserFlowAttributeInputType,
    )
    from office365.directory.identities.userflows.user_attribute_values_item import (
        UserAttributeValuesItem,
    )


class IdentityUserFlowAttributeAssignment(Entity):
    """Update the properties of a identityUserFlowAttributeAssignment object."""

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def is_optional(self) -> Optional[bool]:
        """Gets the isOptional property"""
        return self.properties.get("isOptional", None)

    @property
    def requires_verification(self) -> Optional[bool]:
        """Gets the requiresVerification property"""
        return self.properties.get("requiresVerification", None)

    @property
    def user_attribute_values(self) -> ClientValueCollection[UserAttributeValuesItem]:
        """Gets the userAttributeValues property"""
        from office365.directory.identities.userflows.user_attribute_values_item import (
            UserAttributeValuesItem,
        )

        return self.properties.get(
            "userAttributeValues", ClientValueCollection[UserAttributeValuesItem](UserAttributeValuesItem)
        )

    @property
    def user_input_type(self) -> IdentityUserFlowAttributeInputType:
        """Gets the userInputType property"""
        from office365.directory.identities.userflows.attributeinputtype import (
            IdentityUserFlowAttributeInputType,
        )

        return self.properties.get("userInputType", IdentityUserFlowAttributeInputType.textBox)

    @property
    def user_attribute(self) -> IdentityUserFlowAttribute:
        """Gets the userAttribute property"""
        from office365.directory.identities.userflows.attribute import (
            IdentityUserFlowAttribute,
        )

        return self.properties.get(
            "userAttribute", IdentityUserFlowAttribute(self.context, ResourcePath("userAttribute", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IdentityUserFlowAttributeAssignment"


class IdentityUserFlowAttributeAssignmentCollection(EntityCollection):
    def __init__(self, context, resource_path=None):
        super().__init__(context, IdentityUserFlowAttributeAssignment, resource_path)
