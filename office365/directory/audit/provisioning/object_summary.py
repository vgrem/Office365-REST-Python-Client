from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.audit.initiator import Initiator
from office365.directory.audit.provisioning.action import ProvisioningAction
from office365.directory.audit.provisioning.provisionedidentity import (
    ProvisionedIdentity,
)
from office365.directory.audit.provisioning.service_principal import (
    ProvisioningServicePrincipal,
)
from office365.directory.audit.provisioning.statusinfo import ProvisioningStatusInfo
from office365.directory.audit.provisioning.step import ProvisioningStep
from office365.directory.audit.provisioning.system import ProvisioningSystem
from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.modified_property import ModifiedProperty


class ProvisioningObjectSummary(Entity):
    """Represents an action performed by the Azure AD Provisioning service and its associated properties."""

    @odata(name="activityDateTime")
    @property
    def activity_datetime(self) -> datetime:
        """Represents date and time information using ISO 8601 format and is always in UTC time."""
        return self.properties.get("activityDateTime", datetime.min)

    @property
    def change_id(self) -> Optional[str]:
        """Unique ID of this change in this cycle. Supports $filter (eq, contains)."""
        return self.properties.get("changeId", None)

    @property
    def cycle_id(self) -> Optional[str]:
        """Unique ID per job iteration. Supports $filter (eq, contains)."""
        return self.properties.get("cycleId", None)

    @property
    def duration_in_milliseconds(self) -> Optional[int]:
        """Indicates how long this provisioning action took to finish. Measured in milliseconds."""
        return self.properties.get("durationInMilliseconds", None)

    @odata(name="servicePrincipal")
    @property
    def service_principal(self):
        """Represents the service principal used for provisioning."""
        return self.properties.get("servicePrincipal", ProvisioningServicePrincipal())

    @property
    def activity_date_time(self) -> Optional[datetime]:
        """Gets the activityDateTime property"""
        return self.properties.get("activityDateTime", datetime.min)

    @property
    def initiated_by(self) -> Initiator:
        """Gets the initiatedBy property"""
        return self.properties.get("initiatedBy", Initiator())

    @property
    def job_id(self) -> Optional[str]:
        """Gets the jobId property"""
        return self.properties.get("jobId", None)

    @property
    def provisioning_action(self) -> ProvisioningAction:
        """Gets the provisioningAction property"""
        return self.properties.get("provisioningAction", ProvisioningAction.other)

    @property
    def provisioning_status_info(self) -> ProvisioningStatusInfo:
        """Gets the provisioningStatusInfo property"""
        return self.properties.get("provisioningStatusInfo", ProvisioningStatusInfo())

    @property
    def provisioning_steps(self) -> ClientValueCollection[ProvisioningStep]:
        """Gets the provisioningSteps property"""
        return self.properties.get("provisioningSteps", ClientValueCollection[ProvisioningStep](ProvisioningStep))

    @property
    def source_identity(self) -> ProvisionedIdentity:
        """Gets the sourceIdentity property"""
        return self.properties.get("sourceIdentity", ProvisionedIdentity())

    @property
    def source_system(self) -> ProvisioningSystem:
        """Gets the sourceSystem property"""
        return self.properties.get("sourceSystem", ProvisioningSystem())

    @property
    def target_identity(self) -> ProvisionedIdentity:
        """Gets the targetIdentity property"""
        return self.properties.get("targetIdentity", ProvisionedIdentity())

    @property
    def target_system(self) -> ProvisioningSystem:
        """Gets the targetSystem property"""
        return self.properties.get("targetSystem", ProvisioningSystem())

    @property
    def tenant_id(self) -> Optional[str]:
        """Gets the tenantId property"""
        return self.properties.get("tenantId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProvisioningObjectSummary"

    @property
    def modified_properties(self) -> ClientValueCollection[ModifiedProperty]:
        """Gets the modifiedProperties property"""
        from office365.directory.modified_property import ModifiedProperty

        return self.properties.get("modifiedProperties", ClientValueCollection[ModifiedProperty](ModifiedProperty))
