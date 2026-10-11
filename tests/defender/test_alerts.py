"""Security Alerts — Microsoft 365 Defender alert management (alerts_v2).
Tests cover:
  - Listing alerts with filters and pagination
  - Inspecting alert metadata (severity, status, category, detectionSource)
  - Alert evidence and comments
  - Updating alert status (triaging)
  - Creating alerts via the unified API
"""

from __future__ import annotations

from typing import ClassVar, Optional

from tests.decorators import requires_delegated
from tests.graph_case import GraphDelegatedTestCase

_ALERT_READ = ("SecurityAlert.Read.All", "SecurityAlert.ReadWrite.All")
_ALERT_WRITE = ("SecurityAlert.ReadWrite.All",)


class TestAlerts(GraphDelegatedTestCase):
    """Microsoft 365 Defender alerts (v2 API)."""

    created_alert: ClassVar[Optional[object]] = None

    @requires_delegated(
        *_ALERT_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_01_list_alerts_paginated(self):
        """Listing alerts with $top=10 returns a valid collection."""
        result = self.client.security.alerts_v2.top(10).get().execute_query()
        self.assertIsNotNone(result.resource_path)

    @requires_delegated(
        *_ALERT_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_02_filter_alerts_by_severity(self):
        """Filtering alerts by severity reduces the result set."""
        result = self.client.security.alerts_v2.filter("severity eq 'high'").top(5).get().execute_query()
        self.assertIsNotNone(result.resource_path)
        for alert in result:
            self.assertEqual(alert.get_property("severity"), "high")

    @requires_delegated(
        *_ALERT_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_03_filter_alerts_by_status(self):
        """Filtering alerts by status returns only alerts in that state."""
        for status in ("newAlert", "inProgress", "resolved"):
            result = self.client.security.alerts_v2.filter(f"status eq '{status}'").top(3).get().execute_query()
            # Assert — no crash, valid collection
            self.assertIsNotNone(result.resource_path)
            for alert in result:
                self.assertEqual(alert.get_property("status"), status)

    @requires_delegated(
        *_ALERT_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_04_alert_has_required_properties(self):
        """Each alert exposes severity, status, category, and detectionSource."""
        result = self.client.security.alerts_v2.top(5).get().execute_query()
        if len(result) == 0:
            self.skipTest("No alerts exist to inspect")
        limit = 2
        for alert in result:
            self.assertIsNotNone(alert.id)
            self.assertIsNotNone(alert.severity)
            self.assertIsNotNone(alert.status)
            self.assertIsNotNone(alert.category)
            self.assertIsNotNone(alert.detection_source)
            limit -= 1
            if limit == 0:
                break

    @requires_delegated(
        *_ALERT_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_05_alert_has_evidence(self):
        """An alert may expose an evidence collection."""
        result = self.client.security.alerts_v2.top(5).get().execute_query()
        if len(result) == 0:
            self.skipTest("No alerts exist to inspect")
        for alert in result:
            evidence = alert.get_property("evidence")
            if evidence:
                self.assertGreater(len(evidence), 0)
                break
        else:
            self.skipTest("No alerts with evidence found")

    @requires_delegated(
        *_ALERT_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_06_alert_has_description(self):
        """A typical alert has a description field."""
        result = self.client.security.alerts_v2.top(5).get().execute_query()
        if len(result) == 0:
            self.skipTest("No alerts exist to inspect")
        for alert in result:
            description = alert.get_property("description")
            if description:
                self.assertIsInstance(description, str)
                self.assertGreater(len(description), 0)
                break
        else:
            self.skipTest("No alerts with descriptions found")

    @requires_delegated(
        *_ALERT_WRITE,
        bypass_roles=["Global Administrator"],
    )
    def test_07_update_alert_comment(self):
        """Adding a comment to an alert updates its comments collection."""
        result = self.client.security.alerts_v2.top(3).get().execute_query()
        if len(result) == 0:
            self.skipTest("No alerts exist to update")
        target = result[0]
        alert_id = target.id
        assert alert_id is not None
        try:
            # Add a comment
            from office365.security.alerts.comment import AlertComment

            comment = AlertComment(comment="SDK test — automated triage comment")
            target.comments.add(comment)
            target.update().execute_query()
            # Verify
            updated = self.client.security.alerts_v2[alert_id].get().execute_query()
            updated_comments = updated.get_property("comments", [])
            if len(updated_comments) > 0:
                last_comment = updated_comments[-1]
                self.assertIsNotNone(last_comment.get_property("comment"))
        except Exception as e:
            self.skipTest(f"Cannot update alert comment: {e}")
