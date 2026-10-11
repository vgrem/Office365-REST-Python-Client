"""
Submit and list threat assessments — the security-team workflow.

Assess a file or email-file against threat categories (spam, phishing,
malware) and review existing requests. URL assessment is covered in
``examples/purview/threat-assessment/scan_url.py``.

Requires delegated permission ``ThreatAssessment.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/resources/threatassessment-api-overview
"""

import argparse
import base64

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    parser = argparse.ArgumentParser(description="Submit or list threat assessments")
    parser.add_argument("--list", action="store_true", help="List existing threat assessment requests")
    parser.add_argument("--file", help="Local file path to assess")
    parser.add_argument("--email-file", help="Local .eml file path to assess")
    parser.add_argument("--recipient", help="Recipient email for an email-file assessment")
    parser.add_argument("--category", choices=["spam", "phishing", "malware"], default="phishing")
    parser.add_argument("--expected", choices=["block", "unblock"], default="block")
    args = parser.parse_args()

    if not args.list and not args.file and not args.email_file:
        raise SystemExit("Provide --list, --file, or --email-file")
    if args.email_file and not args.recipient:
        raise SystemExit("--recipient is required for an email-file assessment")

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    if args.list:
        requests = client.information_protection.threat_assessment_requests.get().execute_query()
        print(f"Threat assessment requests ({len(requests)}):")
        for r in requests:
            print(f"  {r.id}  {r.created_datetime}  {r.status or '?'}  [{r.category or '?'}]")
        return

    if args.file:
        with open(args.file, "rb") as f:
            content = base64.b64encode(f.read()).decode()
        request = client.information_protection.create_file_assessment(
            file_name=args.file.rsplit("/", 1)[-1],
            content_data=content,
            expected_assessment=args.expected,
            category=args.category,
        ).execute_query()
        print(f"File assessment submitted: {request.id}")
    else:
        with open(args.email_file, "rb") as f:
            content = base64.b64encode(f.read()).decode()
        request = client.information_protection.create_email_file_assessment(
            recipient_email=args.recipient,
            content_data=content,
            expected_assessment=args.expected,
            category=args.category,
        ).execute_query()
        print(f"Email-file assessment submitted: {request.id}")


if __name__ == "__main__":
    main()
