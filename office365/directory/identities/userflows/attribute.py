from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.identities.userflows.attributedatatype import (
        IdentityUserFlowAttributeDataType,
    )
    from office365.directory.identities.userflows.attributetype import (
        IdentityUserFlowAttributeType,
    )


class IdentityUserFlowAttribute(Entity):
    """
    Represents user flow attributes in an Azure Active Directory (Azure AD) tenant.

    Configuring user flow attributes in your Azure AD tenant allows you to collect information about
    a user during sign-up. You can choose to collect a built-in set of attributes. For example, given name, surname,
    city, and postal code. You can also configure custom user flow attributes to collect information
    from a user that is not built in to the directory. Custom user flow attributes are an abstraction over
    Azure Active Directory schema extensions.
    """

    @property
    def data_type(self) -> IdentityUserFlowAttributeDataType:
        """Gets the dataType property"""
        from office365.directory.identities.userflows.attributedatatype import (
            IdentityUserFlowAttributeDataType,
        )

        return self.properties.get("dataType", IdentityUserFlowAttributeDataType.string)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def user_flow_attribute_type(self) -> IdentityUserFlowAttributeType:
        """Gets the userFlowAttributeType property"""
        from office365.directory.identities.userflows.attributetype import (
            IdentityUserFlowAttributeType,
        )

        return self.properties.get("userFlowAttributeType", IdentityUserFlowAttributeType.builtIn)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IdentityUserFlowAttribute"
