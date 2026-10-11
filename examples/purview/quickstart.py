"""
Purview quickstart — a read-only snapshot of what this tenant can actually do.

Microsoft Purview is a family of services with separate permissions and, in some
cases, separate administrator roles. Instead of failing on the first missing one,
this script probes every surface in turn and reports whether it is reachable,
how many objects came back, or exactly which permission is missing.

Run it first: it tells you which other examples in this folder will work for you.

    python quickstart.py

Reads only, and never raises on a denial — a surface that is not available is
reported, not treated as an error.

https://learn.microsoft.com/en-us/graph/api/resources/security-api-overview
"""

from __future__ import annotations

import argparse
from typing import Callable

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.exceptions import AccessDeniedException
from tests.settings import client_id, password, tenant, username

_COLUMN = 24


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _short(message: str, limit: int = 90) -> str:
    message = " ".join(message.split())
    return message if len(message) <= limit else message[: limit - 1] + "\u2026"


def _probe(name: str, scope: str, call: Callable):
    """Run one probe and print a one-line verdict, never raising."""
    try:
        result = call()
        print(f"  OK       {name:<{_COLUMN}} {len(list(result))} object(s)")
    except AccessDeniedException as exc:
        print(f"  DENIED   {name:<{_COLUMN}} {_short(exc.message)}")
        print(f"           {'':<{_COLUMN}} grant {scope}")
    except ClientRequestException as exc:
        print(f"  BLOCKED  {name:<{_COLUMN}} {exc.code}: {_short(exc.message or '')}")
        print(f"           {'':<{_COLUMN}} needs {scope}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe the Microsoft Purview surfaces available to this tenant")
    parser.parse_args()

    client = _client()
    print("Microsoft Purview — capability snapshot\n")

    _probe(
        "eDiscovery cases",
        "eDiscovery.ReadWrite.All",
        lambda: client.security.cases.ediscovery_cases.get().execute_query(),
    )
    _probe(
        "Retention labels",
        "RecordsManagement.ReadWrite.All + Compliance Administrator",
        lambda: client.security.labels.retention_labels.get().execute_query(),
    )
    _probe(
        "Sensitivity labels",
        "InformationProtectionPolicy.Read.All + Compliance Administrator",
        lambda: client.security.data_security_and_governance.sensitivity_labels.get().execute_query(),
    )
    _probe(
        "Subject rights requests",
        "SubjectRightsRequest.ReadWrite.All",
        lambda: client.security.subject_rights_requests.get().execute_query(),
    )
    _probe(
        "Threat assessments",
        "ThreatAssessment.ReadWrite.All",
        lambda: client.information_protection.threat_assessment_requests.get().execute_query(),
    )

    print("\nEach probe reads the first page only; counts are a sample, not a total.")


if __name__ == "__main__":
    main()
