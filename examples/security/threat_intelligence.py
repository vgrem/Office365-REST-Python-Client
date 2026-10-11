"""
Enrich a host (domain or IP) with Microsoft Defender Threat Intelligence.

Resolves the host and pulls its reputation, WHOIS registration, subdomains,
passive DNS records, trackers and SSL certificates, then lists the active
threat-actor intel profiles and the latest threat intel articles.

Requires delegated permission ``ThreatIntelligence.Read.All``.

https://learn.microsoft.com/en-us/graph/api/security-threatintelligence-list
https://learn.microsoft.com/en-us/graph/api/security-host-get
https://learn.microsoft.com/en-us/graph/api/security-list-intelprofiles
"""

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _enrich_host(ti, host: str) -> None:
    """Resolve a host and print its threat intelligence attributes."""
    try:
        h = ti.hosts[host].get().execute_query()
    except ClientRequestException:
        print(f"\nNo threat intelligence data found for host: {host}")
        return

    print(f"\nHost: {host}")
    print(f"  First seen: {h.properties.get('firstSeenDateTime', '?')}")
    print(f"  Last seen:  {h.properties.get('lastSeenDateTime', '?')}")

    try:
        reputation = h.reputation.get().execute_query()
        print(
            "  Reputation: "
            f"score={reputation.properties.get('score', '?')} "
            f"classification={reputation.properties.get('classification', '?')}"
        )
    except ClientRequestException:
        pass

    for name, navigation in (
        ("Subdomains", h.subdomains),
        ("Passive DNS records", h.passive_dns),
        ("Trackers", h.trackers),
    ):
        try:
            print(f"  {name}: {len(navigation.get().execute_query())}")
        except ClientRequestException:
            pass

    try:
        whois = h.whois.get().execute_query()
        print(
            "  WHOIS: "
            f"registrar={whois.properties.get('registrar', '?')} "
            f"registered={whois.properties.get('createdDateTime', '?')}"
        )
    except ClientRequestException:
        pass


def main():
    parser = argparse.ArgumentParser(description="Threat intelligence IOC enrichment")
    parser.add_argument("host", help="hostname or IP address to enrich")
    parser.add_argument("--articles", type=int, default=5, help="number of latest articles to list (default: 5)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    ti = client.security.threat_intelligence

    _enrich_host(ti, args.host)

    profiles = ti.intel_profiles.get().execute_query()
    print(f"\nThreat-actor intel profiles ({len(profiles)}):")
    for profile in profiles:
        targets = ", ".join(profile.targets) if profile.targets else "?"
        print(f"  {profile.title}  severity={profile.properties.get('severity', '?')}  targets=[{targets}]")

    articles = ti.articles.top(args.articles).get().execute_query()
    print(f"\nLatest threat intel articles ({len(articles)}):")
    for article in articles:
        print(f"  {article.title}")


if __name__ == "__main__":
    main()
