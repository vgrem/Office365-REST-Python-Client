from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.policies.conditionalaccess.condition_set import (
        ConditionalAccessConditionSet,
    )
    from office365.directory.policies.conditionalaccess.grant_controls import (
        ConditionalAccessGrantControls,
    )
    from office365.directory.policies.conditionalaccess.policystate import (
        ConditionalAccessPolicyState,
    )
    from office365.directory.policies.conditionalaccess.session_controls import (
        ConditionalAccessSessionControls,
    )


class ConditionalAccessPolicy(Entity):
    """
    Represents an Azure Active Directory conditional access policy.
    Conditional access policies are custom rules that define an access scenario.
    """

    @property
    def created_datetime(self) -> datetime:
        """Date and time (UTC) the sign-in was initiated."""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def conditions(self) -> ConditionalAccessConditionSet:
        """Gets the conditions property"""
        from office365.directory.policies.conditionalaccess.condition_set import (
            ConditionalAccessConditionSet,
        )

        return self.properties.get("conditions", ConditionalAccessConditionSet())

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def grant_controls(self) -> ConditionalAccessGrantControls:
        """Gets the grantControls property"""
        from office365.directory.policies.conditionalaccess.grant_controls import (
            ConditionalAccessGrantControls,
        )

        return self.properties.get("grantControls", ConditionalAccessGrantControls())

    @property
    def id(self) -> Optional[str]:
        """Gets the id property"""
        return self.properties.get("id", None)

    @property
    def modified_date_time(self) -> Optional[datetime]:
        """Gets the modifiedDateTime property"""
        return self.properties.get("modifiedDateTime", datetime.min)

    @property
    def session_controls(self) -> ConditionalAccessSessionControls:
        """Gets the sessionControls property"""
        from office365.directory.policies.conditionalaccess.session_controls import (
            ConditionalAccessSessionControls,
        )

        return self.properties.get("sessionControls", ConditionalAccessSessionControls())

    @property
    def state(self) -> ConditionalAccessPolicyState:
        """Gets the state property"""
        from office365.directory.policies.conditionalaccess.policystate import (
            ConditionalAccessPolicyState,
        )

        return self.properties.get("state", ConditionalAccessPolicyState.enabled)

    @property
    def template_id(self) -> Optional[str]:
        """Gets the templateId property"""
        return self.properties.get("templateId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ConditionalAccessPolicy"
