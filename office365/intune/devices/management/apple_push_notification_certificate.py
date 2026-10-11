from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity


class ApplePushNotificationCertificate(Entity):
    @property
    def apple_identifier(self) -> Optional[str]:
        """Gets the appleIdentifier property"""
        return self.properties.get("appleIdentifier", None)

    @property
    def certificate(self) -> Optional[str]:
        """Gets the certificate property"""
        return self.properties.get("certificate", None)

    @property
    def certificate_serial_number(self) -> Optional[str]:
        """Gets the certificateSerialNumber property"""
        return self.properties.get("certificateSerialNumber", None)

    @property
    def certificate_upload_failure_reason(self) -> Optional[str]:
        """Gets the certificateUploadFailureReason property"""
        return self.properties.get("certificateUploadFailureReason", None)

    @property
    def certificate_upload_status(self) -> Optional[str]:
        """Gets the certificateUploadStatus property"""
        return self.properties.get("certificateUploadStatus", None)

    @property
    def expiration_date_time(self) -> Optional[datetime]:
        """Gets the expirationDateTime property"""
        return self.properties.get("expirationDateTime", datetime.min)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def topic_identifier(self) -> Optional[str]:
        """Gets the topicIdentifier property"""
        return self.properties.get("topicIdentifier", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ApplePushNotificationCertificate"
