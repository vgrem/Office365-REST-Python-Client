"""
Find guest (B2B) users who haven't signed in within a specified period.

Guest accounts that remain unused are a security risk — they can
be targeted for lateral movement. This script identifies stale
guests for review or cleanup.

Inspired by Find-InactiveGuestsWithAudit.ps1 and
Find-OldGuestAccounts.PS1 from Office 365 for IT Pros.

Required delegated permissions:
    User.Read.All           Read user profiles
    AuditLog.Read.All       Read sign-in activity
    User-Invite.All         (optional) manage guests

https://learn.microsoft.com/en-us/graph/api/resources/user
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def find_inactive_guests(days_threshold: int = 90) -> list[dict]:
    """Find guest users without sign-in activity.

    Args:
        days_threshold: Days since last sign-in to flag a guest.

    Returns:
        List of guest dicts with user info and days since last activity.
    """
    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days_threshold)
    inactive = []

    # Get all guest users (user_type == "Guest")
    guests = client.users.filter("userType eq 'Guest'").get_all().execute_query()

    for guest in guests:
        last_success = guest.sign_in_activity.lastSuccessfulSignInDateTime

        # Also check creation date as fallback
        created = guest.created_date_time

        last_activity = last_success or created
        if last_activity and last_activity < cutoff:
            days_since = (datetime.now(timezone.utc) - last_activity).days
            inactive.append(
                {
                    "upn": guest.user_principal_name,
                    "display_name": guest.display_name,
                    "created": created,
                    "last_signin": last_success,
                    "days_since_activity": days_since,
                }
            )
        elif not last_activity:
            # No sign-in history at all
            inactive.append(
                {
                    "upn": guest.user_principal_name,
                    "display_name": guest.display_name,
                    "created": created,
                    "last_signin": None,
                    "days_since_activity": days_threshold + 1,
                }
            )

    inactive.sort(key=lambda x: x["days_since_activity"], reverse=True)
    return inactive


def main():
    print("Finding inactive guest accounts (90+ days)...")
    guests = find_inactive_guests(days_threshold=90)

    if not guests:
        print("No inactive guest accounts found.")
        return

    print(f"\nFound {len(guests)} inactive guests:\n")
    for g in guests:
        last = g["last_signin"].strftime("%Y-%m-%d") if g["last_signin"] else "Never"
        print(f"  {g['upn']:45s}  {g['display_name'][:25]:25s}  Last: {last}  ({g['days_since_activity']} days)")


if __name__ == "__main__":
    main()
