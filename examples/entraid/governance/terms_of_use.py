"""
Terms of use - list agreements and track user acceptances.

Shows the tenant's terms-of-use agreements, the file behind each one, and how
many users have accepted. The final section highlights users who have not yet
accepted any agreement.

Requires application permissions ``Agreement.Read.All`` and
``AgreementAcceptance.Read.All`` (plus ``User.Read.All`` for the pending list).
Not every tenant grants them; the script reports a denied request and exits 0.

Reference:
    https://learn.microsoft.com/en-us/graph/api/resources/agreement
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--users", type=int, default=100, help="max users to check for missing acceptance")
    args = parser.parse_args()

    client = _client()
    terms_of_use = client.identity_governance.terms_of_use

    try:
        agreements = terms_of_use.agreements.get().execute_query()
    except ClientRequestException as e:
        print(f"Terms of use are not available with these credentials:\n  {e}")
        return

    print(f"Terms of use agreements ({len(agreements)}):\n")
    for agreement in agreements:
        print(f"  {agreement.display_name or '(unnamed)'}")
        print(
            f"    view_required={agreement.is_viewing_before_acceptance_required}  "
            f"per_device={agreement.is_per_device_acceptance_required}  "
            f"reaccept_every={agreement.user_reaccept_required_frequency}"
        )
        for file in agreement.files.get().execute_query():
            print(f"    file: {file.file_name or file.display_name or '?'}")

        accepted = {a.user_principal_name for a in agreement.acceptances.get().execute_query()}
        accepted.discard(None)
        print(f"    accepted by {len(accepted)} user(s)")
        for upn in sorted(accepted)[:5]:
            print(f"      {upn}")

    all_acceptances = terms_of_use.agreement_acceptances.get().execute_query()
    accepted_upns = {a.user_principal_name.upper() for a in all_acceptances if a.user_principal_name}
    print(f"\nTotal acceptances: {len(all_acceptances)}")

    users = client.users.select(["userPrincipalName", "displayName"]).top(args.users).get().execute_query()
    pending = [u for u in users if (u.user_principal_name or "").upper() not in accepted_upns]
    if pending:
        print(f"\nUsers without acceptance: {len(pending)} / {len(users)}")
        for user in pending[:5]:
            print(f"  {user.user_principal_name}  {user.display_name or ''}")


if __name__ == "__main__":
    main()
