from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection
from office365.security.healthissues.severity import HealthIssueSeverity
from office365.security.healthissues.status import HealthIssueStatus
from office365.security.healthissues.type import HealthIssueType


class HealthIssue(Entity):
    @property
    def additional_information(self) -> StringCollection:
        """Gets the additionalInformation property"""
        return self.properties.get("additionalInformation", StringCollection(None))

    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def domain_names(self) -> StringCollection:
        """Gets the domainNames property"""
        return self.properties.get("domainNames", StringCollection(None))

    @property
    def health_issue_type(self) -> HealthIssueType:
        """Gets the healthIssueType property"""
        return self.properties.get("healthIssueType", HealthIssueType.sensor)

    @property
    def issue_type_id(self) -> Optional[str]:
        """Gets the issueTypeId property"""
        return self.properties.get("issueTypeId", None)

    @property
    def last_modified_date_time(self) -> datetime:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def recommendations(self) -> StringCollection:
        """Gets the recommendations property"""
        return self.properties.get("recommendations", StringCollection(None))

    @property
    def recommended_action_commands(self) -> StringCollection:
        """Gets the recommendedActionCommands property"""
        return self.properties.get("recommendedActionCommands", StringCollection(None))

    @property
    def sensor_dns_names(self) -> StringCollection:
        """Gets the sensorDNSNames property"""
        return self.properties.get("sensorDNSNames", StringCollection(None))

    @property
    def severity(self) -> HealthIssueSeverity:
        """Gets the severity property"""
        return self.properties.get("severity", HealthIssueSeverity.low)

    @property
    def status(self) -> HealthIssueStatus:
        """Gets the status property"""
        return self.properties.get("status", HealthIssueStatus.open)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.HealthIssue"
