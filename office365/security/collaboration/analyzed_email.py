from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.security.antispam_directionality import (
        AntispamDirectionality,
    )
    from office365.security.collaboration.analyzed_email_attachment import (
        AnalyzedEmailAttachment,
    )
    from office365.security.collaboration.analyzed_email_authentication_detail import (
        AnalyzedEmailAuthenticationDetail,
    )
    from office365.security.collaboration.analyzed_email_delivery_detail import (
        AnalyzedEmailDeliveryDetail,
    )
    from office365.security.collaboration.analyzed_email_dlp_rule_info import (
        AnalyzedEmailDlpRuleInfo,
    )
    from office365.security.collaboration.analyzed_email_exchange_transport_rule_info import (
        AnalyzedEmailExchangeTransportRuleInfo,
    )
    from office365.security.collaboration.analyzed_email_recipient_detail import (
        AnalyzedEmailRecipientDetail,
    )
    from office365.security.collaboration.analyzed_email_sender_detail import (
        AnalyzedEmailSenderDetail,
    )
    from office365.security.collaboration.analyzed_email_url import (
        AnalyzedEmailUrl,
    )
    from office365.security.threat_detection_detail import (
        ThreatDetectionDetail,
    )
    from office365.security.threat_type import ThreatType
    from office365.security.timeline_event import TimelineEvent


class AnalyzedEmail(Entity):
    @property
    def alert_ids(self) -> StringCollection:
        """Gets the alertIds property"""
        return self.properties.get("alertIds", StringCollection(None))

    @property
    def bulk_complaint_level(self) -> Optional[str]:
        """Gets the bulkComplaintLevel property"""
        return self.properties.get("bulkComplaintLevel", None)

    @property
    def client_type(self) -> Optional[str]:
        """Gets the clientType property"""
        return self.properties.get("clientType", None)

    @property
    def contexts(self) -> StringCollection:
        """Gets the contexts property"""
        return self.properties.get("contexts", StringCollection(None))

    @property
    def detection_methods(self) -> StringCollection:
        """Gets the detectionMethods property"""
        return self.properties.get("detectionMethods", StringCollection(None))

    @property
    def distribution_list(self) -> Optional[str]:
        """Gets the distributionList property"""
        return self.properties.get("distributionList", None)

    @property
    def email_cluster_id(self) -> Optional[str]:
        """Gets the emailClusterId property"""
        return self.properties.get("emailClusterId", None)

    @property
    def forwarding_detail(self) -> Optional[str]:
        """Gets the forwardingDetail property"""
        return self.properties.get("forwardingDetail", None)

    @property
    def inbound_connector_formatted_name(self) -> Optional[str]:
        """Gets the inboundConnectorFormattedName property"""
        return self.properties.get("inboundConnectorFormattedName", None)

    @property
    def internet_message_id(self) -> Optional[str]:
        """Gets the internetMessageId property"""
        return self.properties.get("internetMessageId", None)

    @property
    def language(self) -> Optional[str]:
        """Gets the language property"""
        return self.properties.get("language", None)

    @property
    def logged_date_time(self) -> Optional[datetime]:
        """Gets the loggedDateTime property"""
        return self.properties.get("loggedDateTime", datetime.min)

    @property
    def network_message_id(self) -> Optional[str]:
        """Gets the networkMessageId property"""
        return self.properties.get("networkMessageId", None)

    @property
    def override_sources(self) -> StringCollection:
        """Gets the overrideSources property"""
        return self.properties.get("overrideSources", StringCollection(None))

    @property
    def phish_confidence_level(self) -> Optional[str]:
        """Gets the phishConfidenceLevel property"""
        return self.properties.get("phishConfidenceLevel", None)

    @property
    def policy(self) -> Optional[str]:
        """Gets the policy property"""
        return self.properties.get("policy", None)

    @property
    def policy_action(self) -> Optional[str]:
        """Gets the policyAction property"""
        return self.properties.get("policyAction", None)

    @property
    def policy_type(self) -> Optional[str]:
        """Gets the policyType property"""
        return self.properties.get("policyType", None)

    @property
    def primary_override_source(self) -> Optional[str]:
        """Gets the primaryOverrideSource property"""
        return self.properties.get("primaryOverrideSource", None)

    @property
    def recipient_email_address(self) -> Optional[str]:
        """Gets the recipientEmailAddress property"""
        return self.properties.get("recipientEmailAddress", None)

    @property
    def return_path(self) -> Optional[str]:
        """Gets the returnPath property"""
        return self.properties.get("returnPath", None)

    @property
    def size_in_bytes(self) -> Optional[int]:
        """Gets the sizeInBytes property"""
        return self.properties.get("sizeInBytes", None)

    @property
    def spam_confidence_level(self) -> Optional[str]:
        """Gets the spamConfidenceLevel property"""
        return self.properties.get("spamConfidenceLevel", None)

    @property
    def subject(self) -> Optional[str]:
        """Gets the subject property"""
        return self.properties.get("subject", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AnalyzedEmail"

    @property
    def attachments(self) -> ClientValueCollection[AnalyzedEmailAttachment]:
        """Gets the attachments property"""
        from office365.security.collaboration.analyzed_email_attachment import (
            AnalyzedEmailAttachment,
        )

        return self.properties.get(
            "attachments", ClientValueCollection[AnalyzedEmailAttachment](AnalyzedEmailAttachment)
        )

    @property
    def authentication_details(self) -> AnalyzedEmailAuthenticationDetail:
        """Gets the authenticationDetails property"""
        from office365.security.collaboration.analyzed_email_authentication_detail import (
            AnalyzedEmailAuthenticationDetail,
        )

        return self.properties.get("authenticationDetails", AnalyzedEmailAuthenticationDetail())

    @property
    def directionality(self) -> AntispamDirectionality:
        """Gets the directionality property"""
        from office365.security.antispam_directionality import (
            AntispamDirectionality,
        )

        return self.properties.get("directionality", AntispamDirectionality.unknown)

    @property
    def dlp_rules(self) -> ClientValueCollection[AnalyzedEmailDlpRuleInfo]:
        """Gets the dlpRules property"""
        from office365.security.collaboration.analyzed_email_dlp_rule_info import (
            AnalyzedEmailDlpRuleInfo,
        )

        return self.properties.get("dlpRules", ClientValueCollection[AnalyzedEmailDlpRuleInfo](AnalyzedEmailDlpRuleInfo))

    @property
    def exchange_transport_rules(self) -> ClientValueCollection[AnalyzedEmailExchangeTransportRuleInfo]:
        """Gets the exchangeTransportRules property"""
        from office365.security.collaboration.analyzed_email_exchange_transport_rule_info import (
            AnalyzedEmailExchangeTransportRuleInfo,
        )

        return self.properties.get(
            "exchangeTransportRules",
            ClientValueCollection[AnalyzedEmailExchangeTransportRuleInfo](AnalyzedEmailExchangeTransportRuleInfo),
        )

    @property
    def latest_delivery(self) -> AnalyzedEmailDeliveryDetail:
        """Gets the latestDelivery property"""
        from office365.security.collaboration.analyzed_email_delivery_detail import (
            AnalyzedEmailDeliveryDetail,
        )

        return self.properties.get("latestDelivery", AnalyzedEmailDeliveryDetail())

    @property
    def original_delivery(self) -> AnalyzedEmailDeliveryDetail:
        """Gets the originalDelivery property"""
        from office365.security.collaboration.analyzed_email_delivery_detail import (
            AnalyzedEmailDeliveryDetail,
        )

        return self.properties.get("originalDelivery", AnalyzedEmailDeliveryDetail())

    @property
    def recipient_detail(self) -> AnalyzedEmailRecipientDetail:
        """Gets the recipientDetail property"""
        from office365.security.collaboration.analyzed_email_recipient_detail import (
            AnalyzedEmailRecipientDetail,
        )

        return self.properties.get("recipientDetail", AnalyzedEmailRecipientDetail())

    @property
    def sender_detail(self) -> AnalyzedEmailSenderDetail:
        """Gets the senderDetail property"""
        from office365.security.collaboration.analyzed_email_sender_detail import (
            AnalyzedEmailSenderDetail,
        )

        return self.properties.get("senderDetail", AnalyzedEmailSenderDetail())

    @property
    def threat_detection_details(self) -> ClientValueCollection[ThreatDetectionDetail]:
        """Gets the threatDetectionDetails property"""
        from office365.security.threat_detection_detail import (
            ThreatDetectionDetail,
        )

        return self.properties.get(
            "threatDetectionDetails", ClientValueCollection[ThreatDetectionDetail](ThreatDetectionDetail)
        )

    @property
    def threat_types(self) -> ClientValueCollection[ThreatType]:
        """Gets the threatTypes property"""
        from office365.security.threat_type import ThreatType

        return self.properties.get("threatTypes", ClientValueCollection[ThreatType](ThreatType))

    @property
    def timeline_events(self) -> ClientValueCollection[TimelineEvent]:
        """Gets the timelineEvents property"""
        from office365.security.timeline_event import TimelineEvent

        return self.properties.get("timelineEvents", ClientValueCollection[TimelineEvent](TimelineEvent))

    @property
    def urls(self) -> ClientValueCollection[AnalyzedEmailUrl]:
        """Gets the urls property"""
        from office365.security.collaboration.analyzed_email_url import (
            AnalyzedEmailUrl,
        )

        return self.properties.get("urls", ClientValueCollection[AnalyzedEmailUrl](AnalyzedEmailUrl))
