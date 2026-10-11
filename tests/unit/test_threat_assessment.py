"""Offline tests for threat assessment request serialization.

``UrlAssessmentRequest`` must advertise its concrete OData type instead of the
abstract ``threatAssessmentRequest`` it derives from, otherwise Graph rejects
the create call with ``InvalidBody``.
"""

from __future__ import annotations

import unittest

from office365.directory.protection.threatassessment.requests.email_file import EmailFileAssessmentRequest
from office365.directory.protection.threatassessment.requests.file import FileAssessmentRequest
from office365.directory.protection.threatassessment.requests.url import UrlAssessmentRequest
from office365.graph_client import GraphClient
from office365.runtime.odata.v4.json_format import V4JsonFormat


class TestUrlAssessmentRequestType(unittest.TestCase):
    def test_concrete_odata_type(self):
        request = UrlAssessmentRequest(GraphClient())
        self.assertEqual(request.entity_type_name, "microsoft.graph.urlAssessmentRequest")

    def test_serialization_includes_concrete_type(self):
        request = UrlAssessmentRequest(GraphClient())
        request.set_property("url", "http://test-phishing-example.com")
        request.set_property("expectedAssessment", "block")
        request.set_property("category", "phishing")

        payload = request.to_json(V4JsonFormat())

        self.assertEqual(payload["@odata.type"], "#microsoft.graph.urlAssessmentRequest")
        self.assertEqual(payload["url"], "http://test-phishing-example.com")

    def test_subclasses_still_differ(self):
        client = GraphClient()
        self.assertNotEqual(
            UrlAssessmentRequest(client).entity_type_name,
            FileAssessmentRequest(client).entity_type_name,
        )
        self.assertNotEqual(
            UrlAssessmentRequest(client).entity_type_name,
            EmailFileAssessmentRequest(client).entity_type_name,
        )


if __name__ == "__main__":
    unittest.main()
