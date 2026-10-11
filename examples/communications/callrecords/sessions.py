"""
Drill into a call record: its sessions, and each session's segments.

A record is the *call*; a **session** is one endpoint's leg (one per participant
and device); a **segment** is a media stream inside a session. Quality metrics
and per-participant timings live on the segment, which is why every call-quality
report walks this three-level tree.

Requires the application permission ``CallRecords.Read.All``.

https://learn.microsoft.com/en-us/graph/api/callrecords-session-list
"""

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def identity_name(identity_set) -> str:
    """Best-effort label for a call ``IdentitySet`` — records carry display names, not UPNs."""
    user = identity_set.get_property("user") if identity_set is not None else None
    if user is None or not user.to_json():
        return "unknown"
    return user.get_property("displayName") or user.get_property("id") or "unknown"


def endpoint_name(endpoint) -> str:
    """Best-effort label for a session endpoint — service endpoints have no identity."""
    if endpoint is None:
        return "?"
    identity = endpoint.get_property("identity")
    return endpoint.get_property("name") or (identity_name(identity) if identity is not None else "service endpoint")


def main():
    parser = argparse.ArgumentParser(description="Show sessions and segments of a call record")
    parser.add_argument("--record-id", help="a record id; defaults to the newest in the feed")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    feed = client.communications.call_records

    if args.record_id:
        record = feed[args.record_id].get().execute_query()
    else:
        records = list(feed.get().execute_query())
        if not records:
            print("No call records in the feed yet — make a Teams call, then re-run.")
            return
        record = records[0]

    print(f"Call {record.id}  type={record.type_.name}  organizer={identity_name(record.organizer)}\n")

    sessions = record.sessions.get().execute_query()
    print(f"{len(sessions)} session(s):")
    for session in sessions:
        modalities = [m.name for m in session.modalities]
        print(
            f"  {endpoint_name(session.caller)} -> {endpoint_name(session.callee)}"
            f"  {session.start_date_time:%H:%M:%S}  modalities={modalities}"
        )
        # One request per session — fine for a report; bulk it if you walk many calls.
        for segment in session.segments.get().execute_query():
            print(f"    segment {segment.id}  {segment.start_date_time:%H:%M:%S} -> {segment.end_date_time:%H:%M:%S}")


if __name__ == "__main__":
    main()
