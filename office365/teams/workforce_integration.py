from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.teams.schedule.eligibilityfilteringenabledentities import (
        EligibilityFilteringEnabledEntities,
    )
    from office365.teams.teamwork.workforce_integration_supported_entities import (
        WorkforceIntegrationSupportedEntities,
    )
    from office365.teams.workforce_integration_encryption import (
        WorkforceIntegrationEncryption,
    )


class WorkforceIntegration(Entity):
    @property
    def api_version(self) -> Optional[int]:
        """Gets the apiVersion property"""
        return self.properties.get("apiVersion", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def eligibility_filtering_enabled_entities(self) -> EligibilityFilteringEnabledEntities:
        """Gets the eligibilityFilteringEnabledEntities property"""
        from office365.teams.schedule.eligibilityfilteringenabledentities import (
            EligibilityFilteringEnabledEntities,
        )

        return self.properties.get("eligibilityFilteringEnabledEntities", EligibilityFilteringEnabledEntities.none)

    @property
    def encryption(self) -> WorkforceIntegrationEncryption:
        """Gets the encryption property"""
        from office365.teams.workforce_integration_encryption import (
            WorkforceIntegrationEncryption,
        )

        return self.properties.get("encryption", WorkforceIntegrationEncryption())

    @property
    def is_active(self) -> Optional[bool]:
        """Gets the isActive property"""
        return self.properties.get("isActive", None)

    @property
    def supported_entities(self) -> WorkforceIntegrationSupportedEntities:
        """Gets the supportedEntities property"""
        from office365.teams.teamwork.workforce_integration_supported_entities import (
            WorkforceIntegrationSupportedEntities,
        )

        return self.properties.get("supportedEntities", WorkforceIntegrationSupportedEntities.none)

    @property
    def url(self) -> Optional[str]:
        """Gets the url property"""
        return self.properties.get("url", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkforceIntegration"
