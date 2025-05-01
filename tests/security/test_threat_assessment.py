from tests.graph_case import GraphTestCase


class TestThreatAssessment(GraphTestCase):

    threat_assessment_request = None

    def test1_create_url_assessment(self):
        result = self.client.information_protection.create_url_assessment(
            "http://test.com", "block", "phishing"
        ).execute_query()
        self.assertIsNotNone(result.resource_path)
        self.__class__.threat_assessment_request = result

    def test2_list_threat_assessment_requests(self):
        col = (
            self.client.information_protection.threat_assessment_requests.get().execute_query()
        )
        self.assertIsNotNone(col.resource_path)
