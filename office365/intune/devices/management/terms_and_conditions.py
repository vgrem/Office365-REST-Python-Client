from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.management.terms_and_conditions_acceptance_status import (
        TermsAndConditionsAcceptanceStatus,
    )
    from office365.intune.devices.management.terms_and_conditions_assignment import (
        TermsAndConditionsAssignment,
    )


class TermsAndConditions(Entity):
    """
    A termsAndConditions entity represents the metadata and contents of a given Terms and Conditions (T&C) policy.
    T&C policies’ contents are presented to users upon their first attempt to enroll into Intune and subsequently
    upon edits where an administrator has required re-acceptance. They enable administrators to communicate
    the provisions to which a user must agree in order to have devices enrolled into Intune.
    """

    @property
    def acceptance_statement(self) -> Optional[str]:
        """Gets the acceptanceStatement property"""
        return self.properties.get("acceptanceStatement", None)

    @property
    def body_text(self) -> Optional[str]:
        """Gets the bodyText property"""
        return self.properties.get("bodyText", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def title(self) -> Optional[str]:
        """Gets the title property"""
        return self.properties.get("title", None)

    @property
    def version(self) -> Optional[int]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def acceptance_statuses(self) -> EntityCollection[TermsAndConditionsAcceptanceStatus]:
        """Gets the acceptanceStatuses property"""
        from office365.intune.devices.management.terms_and_conditions_acceptance_status import (
            TermsAndConditionsAcceptanceStatus,
        )

        return self.properties.get(
            "acceptanceStatuses",
            EntityCollection[TermsAndConditionsAcceptanceStatus](
                self.context, TermsAndConditionsAcceptanceStatus, ResourcePath("acceptanceStatuses", self.resource_path)
            ),
        )

    @property
    def assignments(self) -> EntityCollection[TermsAndConditionsAssignment]:
        """Gets the assignments property"""
        from office365.intune.devices.management.terms_and_conditions_assignment import (
            TermsAndConditionsAssignment,
        )

        return self.properties.get(
            "assignments",
            EntityCollection[TermsAndConditionsAssignment](
                self.context, TermsAndConditionsAssignment, ResourcePath("assignments", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TermsAndConditions"
