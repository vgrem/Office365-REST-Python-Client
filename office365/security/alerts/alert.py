from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata
from office365.security.alerts.classification import AlertClassification
from office365.security.alerts.comment import AlertComment
from office365.security.alerts.detectionsource import DetectionSource
from office365.security.alerts.determination import AlertDetermination
from office365.security.alerts.evidence import AlertEvidence
from office365.security.alerts.history_state import AlertHistoryState
from office365.security.alerts.severity import AlertSeverity
from office365.security.alerts.status import AlertStatus

if TYPE_CHECKING:
    from office365.security.alerts.detection import AlertDetection
    from office365.security.alerts.feedback import AlertFeedback
    from office365.security.alerts.file_security_state import (
        FileSecurityState,
    )
    from office365.security.alerts.trigger import AlertTrigger
    from office365.security.cloud_app_security_state import (
        CloudAppSecurityState,
    )
    from office365.security.dictionary import Dictionary
    from office365.security.host_security_state import HostSecurityState
    from office365.security.investigation_security_state import (
        InvestigationSecurityState,
    )
    from office365.security.investigation_state import InvestigationState
    from office365.security.malware_state import MalwareState
    from office365.security.message_security_state import MessageSecurityState
    from office365.security.network_connection import NetworkConnection
    from office365.security.process import Process
    from office365.security.registry_key_state import RegistryKeyState
    from office365.security.security_resource import SecurityResource
    from office365.security.security_vendor_information import (
        SecurityVendorInformation,
    )
    from office365.security.service_source import ServiceSource
    from office365.security.uri_click_security_state import (
        UriClickSecurityState,
    )
    from office365.security.user_security_state import UserSecurityState
    from office365.security.vulnerability_state import VulnerabilityState


class Alert(Entity):
    """This resource corresponds to the latest generation of alerts in the Microsoft Graph security API,
    representing potential security issues within a customer's tenant that Microsoft 365 Defender,
    or a security provider integrated with Microsoft 365 Defender, has identified."""

    def __str__(self) -> str:
        return f"[{self.severity.name}] [{self.status.name}] {self.title or self.entity_type_name}"

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(id={self.id!r}, "
            f"title={self.title!r}, severity={self.severity.name}, status={self.status.name})"
        )

    @property
    def activity_group_name(self) -> Optional[str]:
        """"""
        return self.properties.get("activityGroupName", None)

    @property
    def actor_display_name(self) -> Optional[str]:
        """The adversary or activity group that is associated with this alert."""
        return self.properties.get("actorDisplayName", None)

    @property
    def alert_policy_id(self) -> Optional[str]:
        return self.properties.get("alertPolicyId", None)

    @property
    def evidence(self):
        """Collection of evidence related to the alert."""
        return self.properties.get("evidence", ClientValueCollection(AlertEvidence))

    @odata(name="historyStates")
    @property
    def history_states(self):
        """Collection of changes for the alert."""
        return self.properties.get("historyStates", ClientValueCollection(AlertHistoryState))

    @property
    def alert_web_url(self) -> Optional[str]:
        """Gets the alertWebUrl property"""
        return self.properties.get("alertWebUrl", None)

    @property
    def assigned_to(self) -> Optional[str]:
        """Gets the assignedTo property"""
        return self.properties.get("assignedTo", None)

    @property
    def categories(self) -> StringCollection:
        """Gets the categories property"""
        return self.properties.get("categories", StringCollection(None))

    @property
    def category(self) -> Optional[str]:
        """Gets the category property"""
        return self.properties.get("category", None)

    @property
    def classification(self) -> AlertClassification:
        """Gets the classification property"""
        return self.properties.get("classification", AlertClassification.unknown)

    @property
    def comments(self) -> ClientValueCollection[AlertComment]:
        """Gets the comments property"""
        return self.properties.get("comments", ClientValueCollection[AlertComment](AlertComment))

    @odata(name="createdDateTime")
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @odata(name="detectionSource")
    @property
    def detection_source(self) -> DetectionSource:
        """Gets the detectionSource property"""
        return self.properties.get("detectionSource", DetectionSource.unknown)

    @property
    def detector_id(self) -> Optional[str]:
        """Gets the detectorId property"""
        return self.properties.get("detectorId", None)

    @property
    def determination(self) -> AlertDetermination:
        """Gets the determination property"""
        return self.properties.get("determination", AlertDetermination.unknown)

    @odata(name="firstActivityDateTime")
    @property
    def first_activity_date_time(self) -> Optional[datetime]:
        """Gets the firstActivityDateTime property"""
        return self.properties.get("firstActivityDateTime", datetime.min)

    @property
    def incident_id(self) -> Optional[str]:
        """Gets the incidentId property"""
        return self.properties.get("incidentId", None)

    @property
    def incident_web_url(self) -> Optional[str]:
        """Gets the incidentWebUrl property"""
        return self.properties.get("incidentWebUrl", None)

    @odata(name="lastActivityDateTime")
    @property
    def last_activity_date_time(self) -> Optional[datetime]:
        """Gets the lastActivityDateTime property"""
        return self.properties.get("lastActivityDateTime", datetime.min)

    @property
    def last_update_date_time(self) -> Optional[datetime]:
        """Gets the lastUpdateDateTime property"""
        return self.properties.get("lastUpdateDateTime", datetime.min)

    @odata(name="mitreTechniques")
    @property
    def mitre_techniques(self) -> StringCollection:
        """Gets the mitreTechniques property"""
        return self.properties.get("mitreTechniques", StringCollection(None))

    @property
    def product_name(self) -> Optional[str]:
        """Gets the productName property"""
        return self.properties.get("productName", None)

    @property
    def provider_alert_id(self) -> Optional[str]:
        """Gets the providerAlertId property"""
        return self.properties.get("providerAlertId", None)

    @property
    def recommended_actions(self) -> Optional[str]:
        """Gets the recommendedActions property"""
        return self.properties.get("recommendedActions", None)

    @odata(name="resolvedDateTime")
    @property
    def resolved_date_time(self) -> Optional[datetime]:
        """Gets the resolvedDateTime property"""
        return self.properties.get("resolvedDateTime", datetime.min)

    @property
    def severity(self) -> AlertSeverity:
        """Gets the severity property"""
        return self.properties.get("severity", AlertSeverity.unknown)

    @property
    def status(self) -> AlertStatus:
        """Gets the status property"""
        return self.properties.get("status", AlertStatus.unknown)

    @property
    def system_tags(self) -> StringCollection:
        """Gets the systemTags property"""
        return self.properties.get("systemTags", StringCollection())

    @property
    def tenant_id(self) -> Optional[str]:
        """Gets the tenantId property"""
        return self.properties.get("tenantId", None)

    @property
    def threat_display_name(self) -> Optional[str]:
        """Gets the threatDisplayName property"""
        return self.properties.get("threatDisplayName", None)

    @property
    def threat_family_name(self) -> Optional[str]:
        """Gets the threatFamilyName property"""
        return self.properties.get("threatFamilyName", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the title property"""
        return self.properties.get("title", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.Alert"

    @property
    def additional_data(self) -> Dictionary:
        """Gets the additionalData property"""
        from office365.security.dictionary import Dictionary

        return self.properties.get("additionalData", Dictionary())

    @property
    def custom_details(self) -> Dictionary:
        """Gets the customDetails property"""
        from office365.security.dictionary import Dictionary

        return self.properties.get("customDetails", Dictionary())

    @property
    def investigation_state(self) -> InvestigationState:
        """Gets the investigationState property"""
        from office365.security.investigation_state import InvestigationState

        return self.properties.get("investigationState", InvestigationState.unknown)

    @property
    def service_source(self) -> ServiceSource:
        """Gets the serviceSource property"""
        from office365.security.service_source import ServiceSource

        return self.properties.get("serviceSource", ServiceSource.unknown)

    @property
    def alert_detections(self) -> ClientValueCollection[AlertDetection]:
        """Gets the alertDetections property"""
        from office365.security.alerts.detection import AlertDetection

        return self.properties.get("alertDetections", ClientValueCollection[AlertDetection](AlertDetection))

    @property
    def azure_subscription_id(self) -> Optional[str]:
        """Gets the azureSubscriptionId property"""
        return self.properties.get("azureSubscriptionId", None)

    @property
    def azure_tenant_id(self) -> Optional[str]:
        """Gets the azureTenantId property"""
        return self.properties.get("azureTenantId", None)

    @property
    def closed_date_time(self) -> Optional[datetime]:
        """Gets the closedDateTime property"""
        return self.properties.get("closedDateTime", datetime.min)

    @property
    def cloud_app_states(self) -> ClientValueCollection[CloudAppSecurityState]:
        """Gets the cloudAppStates property"""
        from office365.security.cloud_app_security_state import (
            CloudAppSecurityState,
        )

        return self.properties.get("cloudAppStates", ClientValueCollection[CloudAppSecurityState](CloudAppSecurityState))

    @property
    def confidence(self) -> Optional[int]:
        """Gets the confidence property"""
        return self.properties.get("confidence", None)

    @property
    def detection_ids(self) -> StringCollection:
        """Gets the detectionIds property"""
        return self.properties.get("detectionIds", StringCollection())

    @property
    def event_date_time(self) -> Optional[datetime]:
        """Gets the eventDateTime property"""
        return self.properties.get("eventDateTime", datetime.min)

    @property
    def feedback(self) -> AlertFeedback:
        """Gets the feedback property"""
        from office365.security.alerts.feedback import AlertFeedback

        return self.properties.get("feedback", AlertFeedback.unknown)

    @property
    def file_states(self) -> ClientValueCollection[FileSecurityState]:
        """Gets the fileStates property"""
        from office365.security.alerts.file_security_state import (
            FileSecurityState,
        )

        return self.properties.get("fileStates", ClientValueCollection[FileSecurityState](FileSecurityState))

    @property
    def host_states(self) -> ClientValueCollection[HostSecurityState]:
        """Gets the hostStates property"""
        from office365.security.host_security_state import HostSecurityState

        return self.properties.get("hostStates", ClientValueCollection[HostSecurityState](HostSecurityState))

    @property
    def incident_ids(self) -> StringCollection:
        """Gets the incidentIds property"""
        return self.properties.get("incidentIds", StringCollection())

    @property
    def investigation_security_states(self) -> ClientValueCollection[InvestigationSecurityState]:
        """Gets the investigationSecurityStates property"""
        from office365.security.investigation_security_state import (
            InvestigationSecurityState,
        )

        return self.properties.get(
            "investigationSecurityStates", ClientValueCollection[InvestigationSecurityState](InvestigationSecurityState)
        )

    @property
    def last_event_date_time(self) -> Optional[datetime]:
        """Gets the lastEventDateTime property"""
        return self.properties.get("lastEventDateTime", datetime.min)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def malware_states(self) -> ClientValueCollection[MalwareState]:
        """Gets the malwareStates property"""
        from office365.security.malware_state import MalwareState

        return self.properties.get("malwareStates", ClientValueCollection[MalwareState](MalwareState))

    @property
    def message_security_states(self) -> ClientValueCollection[MessageSecurityState]:
        """Gets the messageSecurityStates property"""
        from office365.security.message_security_state import (
            MessageSecurityState,
        )

        return self.properties.get(
            "messageSecurityStates", ClientValueCollection[MessageSecurityState](MessageSecurityState)
        )

    @property
    def network_connections(self) -> ClientValueCollection[NetworkConnection]:
        """Gets the networkConnections property"""
        from office365.security.network_connection import NetworkConnection

        return self.properties.get("networkConnections", ClientValueCollection[NetworkConnection](NetworkConnection))

    @property
    def processes(self) -> ClientValueCollection[Process]:
        """Gets the processes property"""
        from office365.security.process import Process

        return self.properties.get("processes", ClientValueCollection[Process](Process))

    @property
    def registry_key_states(self) -> ClientValueCollection[RegistryKeyState]:
        """Gets the registryKeyStates property"""
        from office365.security.registry_key_state import RegistryKeyState

        return self.properties.get("registryKeyStates", ClientValueCollection[RegistryKeyState](RegistryKeyState))

    @property
    def security_resources(self) -> ClientValueCollection[SecurityResource]:
        """Gets the securityResources property"""
        from office365.security.security_resource import SecurityResource

        return self.properties.get("securityResources", ClientValueCollection[SecurityResource](SecurityResource))

    @property
    def source_materials(self) -> StringCollection:
        """Gets the sourceMaterials property"""
        return self.properties.get("sourceMaterials", StringCollection())

    @property
    def tags(self) -> StringCollection:
        """Gets the tags property"""
        return self.properties.get("tags", StringCollection())

    @property
    def triggers(self) -> ClientValueCollection[AlertTrigger]:
        """Gets the triggers property"""
        from office365.security.alerts.trigger import AlertTrigger

        return self.properties.get("triggers", ClientValueCollection[AlertTrigger](AlertTrigger))

    @property
    def uri_click_security_states(self) -> ClientValueCollection[UriClickSecurityState]:
        """Gets the uriClickSecurityStates property"""
        from office365.security.uri_click_security_state import (
            UriClickSecurityState,
        )

        return self.properties.get(
            "uriClickSecurityStates", ClientValueCollection[UriClickSecurityState](UriClickSecurityState)
        )

    @property
    def user_states(self) -> ClientValueCollection[UserSecurityState]:
        """Gets the userStates property"""
        from office365.security.user_security_state import UserSecurityState

        return self.properties.get("userStates", ClientValueCollection[UserSecurityState](UserSecurityState))

    @property
    def vendor_information(self) -> SecurityVendorInformation:
        """Gets the vendorInformation property"""
        from office365.security.security_vendor_information import (
            SecurityVendorInformation,
        )

        return self.properties.get("vendorInformation", SecurityVendorInformation())

    @property
    def vulnerability_states(self) -> ClientValueCollection[VulnerabilityState]:
        """Gets the vulnerabilityStates property"""
        from office365.security.vulnerability_state import VulnerabilityState

        return self.properties.get("vulnerabilityStates", ClientValueCollection[VulnerabilityState](VulnerabilityState))
