from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from office365.entity import Entity
from office365.intune.audit.actor import AuditActor
from office365.intune.audit.resource import AuditResource
from office365.runtime.client_value_collection import ClientValueCollection


class AuditEvent(Entity):
    """A class containing the properties for Audit Event."""

    @property
    def activity(self) -> Optional[str]:
        """Friendly name of the activity."""
        return self.properties.get("activity", None)

    @property
    def actor(self):
        """AAD user and application that are associated with the audit event."""
        return self.properties.get("actor", AuditActor())

    @property
    def resources(self):
        """Resources being modified"""
        return self.properties.get("resources", ClientValueCollection(AuditResource))

    @property
    def activity_date_time(self) -> Optional[datetime]:
        """Gets the activityDateTime property"""
        return self.properties.get("activityDateTime", datetime.min)

    @property
    def activity_operation_type(self) -> Optional[str]:
        """Gets the activityOperationType property"""
        return self.properties.get("activityOperationType", None)

    @property
    def activity_result(self) -> Optional[str]:
        """Gets the activityResult property"""
        return self.properties.get("activityResult", None)

    @property
    def activity_type(self) -> Optional[str]:
        """Gets the activityType property"""
        return self.properties.get("activityType", None)

    @property
    def category(self) -> Optional[str]:
        """Gets the category property"""
        return self.properties.get("category", None)

    @property
    def component_name(self) -> Optional[str]:
        """Gets the componentName property"""
        return self.properties.get("componentName", None)

    @property
    def correlation_id(self) -> Optional[UUID]:
        """Gets the correlationId property"""
        return self.properties.get("correlationId", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AuditEvent"
