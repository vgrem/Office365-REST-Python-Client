from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue
from office365.security.alerts.googlecloudlocationtype import GoogleCloudLocationType


@dataclass
class GoogleCloudResourceEvidence(ClientValue):
    fullResourceName: str | None = None
    location: str | None = None
    locationType: GoogleCloudLocationType = GoogleCloudLocationType.unknown
    projectId: str | None = None
    projectNumber: int | None = None
    resourceName: str | None = None
    resourceType: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.GoogleCloudResourceEvidence"
