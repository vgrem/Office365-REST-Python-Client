from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.protection.threatassessment.requests.request import (
    ThreatAssessmentRequest,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.create_entity import CreateEntityQuery

if TYPE_CHECKING:
    from office365.directory.protection.bitlocker import Bitlocker


class InformationProtection(Entity):
    """Exposes methods that you can use to get Microsoft Purview Information Protection labels and label policies."""

    def create_email_file_assessment(self, recipient_email, content_data, expected_assessment, category):
        """Create an email assessment request

        Args:
            recipient_email (str): The mail recipient whose policies are used to assess the mail.
            content_data (str): Base64 encoded file content. The file content can't fetch back because it isn't stored.
            expected_assessment (str): The expected assessment from submitter. Possible values are: block, unblock.
            category (str): The threat category. Possible values are: spam, phishing, malware.
        """

        from office365.directory.protection.threatassessment.requests.email_file import (
            EmailFileAssessmentRequest,
        )

        return_type = EmailFileAssessmentRequest(self.context)
        return_type.set_property("recipientEmail", recipient_email)
        return_type.set_property("contentData", content_data)
        return_type.set_property("expectedAssessment", expected_assessment)
        return_type.set_property("category", category)
        self.threat_assessment_requests.add_child(return_type)
        qry = CreateEntityQuery(self.threat_assessment_requests, return_type, return_type)
        self.context.add_query(qry)
        return return_type

    def create_file_assessment(self, file_name, content_data, expected_assessment, category):
        """Create a new threat assessment request.

        Args:
            file_name (str): File name
            content_data (str): Base64 encoded file content. The file content can't fetch back because it isn't stored.
            expected_assessment (str): The expected assessment from submitter. Possible values are: block, unblock.
            category (str): The threat category. Possible values are: spam, phishing, malware.
        """

        from office365.directory.protection.threatassessment.requests.file import (
            FileAssessmentRequest,
        )

        return_type = FileAssessmentRequest(self.context)
        return_type.set_property("fileName", file_name)
        return_type.set_property("contentData", content_data)
        return_type.set_property("expectedAssessment", expected_assessment)
        return_type.set_property("category", category)
        self.threat_assessment_requests.add_child(return_type)
        qry = CreateEntityQuery(self.threat_assessment_requests, return_type, return_type)
        self.context.add_query(qry)
        return return_type

    def create_url_assessment(self, url, expected_assessment, category):
        """Create a new threat assessment request."""
        from office365.directory.protection.threatassessment.requests.url import (
            UrlAssessmentRequest,
        )

        return_type = UrlAssessmentRequest(self.context)
        return_type.set_property("url", url)
        return_type.set_property("expectedAssessment", expected_assessment)
        return_type.set_property("category", category)
        self.threat_assessment_requests.add_child(return_type)
        qry = CreateEntityQuery(self.threat_assessment_requests, return_type, return_type)
        self.context.add_query(qry)
        return return_type

    def create_mail_assessment(self, message, recipient=None, expected_assessment="block", category="spam"):
        """Create a mail assessment request

        Args:
            recipient (str): Recipient email
            message (office365.outlook.mail.messages.message.Message): Message object or identifier
            expected_assessment (str):
            category (str):
        """

        from office365.directory.protection.threatassessment.requests.mail import (
            MailAssessmentRequest,
        )

        return_type = MailAssessmentRequest(self.context)
        self.threat_assessment_requests.add_child(return_type)

        def _construct_request(request: RequestOptions) -> None:
            request.set_header("Content-Type", "application/json")

        def _create_and_add_query():
            return_type.set_property("recipientEmail", str(message.to_recipients[0].emailAddress))
            return_type.set_property("expectedAssessment", expected_assessment)
            return_type.set_property("category", category)
            return_type.set_property("message", message.resource_url)
            qry = CreateEntityQuery(self.threat_assessment_requests, return_type, return_type)
            self.context.add_query(qry).before_execute(_construct_request)

        message.ensure_properties(["id", "toRecipients"]).after_execute(lambda _: _create_and_add_query())
        return return_type

    @property
    def threat_assessment_requests(self) -> EntityCollection[ThreatAssessmentRequest]:
        """"""
        return self.properties.get(
            "threatAssessmentRequests",
            EntityCollection(
                self.context,
                ThreatAssessmentRequest,
                ResourcePath("threatAssessmentRequests", self.resource_path),
            ),
        )

    @property
    def bitlocker(self) -> Bitlocker:
        """Gets the bitlocker property"""
        from office365.directory.protection.bitlocker import Bitlocker

        return self.properties.get("bitlocker", Bitlocker(self.context, ResourcePath("bitlocker", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.InformationProtection"
