from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.admin.drift_status import DriftStatus
    from office365.directory.drifted_property import DriftedProperty
    from office365.teams.members.open_complex_dictionary_type import (
        OpenComplexDictionaryType,
    )


class ConfigurationDrift(Entity):
    @property
    def baseline_resource_display_name(self) -> Optional[str]:
        """Gets the baselineResourceDisplayName property"""
        return self.properties.get("baselineResourceDisplayName", None)

    @property
    def drifted_properties(self) -> ClientValueCollection[DriftedProperty]:
        """Gets the driftedProperties property"""
        from office365.directory.drifted_property import DriftedProperty

        return self.properties.get("driftedProperties", ClientValueCollection[DriftedProperty](DriftedProperty))

    @property
    def first_reported_date_time(self) -> Optional[datetime]:
        """Gets the firstReportedDateTime property"""
        return self.properties.get("firstReportedDateTime", datetime.min)

    @property
    def monitor_id(self) -> Optional[str]:
        """Gets the monitorId property"""
        return self.properties.get("monitorId", None)

    @property
    def resource_instance_identifier(self) -> OpenComplexDictionaryType:
        """Gets the resourceInstanceIdentifier property"""
        from office365.teams.members.open_complex_dictionary_type import (
            OpenComplexDictionaryType,
        )

        return self.properties.get("resourceInstanceIdentifier", OpenComplexDictionaryType())

    @property
    def resource_type(self) -> Optional[str]:
        """Gets the resourceType property"""
        return self.properties.get("resourceType", None)

    @property
    def status(self) -> DriftStatus:
        """Gets the status property"""
        from office365.admin.drift_status import DriftStatus

        return self.properties.get("status", DriftStatus.active)

    @property
    def tenant_id(self) -> Optional[str]:
        """Gets the tenantId property"""
        return self.properties.get("tenantId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ConfigurationDrift"
