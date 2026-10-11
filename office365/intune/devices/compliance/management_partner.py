from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.intune.devices.compliance.management_partner_assignment import (
        ComplianceManagementPartnerAssignment,
    )
    from office365.intune.devices.management.partnertenantstate import (
        DeviceManagementPartnerTenantState,
    )


class ComplianceManagementPartner(Entity):
    @property
    def android_enrollment_assignments(self) -> ClientValueCollection[ComplianceManagementPartnerAssignment]:
        """Gets the androidEnrollmentAssignments property"""
        from office365.intune.devices.compliance.management_partner_assignment import (
            ComplianceManagementPartnerAssignment,
        )

        return self.properties.get(
            "androidEnrollmentAssignments",
            ClientValueCollection[ComplianceManagementPartnerAssignment](ComplianceManagementPartnerAssignment),
        )

    @property
    def android_onboarded(self) -> Optional[bool]:
        """Gets the androidOnboarded property"""
        return self.properties.get("androidOnboarded", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def ios_enrollment_assignments(self) -> ClientValueCollection[ComplianceManagementPartnerAssignment]:
        """Gets the iosEnrollmentAssignments property"""
        from office365.intune.devices.compliance.management_partner_assignment import (
            ComplianceManagementPartnerAssignment,
        )

        return self.properties.get(
            "iosEnrollmentAssignments",
            ClientValueCollection[ComplianceManagementPartnerAssignment](ComplianceManagementPartnerAssignment),
        )

    @property
    def ios_onboarded(self) -> Optional[bool]:
        """Gets the iosOnboarded property"""
        return self.properties.get("iosOnboarded", None)

    @property
    def last_heartbeat_date_time(self) -> Optional[datetime]:
        """Gets the lastHeartbeatDateTime property"""
        return self.properties.get("lastHeartbeatDateTime", datetime.min)

    @property
    def mac_os_enrollment_assignments(self) -> ClientValueCollection[ComplianceManagementPartnerAssignment]:
        """Gets the macOsEnrollmentAssignments property"""
        from office365.intune.devices.compliance.management_partner_assignment import (
            ComplianceManagementPartnerAssignment,
        )

        return self.properties.get(
            "macOsEnrollmentAssignments",
            ClientValueCollection[ComplianceManagementPartnerAssignment](ComplianceManagementPartnerAssignment),
        )

    @property
    def mac_os_onboarded(self) -> Optional[bool]:
        """Gets the macOsOnboarded property"""
        return self.properties.get("macOsOnboarded", None)

    @property
    def partner_state(self) -> DeviceManagementPartnerTenantState:
        """Gets the partnerState property"""
        from office365.intune.devices.management.partnertenantstate import (
            DeviceManagementPartnerTenantState,
        )

        return self.properties.get("partnerState", DeviceManagementPartnerTenantState.unknown)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ComplianceManagementPartner"
