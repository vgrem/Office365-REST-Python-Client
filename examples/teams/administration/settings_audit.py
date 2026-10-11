"""
Settings compliance: compare every team's settings against a policy baseline.

Team settings are not managed centrally — each team can loosen or tighten guest,
messaging, member and fun settings. This script walks the tenant and prints the
teams that deviate from the baseline below, so you can see where drift happens
before deciding whether to alert on it or fix it.

Requires the application permissions ``TeamSettings.Read.All`` and
``Team.ReadBasic.All``.

https://learn.microsoft.com/en-us/graph/api/team-get
https://learn.microsoft.com/en-us/microsoftteams/team-settings-policies
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

# The four setting groups every team carries, reduced to the fields the listing
# endpoint actually returns. Values are the ones the organization considers
# acceptable; edit them to match your own policy.
BASELINE = {
    "guestSettings": {"allowCreateUpdateChannels": False, "allowDeleteChannels": False},
    "memberSettings": {"allowDeleteChannels": True, "allowAddRemoveApps": True},
    "messagingSettings": {"allowUserEditMessages": True, "allowOwnerDeleteMessages": True},
    "funSettings": {"allowGiphy": False, "allowStickersAndMemes": True},
}


def _setting(settings, key):
    """Read one setting from a settings holder (ClientValue or dict)."""
    if settings is None:
        return None
    if isinstance(settings, dict):
        return settings.get(key)
    return getattr(settings, key, None)


def _deviations(team) -> list[str]:
    diffs = []
    for section, expected in BASELINE.items():
        current = team.get_property(section)
        if current is None:
            continue
        for key, value in expected.items():
            actual = _setting(current, key)
            if actual is None:  # the listing response did not include this field
                continue
            if actual != value:
                diffs.append(f"{section}.{key}: {actual} → {value}")
    return diffs


def main():
    parser = argparse.ArgumentParser(description="Audit team settings against a baseline")
    parser.add_argument("--limit", type=int, default=0, help="scan at most N teams (0 = all)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    teams = list(client.teams.get_all().select(["id", "displayName"]).execute_query())
    if args.limit:
        teams = teams[: args.limit]
    print(f"Checking {len(teams)} team(s) against the baseline…\n")

    offenders = 0
    for team in teams:
        diffs = _deviations(team)
        if not diffs:
            continue
        offenders += 1
        print(f"  {team.display_name}")
        for diff in diffs:
            print(f"      {diff}")

    if offenders:
        print(f"\n{offenders} of {len(teams)} team(s) deviate from the baseline.")
    else:
        print("Every team matches the baseline.")


if __name__ == "__main__":
    main()
