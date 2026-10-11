"""
MFA registration status — who is protected and who is not.

The authentication-methods registration report lists every user with the
authentication features they are registered for and capable of: MFA, self-service
password reset (SSPR) and passwordless. It is the fastest way to find privileged
accounts without MFA.

    python mfa_status.py
    python mfa_status.py --admins-only
    python mfa_status.py --all --limit 50

Requires application permission ``Reports.Read.All`` (or ``AuditLog.Read.All``).

https://learn.microsoft.com/en-us/graph/api/authenticationmethods-list-userregistrationdetails
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main() -> None:
    parser = argparse.ArgumentParser(description="MFA / SSPR registration status")
    parser.add_argument("--all", action="store_true", help="List every user (default: only users without MFA)")
    parser.add_argument("--admins-only", action="store_true", help="Restrict the listing to admins")
    parser.add_argument("--limit", type=int, default=30, help="Rows to print (default: 30)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    details = list(client.reports.authentication_methods.user_registration_details.get().execute_query())

    total = len(details)
    mfa = [d for d in details if d.is_mfa_registered]
    sspr = [d for d in details if d.is_sspr_registered]
    passwordless = [d for d in details if d.is_passwordless_capable]
    admins = [d for d in details if d.is_admin]
    admins_without_mfa = [d for d in admins if not d.is_mfa_registered]

    def pct(count: int) -> str:
        return f"{count / total * 100:.1f}%" if total else "n/a"

    print(f"Authentication coverage across {total:,} user(s):")
    print(f"  MFA registered        {len(mfa):>6,}  ({pct(len(mfa))})")
    print(f"  SSPR registered       {len(sspr):>6,}  ({pct(len(sspr))})")
    print(f"  Passwordless capable  {len(passwordless):>6,}  ({pct(len(passwordless))})")
    print(f"  Admins                {len(admins):>6,}  ({len(admins_without_mfa)} without MFA)")

    shown = details
    if args.admins_only:
        shown = [d for d in shown if d.is_admin]
    if not args.all:
        shown = [d for d in shown if not d.is_mfa_registered]

    label = "admin(s)" if args.admins_only else "user(s)"
    if not args.all:
        label = f"{label} without MFA"
    print(f"\n{len(shown):,} {label} — first {min(args.limit, len(shown))}:")
    for details_row in shown[: args.limit]:
        methods = ", ".join(str(m) for m in details_row.methods_registered) or "-"
        flag = " [admin]" if details_row.is_admin else ""
        print(f"  {details_row.user_principal_name:45s}{flag}  methods: {methods}")


if __name__ == "__main__":
    main()
