from unittest import TestCase

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant
from tests.decorators import requires_app_permission


class TestSecurity(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient(tenant=test_tenant).with_client_secret(
            test_client_id, test_client_secret
        )

    # def test1_create_alert(self):
    #    result = self.client.security.alerts.add(
    #        "Simulated Phishing Alert",
    #        "This is a test alert for simulation purposes.",
    #        "high",
    #        "ThreatManagement",
    #        "newAlert",
    #        "Custom",
    #        {"provider": "CustomProvider", "providerVersion": "1.0"},
    #    ).execute_query()
    #    self.assertIsNotNone(result.resource_path)

    @requires_app_permission("AttackSimulation.ReadWrite.All")
    def test2_create_simulations(self):
        simulation = {
            "displayName": "Test Phishing Campaign",
            "payloadDeliveryPlatform": "email",
            "durationInDays": 3,
            "attackTechnique": "credentialHarvesting",
            "status": "scheduled",
            "startDateTime": "2023-12-01T08:00:00Z",
        }
        result = self.client.security.attack_simulation.simulations.add(
            **simulation
        ).execute_query()
        self.assertIsNotNone(result.resource_path)

    #@requires_app_permission("SecurityIncident.Read.All")
    #@requires_app_permission("SecurityIncident.ReadWrite.All")
    def test2_list_incidents(self):
        col = self.client.security.incidents.top(10).get().execute_query()
        self.assertIsNotNone(col.resource_path)

    # def test3_list_landing_pages(self):
    #    col = (
    #        self.client.security.attack_simulation.landing_pages.filter("source eq 'tenant'")
    #        .get()
    #        .execute_query()
    #    )
    #    self.assertIsNotNone(col.resource_path)
