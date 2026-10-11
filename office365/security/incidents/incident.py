from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata
from office365.security.alerts.alert import Alert
from office365.security.alerts.comment import AlertComment

if TYPE_CHECKING:
    from office365.security.alerts.determination import AlertDetermination
    from office365.security.alerts.severity import AlertSeverity
    from office365.security.incidents.status import IncidentStatus


class Incident(Entity):
    """
    An incident in Microsoft 365 Defender is a collection of correlated alert instances and associated metadata
    that reflects the story of an attack in a tenant.

    Microsoft 365 services and apps create alerts when they detect a suspicious or malicious event or activity.
    Individual alerts provide valuable clues about a completed or ongoing attack. However, attacks typically employ
    various techniques against different types of entities, such as devices, users, and mailboxes. The result is
    multiple alerts for multiple entities in your tenant. Because piecing the individual alerts together to gain
    insight into an attack can be challenging and time-consuming, Microsoft 365 Defender automatically aggregates the
    alerts and their associated information into an incident.
    """

    @property
    def assigned_to(self) -> Optional[str]:
        """Owner of the incident, or null if no owner is assigned. Free editable text."""
        return self.properties.get("assignedTo", None)

    @property
    def classification(self) -> Optional[str]:
        """The specification for the incident.
        Possible values are: unknown, falsePositive, truePositive, informationalExpectedActivity, unknownFutureValue.
        """
        return self.properties.get("classification", None)

    @property
    def comments(self):
        """Array of comments created by the Security Operations (SecOps) team when the incident is managed."""
        return self.properties.get("comments", ClientValueCollection(AlertComment))

    @odata(name="createdDateTime")
    @property
    def created_datetime(self) -> datetime:
        """Time when the incident was first created."""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def alerts(self) -> EntityCollection[Alert]:
        """The list of related alerts. Supports $expand."""
        return self.properties.get(
            "alerts",
            EntityCollection(self.context, Alert, ResourcePath("alerts", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.incident"

    @property
    def custom_tags(self) -> StringCollection:
        """Gets the customTags property"""
        return self.properties.get("customTags", StringCollection())

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def determination(self) -> AlertDetermination:
        """Gets the determination property"""
        from office365.security.alerts.determination import AlertDetermination

        return self.properties.get("determination", AlertDetermination.unknown)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def incident_web_url(self) -> Optional[str]:
        """Gets the incidentWebUrl property"""
        return self.properties.get("incidentWebUrl", None)

    @property
    def last_modified_by(self) -> Optional[str]:
        """Gets the lastModifiedBy property"""
        return self.properties.get("lastModifiedBy", None)

    @property
    def last_update_date_time(self) -> Optional[datetime]:
        """Gets the lastUpdateDateTime property"""
        return self.properties.get("lastUpdateDateTime", datetime.min)

    @property
    def priority_score(self) -> Optional[int]:
        """Gets the priorityScore property"""
        return self.properties.get("priorityScore", None)

    @property
    def redirect_incident_id(self) -> Optional[str]:
        """Gets the redirectIncidentId property"""
        return self.properties.get("redirectIncidentId", None)

    @property
    def resolving_comment(self) -> Optional[str]:
        """Gets the resolvingComment property"""
        return self.properties.get("resolvingComment", None)

    @property
    def severity(self) -> AlertSeverity:
        """Gets the severity property"""
        from office365.security.alerts.severity import AlertSeverity

        return self.properties.get("severity", AlertSeverity.unknown)

    @property
    def status(self) -> IncidentStatus:
        """Gets the status property"""
        from office365.security.incidents.status import IncidentStatus

        return self.properties.get("status", IncidentStatus.active)

    @property
    def summary(self) -> Optional[str]:
        """Gets the summary property"""
        return self.properties.get("summary", None)

    @property
    def system_tags(self) -> StringCollection:
        """Gets the systemTags property"""
        return self.properties.get("systemTags", StringCollection())

    @property
    def tenant_id(self) -> Optional[str]:
        """Gets the tenantId property"""
        return self.properties.get("tenantId", None)
