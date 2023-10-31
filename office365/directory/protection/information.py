from office365.directory.protection.threatassessment.request import (
    ThreatAssessmentRequest,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.create_entity import CreateEntityQuery


class InformationProtection(Entity):
    """Exposes methods that you can use to get Microsoft Purview Information Protection labels and label policies."""

    def create_mail_assessment(
        self, message, recipient=None, expected_assessment="block", category="spam"
    ):
        """
        Create a mail assessment request
        :param str recipient: Recipient email
        :param office365.outlook.mail.messages.message.Message message: Message object or identifier
        :param str expected_assessment:
        :param str category:
        """

        from office365.directory.protection.threatassessment.mail_request import (
            MailAssessmentRequest,
        )

        return_type = MailAssessmentRequest(self.context)
        self.threat_assessment_requests.add_child(return_type)

        def _construct_request(request):
            # type: (RequestOptions) -> None
            request.set_header("Content-Type", "application/json")

        def _create_and_add_query():
            return_type.set_property(
                "recipientEmail", str(message.to_recipients[0].emailAddress)
            )
            return_type.set_property("expectedAssessment", expected_assessment)
            return_type.set_property("category", category)
            return_type.set_property("message", message.resource_url)
            qry = CreateEntityQuery(
                self.threat_assessment_requests, return_type, return_type
            )
            self.context.add_query(qry).before_query_execute(_construct_request)

        message.ensure_properties(["id", "toRecipients"], _create_and_add_query)
        return return_type

    @property
    def threat_assessment_requests(self):
        # type: () -> EntityCollection[ThreatAssessmentRequest]
        """"""
        return self.properties.get(
            "threatAssessmentRequests",
            EntityCollection(
                self.context,
                ThreatAssessmentRequest,
                ResourcePath("threatAssessmentRequests", self.resource_path),
            ),
        )
