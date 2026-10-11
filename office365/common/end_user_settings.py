from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.suggestion_related_people_insight_level import (  # noqa: E501
        AccessPackageSuggestionRelatedPeopleInsightLevel,
    )


class EndUserSettings(Entity):
    @property
    def related_people_insight_level(self) -> AccessPackageSuggestionRelatedPeopleInsightLevel:
        """Gets the relatedPeopleInsightLevel property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.suggestion_related_people_insight_level import (  # noqa: E501
            AccessPackageSuggestionRelatedPeopleInsightLevel,
        )

        return self.properties.get(
            "relatedPeopleInsightLevel", AccessPackageSuggestionRelatedPeopleInsightLevel.disabled
        )

    @property
    def show_approver_details_to_members(self) -> Optional[bool]:
        """Gets the showApproverDetailsToMembers property"""
        return self.properties.get("showApproverDetailsToMembers", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EndUserSettings"
