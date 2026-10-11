from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.directory.identitygovernance.accessreview.reviewer_scope import (
        AccessReviewReviewerScope,
    )


class AdminConsentRequestPolicy(Entity):
    """
    Represents the policy for enabling or disabling the Microsoft Entra admin consent workflow.
    The admin consent workflow allows users to request access for apps that they wish to use and that require admin
    authorization before users can use the apps to access organizational data.
    There is a single adminConsentRequestPolicy per tenant.
    """

    @property
    def is_enabled(self) -> Optional[bool]:
        """Gets the isEnabled property"""
        return self.properties.get("isEnabled", None)

    @property
    def notify_reviewers(self) -> Optional[bool]:
        """Gets the notifyReviewers property"""
        return self.properties.get("notifyReviewers", None)

    @property
    def reminders_enabled(self) -> Optional[bool]:
        """Gets the remindersEnabled property"""
        return self.properties.get("remindersEnabled", None)

    @property
    def request_duration_in_days(self) -> Optional[int]:
        """Gets the requestDurationInDays property"""
        return self.properties.get("requestDurationInDays", None)

    @property
    def reviewers(self) -> ClientValueCollection[AccessReviewReviewerScope]:
        """Gets the reviewers property"""
        from office365.directory.identitygovernance.accessreview.reviewer_scope import (
            AccessReviewReviewerScope,
        )

        return self.properties.get(
            "reviewers", ClientValueCollection[AccessReviewReviewerScope](AccessReviewReviewerScope)
        )

    @property
    def version(self) -> Optional[int]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AdminConsentRequestPolicy"
