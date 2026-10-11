"""
Security alerts — list, triage, and update Microsoft 365 Defender
alerts programmatically.

Security operations teams use this to:
  - List active alerts across the tenant
  - Filter by severity, status, or detection source
  - Update alert classification, determination, and status
  - Automate triage (e.g. auto-resolve low-severity known issues)

Requires delegated permission ``SecurityAlert.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/resources/alert
"""

from datetime import datetime

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    alerts = client.security.alerts_v2

    # -- Step 1: list recent active alerts --
    all_alerts = alerts.get().execute_query()
    print(f"Total alerts: {len(all_alerts)}\n")

    # Filter by status
    active = [a for a in all_alerts if a.properties.get("status") in ("new", "inProgress")]
    resolved = [a for a in all_alerts if a.properties.get("status") == "resolved"]

    print(f"Active:   {len(active)}")
    print(f"Resolved: {len(resolved)}\n")

    if not active:
        print("No active alerts. Showing recent alerts:\n")

    for a in active or list(all_alerts)[:10]:
        alert_id = a.id or "?"
        title = a.properties.get("title", "(untitled)")
        severity = a.properties.get("severity", "?")
        status = a.properties.get("status", "?")
        created = a.properties.get("createdDateTime", "?")
        if isinstance(created, datetime):
            created = created.strftime("%m-%d %H:%M")

        detection = a.properties.get("detectionSource", a.properties.get("serviceSource", "?"))

        print(f"  [{severity:7s}] [{status:10s}] {title}")
        print(f"    id={alert_id[:20]}  source={detection}  created={created}")

        # Show tags if any
        tags = a.properties.get("tags", [])
        if tags:
            print(f"    tags: {', '.join(tags)}")
        print()

    # -- Step 2: update an alert (triage) --
    if active:
        target = active[0]
        alert_id = target.id
        title = target.properties.get("title", "(untitled)")
        print(f"Updating alert: {title}")

        # Available classification values:
        #   unknown, falsePositive, truePositive, informationalExpectedActivity
        #
        # Available determination values:
        #   unknown, apt, malware, phishing, securityPersonnel, securityTesting
        #   unwantedSoftware, other, multiStagedAttack, compromisedAccount
        #   maliciousUserActivity, notEnoughDataToValidate
        #
        # Available status values:
        #   unknown, new, inProgress, resolved

        target.set_property("classification", "informationalExpectedActivity")
        target.set_property("determination", "securityTesting")
        target.set_property("status", "inProgress")
        target.set_property("comment", "Reviewed — security testing, investigating")
        target.update().execute_query()
        print(f"  ✓ Updated: classification/status modified for {title}")

    # -- Step 3: create a custom alert (for security workflows) --
    # Alerts can also be created, for example from a SOAR playbook:
    #
    # from office365.security.alerts.alert import Alert
    # new_alert = Alert(client.context)
    # new_alert.set_property("title", "Custom alert from automation")
    # new_alert.set_property("severity", "medium")
    # new_alert.set_property("status", "new")
    # new_alert.set_property("category", "CustomAutomation")
    # client.security.alerts_v2.add(new_alert)
    # client.execute_query()
    # print("Custom alert created.")


if __name__ == "__main__":
    main()
