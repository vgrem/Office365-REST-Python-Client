from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.intune.devices.compliance.information import ComplianceInformation
    from office365.security.securescores.control_state_update import (
        SecureScoreControlStateUpdate,
    )
    from office365.security.security_vendor_information import (
        SecurityVendorInformation,
    )


class SecureScoreControlProfile(Entity):
    """Represents a tenant's secure score per control data. By default, it returns all controls
    for a tenant and can explicitly pull individual controls."""

    @property
    def action_type(self) -> Optional[str]:
        """Control action type (Config, Review, Behavior)."""
        return self.properties.get("actionType", None)

    @property
    def action_url(self) -> Optional[str]:
        """URL to where the control can be actioned."""
        return self.properties.get("actionUrl", None)

    @property
    def azure_tenant_id(self) -> Optional[str]:
        """GUID string for tenant ID."""
        return self.properties.get("azureTenantId", None)

    @property
    def compliance_information(self) -> ClientValueCollection[ComplianceInformation]:
        """Gets the complianceInformation property"""
        from office365.intune.devices.compliance.information import ComplianceInformation

        return self.properties.get(
            "complianceInformation", ClientValueCollection[ComplianceInformation](ComplianceInformation)
        )

    @property
    def control_category(self) -> Optional[str]:
        """Gets the controlCategory property"""
        return self.properties.get("controlCategory", None)

    @property
    def control_state_updates(self) -> ClientValueCollection[SecureScoreControlStateUpdate]:
        """Gets the controlStateUpdates property"""
        from office365.security.securescores.control_state_update import (
            SecureScoreControlStateUpdate,
        )

        return self.properties.get(
            "controlStateUpdates", ClientValueCollection[SecureScoreControlStateUpdate](SecureScoreControlStateUpdate)
        )

    @property
    def deprecated(self) -> Optional[bool]:
        """Gets the deprecated property"""
        return self.properties.get("deprecated", None)

    @property
    def implementation_cost(self) -> Optional[str]:
        """Gets the implementationCost property"""
        return self.properties.get("implementationCost", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def max_score(self) -> Optional[float]:
        """Gets the maxScore property"""
        return self.properties.get("maxScore", None)

    @property
    def rank(self) -> Optional[int]:
        """Gets the rank property"""
        return self.properties.get("rank", None)

    @property
    def remediation(self) -> Optional[str]:
        """Gets the remediation property"""
        return self.properties.get("remediation", None)

    @property
    def remediation_impact(self) -> Optional[str]:
        """Gets the remediationImpact property"""
        return self.properties.get("remediationImpact", None)

    @property
    def service(self) -> Optional[str]:
        """Gets the service property"""
        return self.properties.get("service", None)

    @property
    def threats(self) -> StringCollection:
        """Gets the threats property"""
        return self.properties.get("threats", StringCollection())

    @property
    def tier(self) -> Optional[str]:
        """Gets the tier property"""
        return self.properties.get("tier", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the title property"""
        return self.properties.get("title", None)

    @property
    def user_impact(self) -> Optional[str]:
        """Gets the userImpact property"""
        return self.properties.get("userImpact", None)

    @property
    def vendor_information(self) -> SecurityVendorInformation:
        """Gets the vendorInformation property"""
        from office365.security.security_vendor_information import (
            SecurityVendorInformation,
        )

        return self.properties.get("vendorInformation", SecurityVendorInformation())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SecureScoreControlProfile"
