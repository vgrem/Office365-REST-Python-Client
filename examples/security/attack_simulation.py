"""
Attack simulation training — list phishing simulation campaigns,
automations, payloads, and training assignments.

Attack simulation is part of Microsoft 365 Defender. Security teams
use this to:
  - List active and past phishing simulations
  - View simulation automations (recurring campaigns)
  - Check landing pages configured for the tenant

Requires delegated permission ``AttackSimulation.Read.All`` and
``SecurityEvents.Read.All``.

https://learn.microsoft.com/en-us/graph/api/resources/attacksimulationroot
"""

from datetime import datetime

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def _fmt(dt):
    return dt.strftime("%Y-%m-%d") if isinstance(dt, datetime) else "?"


def main():
    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    sim = client.security.attack_simulation

    # -- Simulations --
    items = sim.simulations.get().execute_query()
    print(f"Attack simulations: {len(items)}\n")
    for s in items:
        name = s.properties.get("displayName", s.properties.get("name", "(unnamed)"))
        print(
            f"  {name:50s}  "
            f"status={s.properties.get('status', '?'):15s}  "
            f"technique={s.properties.get('attackTechnique', '?'):20s}  "
            f"created={_fmt(s.properties.get('createdDateTime'))}  "
            f"complete={_fmt(s.properties.get('completionDateTime'))}"
        )

    # -- Simulation automations --
    items = sim.simulation_automations.get().execute_query()
    print(f"\nSimulation automations: {len(items)}")
    for a in items:
        name = a.properties.get("displayName", "(unnamed)")
        print(f"  {name:50s}  status={a.properties.get('status', '?')}")
        for r in a.runs.get().execute_query():
            print(
                f"    -> run: simulation={str(r.properties.get('simulationId', ''))[:20]}  "
                f"status={r.properties.get('status', '?')}  "
                f"start={_fmt(r.properties.get('startDateTime'))}"
            )

    # -- Landing pages (the endpoint requires a filter; `source` is tenant|builtIn) --
    items = sim.landing_pages.filter("source eq 'tenant'").get().execute_query()
    print(f"\nLanding pages: {len(items)}")
    for p in items:
        print(f"  locale={p.properties.get('locale', '?'):10s}  status={p.properties.get('status', '?')}")


if __name__ == "__main__":
    main()
