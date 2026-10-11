"""
Threat assessment — submit a URL and a file for phishing/malware analysis.

Purview Information Protection scores content for spam, phishing and malware.
You submit a URL or a base64 file with an *expected* verdict (`block` or
`unblock`); Purview returns a request whose `status` is first `pending` and
later `completed`, together with the per-provider results.

    python scan_url.py
    python scan_url.py --url http://test-phishing-example.com --category phishing
    python scan_url.py --no-file

Requires delegated permission ``ThreatAssessment.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/informationprotection-post-threatassessmentrequests
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.exceptions import AccessDeniedException
from tests.settings import client_id, password, tenant, username

_SCOPE = "ThreatAssessment.ReadWrite.All"
# Harmless EICAR test string (base64) — the standard antivirus test file.
_EICAR_B64 = "WDVPIVAlQEFQWzRcUFpYNTQoUFpYNTQoUFpYNTQoUFpYNTQoUFpYNTQoUFpYNTQoUFpYNTQoUFpYNTQo"


def _client() -> GraphClient:
    return (
        GraphClient(tenant=tenant)
        .with_username_and_password(client_id, username, password)
        .require_delegated_permission(_SCOPE)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Submit a URL and a file for threat assessment")
    parser.add_argument("--url", default="http://test-phishing-example.com", help="URL to assess")
    parser.add_argument("--category", default="phishing", choices=["spam", "phishing", "malware"])
    parser.add_argument("--expected", default="block", choices=["block", "unblock"])
    parser.add_argument("--no-file", action="store_true", help="Skip the file assessment")
    args = parser.parse_args()

    client = _client()
    try:
        url_result = client.information_protection.create_url_assessment(
            url=args.url, expected_assessment=args.expected, category=args.category
        ).execute_query()
        print(f"URL   {url_result.url}  ->  {url_result.status}  ({url_result.id})")

        if not args.no_file:
            file_result = client.information_protection.create_file_assessment(
                file_name="eicar_test.txt",
                content_data=_EICAR_B64,
                expected_assessment=args.expected,
                category="malware",
            ).execute_query()
            print(f"File  {file_result.file_name}  ->  {file_result.status}  ({file_result.id})")
    except AccessDeniedException as exc:
        print(f"Access denied: {exc.message}")
        print(f"Grant the delegated permission {_SCOPE} and re-run.")
        raise SystemExit(0) from None

    print("\nAssessment is asynchronous: the initial status is 'pending', then 'completed'.")


if __name__ == "__main__":
    main()
