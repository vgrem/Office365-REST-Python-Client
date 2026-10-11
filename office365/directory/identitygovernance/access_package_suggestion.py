from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.suggestion_reason import (
        AccessPackageSuggestionReason,
    )
    from office365.directory.identitygovernance.entitlementmanagement.available_access_package import (
        AvailableAccessPackage,
    )


class AccessPackageSuggestion(Entity):
    @property
    def reasons(self) -> ClientValueCollection[AccessPackageSuggestionReason]:
        """Gets the reasons property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.suggestion_reason import (
            AccessPackageSuggestionReason,
        )

        return self.properties.get(
            "reasons", ClientValueCollection[AccessPackageSuggestionReason](AccessPackageSuggestionReason)
        )

    @property
    def access_package(self) -> AvailableAccessPackage:
        """Gets the accessPackage property"""
        from office365.directory.identitygovernance.entitlementmanagement.available_access_package import (
            AvailableAccessPackage,
        )

        return self.properties.get(
            "accessPackage", AvailableAccessPackage(self.context, ResourcePath("accessPackage", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessPackageSuggestion"
