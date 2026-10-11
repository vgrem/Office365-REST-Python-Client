"""
Monitor a Microsoft Graph long-running operation from the command line.

Operators rarely sit in the process that *started* a long job. A Graph monitor
URL is self-contained, and the library can serialize it to a small
``ContinuationToken``, so any later process can pick the job up and watch it:

    # a worker wrote the token when it submitted the copy
    python examples/patterns/lro/monitor_cli.py --token lro_continuation.json

    # or poll a raw monitor URL, emitting machine-readable events
    python examples/patterns/lro/monitor_cli.py --url "https://.../operations/op1" --json

The exit status makes it usable as a CI gate or a cron watchdog:
``0`` success, ``1`` the operation failed, ``2`` it timed out, ``130`` interrupted.
No permission beyond the ones the original operation required is needed — Graph
monitor URLs are caller-scoped and are polled with the same credentials.

https://learn.microsoft.com/en-us/graph/long-running-actions-overview
https://github.com/microsoft/api-guidelines/blob/vNext/graph/patterns/long-running-operations.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from office365.graph_client import GraphClient
from office365.runtime.lro import (
    ContinuationToken,
    OperationFailedError,
    OperationPoller,
    OperationStatus,
    OperationTimeoutError,
)
from tests.settings import client_id, password, tenant, username


def _event(status: OperationStatus) -> dict:
    return {
        "status": status.status,
        "http_status": status.http_status,
        "percentage_complete": status.percentage_complete,
        "resource_id": status.resource_id,
        "resource_location": status.resource_location,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor a Microsoft Graph long-running operation")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--token", metavar="FILE", help="continuation-token JSON written by a previous run")
    source.add_argument("--url", metavar="URL", help="raw operation-status (monitor) URL")
    parser.add_argument("--interval", type=float, default=2.0, help="seconds between polls when no Retry-After")
    parser.add_argument("--timeout", type=float, default=600.0, help="overall timeout in seconds")
    parser.add_argument("--json", action="store_true", help="emit one JSON object per poll event")
    args = parser.parse_args()

    token = (
        ContinuationToken.from_json(Path(args.token).read_text()) if args.token else ContinuationToken(poll_url=args.url)
    )

    def on_progress(status: OperationStatus) -> None:
        if args.json:
            print(json.dumps(_event(status)), flush=True)
        else:
            pct = f"{status.percentage_complete:6.1f}%" if status.percentage_complete is not None else "     -%"
            print(f"\r{pct}  {status.status or status.http_status}", end="", flush=True)

    # Graph monitor URLs are absolute and may live on another host, so attach the
    # client's credentials while polling.
    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    poller = OperationPoller.from_continuation_token(client, token, interval=args.interval, timeout=args.timeout)

    try:
        status = poller.wait(on_progress=on_progress)
    except OperationFailedError as exc:
        print(f"\n{exc}", file=sys.stderr)
        return 1
    except OperationTimeoutError as exc:
        print(f"\n{exc}", file=sys.stderr)
        return 2

    if not args.json:
        print()
        print(f"Terminal: {status.status}  resource_id={status.resource_id or '-'}")
    else:
        print(json.dumps(_event(status)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
