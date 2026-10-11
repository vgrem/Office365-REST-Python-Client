from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.directory.profile_card_annotation import ProfileCardAnnotation


class ProfileCardProperty(Entity):
    """
    Represents an attribute of a user on the Microsoft 365 profile card for an organization to surface in a shared,
    people experience.

    The attribute can be an Microsoft Entra ID built-in attribute, such as Alias or UserPrincipalName,
    or it can be a custom attribute. For a custom attribute, an administrator can define an en-us default display name
    String and a set of alternative translations for the languages supported in their organization.

    For more information about how to add properties to the profile card for an organization, see Add or remove
    custom attributes on a profile card using the profile card API.
    """

    @property
    def annotations(self) -> ClientValueCollection[ProfileCardAnnotation]:
        """Gets the annotations property"""
        from office365.directory.profile_card_annotation import ProfileCardAnnotation

        return self.properties.get("annotations", ClientValueCollection[ProfileCardAnnotation](ProfileCardAnnotation))

    @property
    def directory_property_name(self) -> Optional[str]:
        """Gets the directoryPropertyName property"""
        return self.properties.get("directoryPropertyName", None)

    @property
    def is_visible(self) -> Optional[bool]:
        """Gets the isVisible property"""
        return self.properties.get("isVisible", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProfileCardProperty"
