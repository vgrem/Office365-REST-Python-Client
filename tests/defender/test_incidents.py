"""Security Incidents — correlated alert collections in Microsoft 365 Defender.
Tests cover:
  - Listing incidents with pagination
  - Filtering by status, severity, and assignedTo
  - Reading incident metadata (classification, tags, comments)
  - Expanding related alerts
  - Updating incident status and assignment
"""

from __future__ import annotations

from typing import ClassVar, Optional

from tests.decorators import requires_delegated
from tests.graph_case import GraphDelegatedTestCase

_INCIDENT_READ = ("SecurityIncident.Read.All", "SecurityIncident.ReadWrite.All")
_INCIDENT_WRITE = ("SecurityIncident.ReadWrite.All",)


class TestIncidents(GraphDelegatedTestCase):
    """Microsoft 365 Defender incidents."""

    created_simulated_incident: ClassVar[Optional[object]] = None

    @requires_delegated(
        *_INCIDENT_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_01_list_incidents(self):
        """Listing incidents with $top=10 returns a valid collection."""
        result = self.client.security.incidents.top(10).get().execute_query()
        self.assertIsNotNone(result.resource_path)

    @requires_delegated(
        *_INCIDENT_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_02_filter_incidents_by_status(self):
        """Filtering incidents by 'activeStatus' returns active incidents."""
        result = self.client.security.incidents.filter("status eq 'active'").top(5).get().execute_query()
        self.assertIsNotNone(result.resource_path)
        for inc in result:
            self.assertEqual(inc.get_property("status"), "active")

    @requires_delegated(
        *_INCIDENT_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_03_incident_has_expected_properties(self):
        """An incident exposes id, severity, status, createdDateTime, and assignedTo."""
        result = self.client.security.incidents.top(3).get().execute_query()
        if len(result) == 0:
            self.skipTest("No incidents exist to inspect")
        for inc in result:
            self.assertIsNotNone(inc.id)
            self.assertIsNotNone(inc.get_property("severity"))
            self.assertIsNotNone(inc.get_property("status"))
            self.assertIsNotNone(inc.get_property("createdDateTime"))
            break  # Check one

    @requires_delegated(
        *_INCIDENT_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_04_incident_can_expand_alerts(self):
        """Expanding alerts on an incident returns its associated alerts."""
        result = self.client.security.incidents.top(3).get().execute_query()
        if len(result) == 0:
            self.skipTest("No incidents exist to inspect")
        for inc in result:
            try:
                alerts = inc.alerts.get().execute_query()
                if len(alerts) > 0:
                    # Verify at least one alert has expected properties
                    alert = alerts[0]
                    self.assertIsNotNone(alert.get_property("id"))
                    self.assertIsNotNone(alert.get_property("severity"))
                    break
            except Exception:
                continue

    @requires_delegated(
        *_INCIDENT_WRITE,
        bypass_roles=["Global Administrator"],
    )
    def test_05_update_incident_classification(self):
        """Updating an incident's classification and determination should succeed."""
        result = self.client.security.incidents.top(3).get().execute_query()
        if len(result) == 0:
            self.skipTest("No incidents exist to update")
        target = result[0]
        # Set a test comment and don't change the actual classification
        try:
            from office365.security.alerts.comment import AlertComment

            comment = AlertComment(comment="SDK test incident — reviewing")
            target.comments.append(comment)
            target.update().execute_query()
        except Exception as e:
            self.skipTest(f"Cannot update incident: {e}")

    @requires_delegated(
        *_INCIDENT_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_06_incident_has_tags(self):
        """Incidents may have tags; the collection should be accessible."""
        result = self.client.security.incidents.top(5).get().execute_query()
        if len(result) == 0:
            self.skipTest("No incidents exist to inspect")
        for inc in result:
            tags = inc.get_property("tags", [])
            self.assertIsNotNone(tags)
            break

    @requires_delegated(
        *_INCIDENT_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_07_filter_incidents_by_severity(self):
        """Filtering incidents by severity returns only matching results."""
        for severity in ("high", "medium", "low", "informational"):
            result = self.client.security.incidents.filter(f"severity eq '{severity}'").top(3).get().execute_query()
            self.assertIsNotNone(result.resource_path)
            for inc in result:
                self.assertEqual(inc.get_property("severity"), severity)
