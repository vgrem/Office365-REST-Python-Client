from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.management.terms_and_conditions import (
        TermsAndConditions,
    )


class TermsAndConditionsAcceptanceStatus(Entity):
    @property
    def accepted_date_time(self) -> Optional[datetime]:
        """Gets the acceptedDateTime property"""
        return self.properties.get("acceptedDateTime", datetime.min)

    @property
    def accepted_version(self) -> Optional[int]:
        """Gets the acceptedVersion property"""
        return self.properties.get("acceptedVersion", None)

    @property
    def user_display_name(self) -> Optional[str]:
        """Gets the userDisplayName property"""
        return self.properties.get("userDisplayName", None)

    @property
    def user_principal_name(self) -> Optional[str]:
        """Gets the userPrincipalName property"""
        return self.properties.get("userPrincipalName", None)

    @property
    def terms_and_conditions(self) -> TermsAndConditions:
        """Gets the termsAndConditions property"""
        from office365.intune.devices.management.terms_and_conditions import (
            TermsAndConditions,
        )

        return self.properties.get(
            "termsAndConditions",
            TermsAndConditions(self.context, ResourcePath("termsAndConditions", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TermsAndConditionsAcceptanceStatus"
