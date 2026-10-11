"""
Inventory of apps in the tenant Teams app catalog.

Lists every app uploaded or installed from the store, with its
distribution method and the details of the latest definition.

Useful for app governance: which apps are sideloaded, which are
store apps, and which versions are published.

Requires delegated or application permission ``AppCatalog.Read.All``.

https://learn.microsoft.com/en-us/graph/api/appcatalogs-list-teamsapps
"""

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.teams.apps.distributionmethod import TeamsAppDistributionMethod
from tests.settings import client_id, client_secret, tenant

DISTRIBUTION = {
    TeamsAppDistributionMethod.store: "store",
    TeamsAppDistributionMethod.organization: "organization",
    TeamsAppDistributionMethod.sideloaded: "sideloaded",
}


def _fmt_distribution(value) -> str:
    if isinstance(value, TeamsAppDistributionMethod):
        return DISTRIBUTION.get(value, value.name)
    return str(value or "?")


def main():
    parser = argparse.ArgumentParser(description="Inventory of apps in the tenant Teams app catalog")
    parser.add_argument("--name", default=None, help="only show apps whose display name matches")
    parser.add_argument("--top", type=int, default=100, help="maximum number of apps to show (default 100)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    try:
        apps = client.app_catalogs.teams_apps.expand(["appDefinitions"]).top(args.top).get().execute_query()
    except ClientRequestException as ex:
        print(f"✗ The app catalog is not readable ({ex.code})")
        print("  Grant AppCatalog.Read.All (or AppCatalog.ReadWrite.All) to the app,")
        print("  or sign in as a user who can see the catalog.")
        return

    print(f"Apps in catalog: {len(apps)}")
    for app in apps:
        if args.name and args.name.lower() not in (app.display_name or "").lower():
            continue

        definitions = list(app.app_definitions)
        latest = definitions[-1] if definitions else None
        state = latest.properties.get("publishingState", "?") if latest else "?"
        version = latest.properties.get("version", "?") if latest else "?"
        print(
            f"  {app.id:50s} {app.display_name or '(unnamed)':35s} "
            f"{_fmt_distribution(app.distribution_method):15s} state={state}  version={version}"
        )


if __name__ == "__main__":
    main()
