from __future__ import annotations

from office365.directory.permissions.require_permission import require_permission
from office365.entity import Entity
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.function import FunctionQuery
from office365.security.attacksimulations.repeat_offender import (
    AttackSimulationRepeatOffender,
)
from office365.security.attacksimulations.user_coverage import (
    AttackSimulationSimulationUserCoverage,
)


class SecurityReportsRoot(Entity):
    """
    Represents an abstract type that contains resources for attack simulation and training reports. This resource
    provides the ability to launch a realistic simulated phishing attack that organizations can learn from.
    """

    @require_permission(delegated=["AttackSimulation.Read.All"], application=["AttackSimulation.Read.All"])
    def get_attack_simulation_repeat_offenders(
        self,
    ) -> ClientResult[ClientValueCollection[AttackSimulationRepeatOffender]]:
        """
        List the tenant users who have yielded to attacks more than once in attack simulation and training campaigns.
        """
        return_type = ClientResult(self.context, ClientValueCollection(AttackSimulationRepeatOffender))
        qry = FunctionQuery(self, "getAttackSimulationRepeatOffenders", None, return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(delegated=["AttackSimulation.Read.All"], application=["AttackSimulation.Read.All"])
    def get_attack_simulation_simulation_user_coverage(
        self,
    ) -> ClientResult[ClientValueCollection[AttackSimulationSimulationUserCoverage]]:
        """
        List training coverage for each tenant user in attack simulation and training campaigns.
        """
        return_type = ClientResult(self.context, ClientValueCollection(AttackSimulationSimulationUserCoverage))
        qry = FunctionQuery(self, "getAttackSimulationSimulationUserCoverage", None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SecurityReportsRoot"
