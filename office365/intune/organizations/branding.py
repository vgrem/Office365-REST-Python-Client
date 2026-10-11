from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity_collection import EntityCollection
from office365.intune.organizations.branding_properties import (
    OrganizationalBrandingProperties,
)
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.organizations.organizational_branding_localization import (
        OrganizationalBrandingLocalization,
    )


class OrganizationalBranding(OrganizationalBrandingProperties):
    """
    Contains details about the organization's default branding. Inherits from organizationalBrandingProperties.

    Organizations can customize their Azure Active Directory (Azure AD) sign-in pages which appear when users sign
    in to their organization's tenant-specific apps, or when Azure AD identifies the user's tenant from their username.
    A developer can also read the company's branding information and customize their app experience to tailor
    it specifically for the signed-in user using their company's branding.

    You can't change your original configuration's language. However, companies can add different branding based on
    locale. For language-specific branding, see the organizationalBrandingLocalization object.
    """

    @property
    def localizations(self) -> EntityCollection[OrganizationalBrandingLocalization]:
        """Gets the localizations property"""
        from office365.intune.organizations.organizational_branding_localization import (
            OrganizationalBrandingLocalization,
        )

        return self.properties.get(
            "localizations",
            EntityCollection[OrganizationalBrandingLocalization](
                self.context, OrganizationalBrandingLocalization, ResourcePath("localizations", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OrganizationalBranding"
