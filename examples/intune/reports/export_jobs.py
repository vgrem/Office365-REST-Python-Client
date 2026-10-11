"""
Long-running export jobs: request a report, poll it, download the result.

Some Intune reports are too large to return inline. You create an *export job*
that references the report, Graph renders it in the background (a genuine
long-running operation), and when the job completes it exposes a download URL.

This is the canonical Intune async flow:

1. **Create** the job with ``reports.export_jobs.add(...)`` — you get back a job
   in ``notStarted``/``inProgress`` state.
2. **Poll** ``reports.export_jobs[<job-id>].get()`` every ``--interval`` seconds
   until the status is ``completed`` (or ``failed``).
3. **Download** the pre-signed URL the job exposes.

Because the job runs server-side, the script is bounded by ``--timeout`` and
exits cleanly if the report is still being generated.

    python export_jobs.py                                  # Devices -> CSV
    python export_jobs.py --report DevicesWithoutCompliancePolicy
    python export_jobs.py --report DeviceCompliancePolicyDeviceStateSummary

Requires delegated permission ``DeviceManagementManagedDevices.Read.All``.

https://learn.microsoft.com/en-us/graph/api/intune-reporting-devicemanagementexportjob-create
https://learn.microsoft.com/en-us/graph/api/intune-reporting-devicemanagementexportjob-get
"""

from __future__ import annotations

import argparse
import os
import tempfile
import time

import requests
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def status_name(job) -> str:
    """Normalise the job status to a lower-case string (enum or plain text)."""
    status = job.status
    return (getattr(status, "name", None) or str(status or "")).lower()


def download(url: str, target: str) -> int:
    """Stream a report download URL to ``target`` and return the byte count."""
    with requests.get(url, stream=True, timeout=300) as response:
        response.raise_for_status()
        with open(target, "wb") as handle:
            total = 0
            for chunk in response.iter_content(chunk_size=64 * 1024):
                handle.write(chunk)
                total += len(chunk)
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Create and poll an Intune export job")
    parser.add_argument("--report", default="Devices", help="Report name (default: Devices)")
    parser.add_argument("--format", default="csv", choices=["csv", "json"], help="Output format")
    parser.add_argument("--filter", default="", help="OData filter applied to the report")
    parser.add_argument("--timeout", type=int, default=300, help="Seconds to wait for completion")
    parser.add_argument("--interval", type=int, default=15, help="Seconds between polls")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    jobs = client.device_management.reports.export_jobs

    try:
        job = jobs.add(
            reportName=args.report,
            filter=args.filter,
            format=args.format,
            localizationType="localizedValuesAsAdditionalColumn",
        ).execute_query()
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementManagedDevices.Read.All and re-run.")
        return

    print(f"Created export job {job.id} for '{args.report}' (status: {status_name(job) or '?'})")

    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        time.sleep(args.interval)
        try:
            job = jobs[job.id].get().execute_query()
        except ClientRequestException as exc:
            print(f"  poll failed: {exc.code}: {exc.message}")
            return
        state = status_name(job)
        print(f"  status: {state or '?'}")
        if state == "completed":
            break
        if state == "failed":
            print("[failed] the report could not be generated.")
            return
    else:
        print(f"\n[timeout] still running after {args.timeout}s — increase --timeout to keep waiting.")
        return

    if not job.url:
        print("[completed] the job exposes no download URL (empty report).")
        return

    target = os.path.join(tempfile.gettempdir(), f"intune_export_{job.id}.{args.format}")
    size = download(job.url, target)
    print(f"\nDownloaded {size} byte(s) to {target}")


if __name__ == "__main__":
    main()
