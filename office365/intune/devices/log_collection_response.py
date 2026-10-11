from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.apploguploadstate import AppLogUploadState


class DeviceLogCollectionResponse(Entity):
    @property
    def enrolled_by_user(self) -> Optional[str]:
        """Gets the enrolledByUser property"""
        return self.properties.get("enrolledByUser", None)

    @property
    def expiration_date_time_utc(self) -> Optional[datetime]:
        """Gets the expirationDateTimeUTC property"""
        return self.properties.get("expirationDateTimeUTC", datetime.min)

    @property
    def initiated_by_user_principal_name(self) -> Optional[str]:
        """Gets the initiatedByUserPrincipalName property"""
        return self.properties.get("initiatedByUserPrincipalName", None)

    @property
    def managed_device_id(self) -> Optional[UUID]:
        """Gets the managedDeviceId property"""
        return self.properties.get("managedDeviceId", None)

    @property
    def received_date_time_utc(self) -> Optional[datetime]:
        """Gets the receivedDateTimeUTC property"""
        return self.properties.get("receivedDateTimeUTC", datetime.min)

    @property
    def requested_date_time_utc(self) -> Optional[datetime]:
        """Gets the requestedDateTimeUTC property"""
        return self.properties.get("requestedDateTimeUTC", datetime.min)

    @property
    def size_in_kb(self) -> Optional[float]:
        """Gets the sizeInKB property"""
        return self.properties.get("sizeInKB", None)

    @property
    def status(self) -> AppLogUploadState:
        """Gets the status property"""
        from office365.intune.devices.management.apploguploadstate import (
            AppLogUploadState,
        )

        return self.properties.get("status", AppLogUploadState.pending)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceLogCollectionResponse"
