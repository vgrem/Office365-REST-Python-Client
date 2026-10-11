from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.exportjoblocalizationtype import (
        DeviceManagementExportJobLocalizationType,
    )
    from office365.intune.devices.management.reports.fileformat import (
        DeviceManagementReportFileFormat,
    )
    from office365.intune.devices.management.reports.status import (
        DeviceManagementReportStatus,
    )


class DeviceManagementExportJob(Entity):
    @property
    def expiration_date_time(self) -> Optional[datetime]:
        """Gets the expirationDateTime property"""
        return self.properties.get("expirationDateTime", datetime.min)

    @property
    def filter(self) -> Optional[str]:
        """Gets the filter property"""
        return self.properties.get("filter", None)

    @property
    def format(self) -> DeviceManagementReportFileFormat:
        """Gets the format property"""
        from office365.intune.devices.management.reports.fileformat import (
            DeviceManagementReportFileFormat,
        )

        return self.properties.get("format", DeviceManagementReportFileFormat.csv)

    @property
    def localization_type(self) -> DeviceManagementExportJobLocalizationType:
        """Gets the localizationType property"""
        from office365.intune.devices.management.exportjoblocalizationtype import (
            DeviceManagementExportJobLocalizationType,
        )

        return self.properties.get(
            "localizationType", DeviceManagementExportJobLocalizationType.localizedValuesAsAdditionalColumn
        )

    @property
    def report_name(self) -> Optional[str]:
        """Gets the reportName property"""
        return self.properties.get("reportName", None)

    @property
    def request_date_time(self) -> Optional[datetime]:
        """Gets the requestDateTime property"""
        return self.properties.get("requestDateTime", datetime.min)

    @property
    def snapshot_id(self) -> Optional[str]:
        """Gets the snapshotId property"""
        return self.properties.get("snapshotId", None)

    @property
    def status(self) -> DeviceManagementReportStatus:
        """Gets the status property"""
        from office365.intune.devices.management.reports.status import (
            DeviceManagementReportStatus,
        )

        return self.properties.get("status", DeviceManagementReportStatus.unknown)

    @property
    def url(self) -> Optional[str]:
        """Gets the url property"""
        return self.properties.get("url", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceManagementExportJob"
