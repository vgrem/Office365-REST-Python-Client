from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.management.managed.windows.defender_product_status import (
        WindowsDefenderProductStatus,
    )
    from office365.intune.devices.management.managed.windows.healthstate import (
        WindowsDeviceHealthState,
    )
    from office365.intune.devices.management.windowsmalware.windows_device_malware_state import (
        WindowsDeviceMalwareState,
    )


class WindowsProtectionState(Entity):
    @property
    def anti_malware_version(self) -> Optional[str]:
        """Gets the antiMalwareVersion property"""
        return self.properties.get("antiMalwareVersion", None)

    @property
    def controlled_configuration_enabled(self) -> Optional[bool]:
        """Gets the controlledConfigurationEnabled property"""
        return self.properties.get("controlledConfigurationEnabled", None)

    @property
    def device_state(self) -> WindowsDeviceHealthState:
        """Gets the deviceState property"""
        from office365.intune.devices.management.managed.windows.healthstate import (
            WindowsDeviceHealthState,
        )

        return self.properties.get("deviceState", WindowsDeviceHealthState.clean)

    @property
    def engine_version(self) -> Optional[str]:
        """Gets the engineVersion property"""
        return self.properties.get("engineVersion", None)

    @property
    def full_scan_overdue(self) -> Optional[bool]:
        """Gets the fullScanOverdue property"""
        return self.properties.get("fullScanOverdue", None)

    @property
    def full_scan_required(self) -> Optional[bool]:
        """Gets the fullScanRequired property"""
        return self.properties.get("fullScanRequired", None)

    @property
    def is_virtual_machine(self) -> Optional[bool]:
        """Gets the isVirtualMachine property"""
        return self.properties.get("isVirtualMachine", None)

    @property
    def last_full_scan_date_time(self) -> Optional[datetime]:
        """Gets the lastFullScanDateTime property"""
        return self.properties.get("lastFullScanDateTime", datetime.min)

    @property
    def last_full_scan_signature_version(self) -> Optional[str]:
        """Gets the lastFullScanSignatureVersion property"""
        return self.properties.get("lastFullScanSignatureVersion", None)

    @property
    def last_quick_scan_date_time(self) -> Optional[datetime]:
        """Gets the lastQuickScanDateTime property"""
        return self.properties.get("lastQuickScanDateTime", datetime.min)

    @property
    def last_quick_scan_signature_version(self) -> Optional[str]:
        """Gets the lastQuickScanSignatureVersion property"""
        return self.properties.get("lastQuickScanSignatureVersion", None)

    @property
    def last_reported_date_time(self) -> Optional[datetime]:
        """Gets the lastReportedDateTime property"""
        return self.properties.get("lastReportedDateTime", datetime.min)

    @property
    def malware_protection_enabled(self) -> Optional[bool]:
        """Gets the malwareProtectionEnabled property"""
        return self.properties.get("malwareProtectionEnabled", None)

    @property
    def network_inspection_system_enabled(self) -> Optional[bool]:
        """Gets the networkInspectionSystemEnabled property"""
        return self.properties.get("networkInspectionSystemEnabled", None)

    @property
    def product_status(self) -> WindowsDefenderProductStatus:
        """Gets the productStatus property"""
        from office365.intune.devices.management.managed.windows.defender_product_status import (
            WindowsDefenderProductStatus,
        )

        return self.properties.get("productStatus", WindowsDefenderProductStatus.noStatus)

    @property
    def quick_scan_overdue(self) -> Optional[bool]:
        """Gets the quickScanOverdue property"""
        return self.properties.get("quickScanOverdue", None)

    @property
    def real_time_protection_enabled(self) -> Optional[bool]:
        """Gets the realTimeProtectionEnabled property"""
        return self.properties.get("realTimeProtectionEnabled", None)

    @property
    def reboot_required(self) -> Optional[bool]:
        """Gets the rebootRequired property"""
        return self.properties.get("rebootRequired", None)

    @property
    def signature_update_overdue(self) -> Optional[bool]:
        """Gets the signatureUpdateOverdue property"""
        return self.properties.get("signatureUpdateOverdue", None)

    @property
    def signature_version(self) -> Optional[str]:
        """Gets the signatureVersion property"""
        return self.properties.get("signatureVersion", None)

    @property
    def tamper_protection_enabled(self) -> Optional[bool]:
        """Gets the tamperProtectionEnabled property"""
        return self.properties.get("tamperProtectionEnabled", None)

    @property
    def detected_malware_state(self) -> EntityCollection[WindowsDeviceMalwareState]:
        """Gets the detectedMalwareState property"""
        from office365.intune.devices.management.windowsmalware.windows_device_malware_state import (
            WindowsDeviceMalwareState,
        )

        return self.properties.get(
            "detectedMalwareState",
            EntityCollection[WindowsDeviceMalwareState](
                self.context, WindowsDeviceMalwareState, ResourcePath("detectedMalwareState", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsProtectionState"
