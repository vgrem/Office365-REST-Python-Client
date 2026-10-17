from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata
from office365.security.alerts.alert import Alert
from office365.security.alerts.collection import AlertCollection
from office365.security.attacksimulations.root import AttackSimulationRoot
from office365.security.cases.root import CasesRoot
from office365.security.datasecurity.governance import (
    TenantDataSecurityAndGovernance,
)
from office365.security.hunting_query_results import HuntingQueryResults
from office365.security.incidents.incident import Incident
from office365.security.labels.root import LabelsRoot
from office365.security.scorecontrol.profile import SecureScoreControlProfile
from office365.security.subjectrightsrequests.request import (
    SubjectRightsRequest,
)
from office365.security.threatintelligence.threat_intelligence import (
    ThreatIntelligence,
)
from office365.security.triggers.root import TriggersRoot
from office365.security.triggertypes.root import TriggerTypesRoot

if TYPE_CHECKING:
    from office365.directory.identities.container import IdentityContainer
    from office365.security.audit.core_root import AuditCoreRoot
    from office365.security.collaboration.collaboration_root import (
        CollaborationRoot,
    )
    from office365.security.securescores.secure_score import SecureScore


class Security(Entity):
    """The security resource is the entry point for the Security object model. It returns a singleton security resource.
    It doesn't contain any usable properties."""

    def run_hunting_query(self, query: str) -> ClientResult[HuntingQueryResults]:
        """Queries a specified set of event, activity, or entity data supported by Microsoft 365 Defender
        to proactively look for specific threats in your environment.

        Args:
            query (str): The hunting query in Kusto Query Language (KQL). For more information on KQL syntax,
              see KQL quick reference:
              https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/kql-quick-reference
        """
        return_type = ClientResult(self.context, HuntingQueryResults())
        payload = {"Query": query}
        qry = ServiceOperationQuery(self, "runHuntingQuery", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def alerts(self) -> AlertCollection:
        return self.properties.get(
            "alerts",
            AlertCollection(self.context, ResourcePath("alerts", self.resource_path)),
        )

    @odata(name="alerts_v2")
    @property
    def alerts_v2(self) -> EntityCollection[Alert]:
        """A collection of alerts in Microsoft 365 Defender."""
        return self.properties.get(
            "alerts_v2",
            EntityCollection(self.context, Alert, ResourcePath("alerts_v2", self.resource_path)),
        )

    @property
    def cases(self) -> CasesRoot:
        """"""
        return self.properties.get("cases", CasesRoot(self.context, ResourcePath("cases", self.resource_path)))

    @odata(name="attackSimulation")
    @property
    def attack_simulation(self) -> AttackSimulationRoot:
        """"""
        return self.properties.get(
            "attackSimulation",
            AttackSimulationRoot(self.context, ResourcePath("attackSimulation", self.resource_path)),
        )

    @odata(name="dataSecurityAndGovernance")
    @property
    def data_security_and_governance(self) -> TenantDataSecurityAndGovernance:
        """Provides access to sensitivity labels and other data security settings."""
        return self.properties.get(
            "dataSecurityAndGovernance",
            TenantDataSecurityAndGovernance(self.context, ResourcePath("dataSecurityAndGovernance", self.resource_path)),
        )

    @property
    def incidents(self) -> EntityCollection[Incident]:
        """A collection of correlated alert instances and associated metadata that reflects the story of
        an attack in a tenant"""
        return self.properties.get(
            "incidents",
            EntityCollection(self.context, Incident, ResourcePath("incidents", self.resource_path)),
        )

    @property
    def labels(self) -> LabelsRoot:
        """"""
        return self.properties.get(
            "labels",
            LabelsRoot(self.context, ResourcePath("labels", self.resource_path)),
        )

    @odata(name="subjectRightsRequests")
    @property
    def subject_rights_requests(self) -> EntityCollection[SubjectRightsRequest]:
        """Get a list of the subjectRightsRequest objects and their properties."""
        return self.properties.get(
            "subjectRightsRequests",
            EntityCollection(
                self.context,
                SubjectRightsRequest,
                ResourcePath("subjectRightsRequests", self.resource_path),
            ),
        )

    @odata(name="secureScoreControlProfiles")
    @property
    def secure_score_control_profiles(
        self,
    ) -> EntityCollection[SecureScoreControlProfile]:
        """"""
        return self.properties.get(
            "secureScoreControlProfiles",
            EntityCollection(
                self.context,
                SecureScoreControlProfile,
                ResourcePath("secureScoreControlProfiles", self.resource_path),
            ),
        )

    @property
    def triggers(self) -> TriggersRoot:
        """"""
        return self.properties.get(
            "triggers",
            TriggersRoot(self.context, ResourcePath("triggers", self.resource_path)),
        )

    @odata(name="triggerTypes")
    @property
    def trigger_types(self) -> TriggerTypesRoot:
        """"""
        return self.properties.get(
            "triggerTypes",
            TriggerTypesRoot(self.context, ResourcePath("triggerTypes", self.resource_path)),
        )

    @odata(name="threatIntelligence")
    @property
    def threat_intelligence(self) -> ThreatIntelligence:
        """"""
        return self.properties.get(
            "threatIntelligence",
            ThreatIntelligence(self.context, ResourcePath("threatIntelligence", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.Security"

    @property
    def identities(self) -> IdentityContainer:
        """Gets the identities property"""
        from office365.directory.identities.container import IdentityContainer

        return self.properties.get(
            "identities", IdentityContainer(self.context, ResourcePath("identities", self.resource_path))
        )

    @property
    def audit_log(self) -> AuditCoreRoot:
        """Gets the auditLog property"""
        from office365.security.audit.core_root import AuditCoreRoot

        return self.properties.get("auditLog", AuditCoreRoot(self.context, ResourcePath("auditLog", self.resource_path)))

    @property
    def collaboration(self) -> CollaborationRoot:
        """Gets the collaboration property"""
        from office365.security.collaboration.collaboration_root import (
            CollaborationRoot,
        )

        return self.properties.get(
            "collaboration", CollaborationRoot(self.context, ResourcePath("collaboration", self.resource_path))
        )

    @property
    def secure_scores(self) -> EntityCollection[SecureScore]:
        """Gets the secureScores property"""
        from office365.security.securescores.secure_score import SecureScore

        return self.properties.get(
            "secureScores",
            EntityCollection[SecureScore](self.context, SecureScore, ResourcePath("secureScores", self.resource_path)),
        )
