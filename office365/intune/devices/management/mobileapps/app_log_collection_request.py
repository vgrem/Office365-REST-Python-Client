from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.intune.devices.management.apploguploadstate import AppLogUploadState


class AppLogCollectionRequest(Entity):
    @property
    def completed_date_time(self) -> Optional[datetime]:
        """Gets the completedDateTime property"""
        return self.properties.get("completedDateTime", datetime.min)

    @property
    def custom_log_folders(self) -> StringCollection:
        """Gets the customLogFolders property"""
        return self.properties.get("customLogFolders", StringCollection())

    @property
    def error_message(self) -> Optional[str]:
        """Gets the errorMessage property"""
        return self.properties.get("errorMessage", None)

    @property
    def status(self) -> AppLogUploadState:
        """Gets the status property"""
        from office365.intune.devices.management.apploguploadstate import (
            AppLogUploadState,
        )

        return self.properties.get("status", AppLogUploadState.pending)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AppLogCollectionRequest"
