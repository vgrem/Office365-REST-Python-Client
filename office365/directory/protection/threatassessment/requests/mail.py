from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.directory.protection.threatassessment.requests.request import (
    ThreatAssessmentRequest,
)

if TYPE_CHECKING:
    from office365.directory.protection.threatassessment.requests.maildestinationroutingreason import (
        MailDestinationRoutingReason,
    )


class MailAssessmentRequest(ThreatAssessmentRequest):
    """
    Used to create and retrieve a mail threat assessment, derived from threatAssessmentRequest.

    When you create a mail threat assessment request, the mail should be received by the user specified
    in recipientEmail. Delegated Mail permissions (Mail.Read or Mail.Read.Shared) are requried to access the mail
    received by the user or shared by someone else.
    """

    @property
    def destination_routing_reason(self) -> MailDestinationRoutingReason:
        """Gets the destinationRoutingReason property"""
        from office365.directory.protection.threatassessment.requests.maildestinationroutingreason import (
            MailDestinationRoutingReason,
        )

        return self.properties.get("destinationRoutingReason", MailDestinationRoutingReason.none)

    @property
    def message_uri(self) -> Optional[str]:
        """Gets the messageUri property"""
        return self.properties.get("messageUri", None)

    @property
    def recipient_email(self) -> Optional[str]:
        """Gets the recipientEmail property"""
        return self.properties.get("recipientEmail", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MailAssessmentRequest"
