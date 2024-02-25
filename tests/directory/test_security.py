from unittest import TestCase

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_client_credentials


class TestSecurity(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(acquire_token_by_client_credentials)

    def test1_list_incidents(self):
        col = self.client.security.incidents.top(10).get().execute_query()
        self.assertIsNotNone(col.resource_path)

    # def test2_list_threat_assessment_requests(self):
    #    col = self.client.information_protection.threat_assessment_requests.top(10).get().execute_query()
    #    self.assertIsNotNone(col.resource_path)

    # def test3_list_landing_pages(self):
    #    col = (
    #        self.client.security.attack_simulation.landing_pages.filter("source eq 'tenant'")
    #        .get()
    #        .execute_query()
    #    )
    #    self.assertIsNotNone(col.resource_path)
