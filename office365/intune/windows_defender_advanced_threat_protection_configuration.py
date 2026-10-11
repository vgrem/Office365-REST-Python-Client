from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class WindowsDefenderAdvancedThreatProtectionConfiguration(Entity):
    @property
    def allow_sample_sharing(self) -> Optional[bool]:
        """Gets the allowSampleSharing property"""
        return self.properties.get("allowSampleSharing", None)

    @property
    def enable_expedited_telemetry_reporting(self) -> Optional[bool]:
        """Gets the enableExpeditedTelemetryReporting property"""
        return self.properties.get("enableExpeditedTelemetryReporting", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsDefenderAdvancedThreatProtectionConfiguration"
