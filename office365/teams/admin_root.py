from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.policy_assignment import TeamsPolicyAssignment

if TYPE_CHECKING:
    from office365.teams.administration.telephone_number_management_root import (
        TelephoneNumberManagementRoot,
    )
    from office365.teams.administration.user_configuration import TeamsUserConfiguration


class TeamsAdminRoot(Entity):
    @property
    def policy(self) -> TeamsPolicyAssignment:
        """Gets the policy property"""
        return self.properties.get(
            "policy", TeamsPolicyAssignment(self.context, ResourcePath("policy", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.teamsAdministration.TeamsAdminRoot"

    @property
    def user_configurations(self) -> EntityCollection[TeamsUserConfiguration]:
        """Gets the userConfigurations property"""
        from office365.teams.administration.user_configuration import (
            TeamsUserConfiguration,
        )

        return self.properties.get(
            "userConfigurations",
            EntityCollection[TeamsUserConfiguration](
                self.context, TeamsUserConfiguration, ResourcePath("userConfigurations", self.resource_path)
            ),
        )

    @property
    def telephone_number_management(self) -> TelephoneNumberManagementRoot:
        """Gets the telephoneNumberManagement property"""
        from office365.teams.administration.telephone_number_management_root import (
            TelephoneNumberManagementRoot,
        )

        return self.properties.get(
            "telephoneNumberManagement",
            TelephoneNumberManagementRoot(self.context, ResourcePath("telephoneNumberManagement", self.resource_path)),
        )
