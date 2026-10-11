from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.users.user import User
from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.teams.administration.assigned_telephone_number import (
    AssignedTelephoneNumber,
)
from office365.teams.administration.effective_policy_assignment import (
    EffectivePolicyAssignment,
)

if TYPE_CHECKING:
    from office365.teams.administration.account_type import AccountType


class TeamsUserConfiguration(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def effective_policy_assignments(self) -> ClientValueCollection[EffectivePolicyAssignment]:
        """Gets the effectivePolicyAssignments property"""
        return self.properties.get(
            "effectivePolicyAssignments", ClientValueCollection[EffectivePolicyAssignment](EffectivePolicyAssignment)
        )

    @property
    def feature_types(self) -> StringCollection:
        """Gets the featureTypes property"""
        return self.properties.get("featureTypes", StringCollection(None))

    @property
    def is_enterprise_voice_enabled(self) -> Optional[bool]:
        """Gets the isEnterpriseVoiceEnabled property"""
        return self.properties.get("isEnterpriseVoiceEnabled", None)

    @property
    def modified_date_time(self) -> Optional[datetime]:
        """Gets the modifiedDateTime property"""
        return self.properties.get("modifiedDateTime", datetime.min)

    @property
    def telephone_numbers(self) -> ClientValueCollection[AssignedTelephoneNumber]:
        """Gets the telephoneNumbers property"""
        return self.properties.get(
            "telephoneNumbers", ClientValueCollection[AssignedTelephoneNumber](AssignedTelephoneNumber)
        )

    @property
    def tenant_id(self) -> Optional[str]:
        """Gets the tenantId property"""
        return self.properties.get("tenantId", None)

    @property
    def user_principal_name(self) -> Optional[str]:
        """Gets the userPrincipalName property"""
        return self.properties.get("userPrincipalName", None)

    @property
    def user(self) -> User:
        """Gets the user property"""
        return self.properties.get("user", User(self.context, ResourcePath("user", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.teamsAdministration.TeamsUserConfiguration"

    @property
    def account_type(self) -> AccountType:
        """Gets the accountType property"""
        from office365.teams.administration.account_type import AccountType

        return self.properties.get("accountType", AccountType.user)
