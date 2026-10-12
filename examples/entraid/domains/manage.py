"""
Domain management — add, verify, check DNS records, and configure
supported services.

Managing custom domains is one of the first steps when onboarding a
new tenant. This example covers the full lifecycle:
  - Add a custom domain
  - Read the verification DNS records to paste into your registrar
  - Verify domain ownership
  - Show service configuration DNS records
  - Set supported services (Email, OfficeCommunicationsOnline, etc.)

Requires delegated permission ``Domain.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/resources/domain
"""

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

CUSTOM_DOMAIN = "contoso-marketing.com"  # ← change to your domain


def main():
    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    # -- Step 1: list existing domains --
    domains = client.domains.get().execute_query()
    print("Domain(s):")
    for d in domains:
        state = "✔ verified" if d.state and d.state.status == "Verified" else "✗ unverified"
        svc = ", ".join(d.supported_services) if d.supported_services else "none"
        print(f"  {d.id:30s}  {state:14s}  services: {svc}")
    print()

    # -- Step 2: add a custom domain (if it doesn't exist already) --
    domain = next((d for d in domains if d.id == CUSTOM_DOMAIN), None)
    if domain is None:
        print(f"Adding domain '{CUSTOM_DOMAIN}'...")
        domain = client.domains.add(id=CUSTOM_DOMAIN).execute_query()
        print(f"  Added: {domain.id}")
    else:
        print(f"Domain '{CUSTOM_DOMAIN}' already exists.")

    # -- Step 3: show verification DNS records --
    # These need to be added to your DNS registrar's zone file.
    print(f"\nVerification DNS records for '{CUSTOM_DOMAIN}':")
    v_records = domain.verification_dns_records.get().execute_query()
    for r in v_records:
        rtype = r.properties.get("recordType", "?")
        label = r.properties.get("label", "?")
        value = r.properties.get("value", r.properties.get("text", "?"))
        ttl = r.properties.get("ttl", "?")
        print(f"  {rtype:6s}  {label:35s}  TTL={ttl:>5}  → {value}")

    if not v_records:
        print("  (no verification records — domain may already be verified)")

    # -- Step 4: verify the domain --
    # Do this only after you've added the DNS records at your registrar.
    response = input("\nAdd the DNS records above at your registrar, then type 'verify' to confirm: ")
    if response.strip().lower() == "verify":
        domain = domain.verify().execute_query()
        is_verified = domain.state and domain.state.status == "Verified"
        print(f"  Domain verification: {'✔ SUCCESS' if is_verified else '✗ FAILED'}")
    else:
        print("  Skipped verification.")

    # -- Step 5: show service configuration records --
    print("\nService configuration DNS records:")
    s_records = domain.service_configuration_records.get().execute_query()
    for r in s_records:
        rtype = r.properties.get("recordType", "?")
        label = r.properties.get("label", "?")
        value = r.properties.get("value", r.properties.get("text", "?"))
        ttl = r.properties.get("ttl", "?")
        print(f"  {rtype:6s}  {label:35s}  TTL={ttl:>5}  → {value}")

    # -- Step 6: set supported services (optional) --
    # domain.set_property("supportedServices", ["Email", "OfficeCommunicationsOnline"])
    # domain.update().execute_query()
    # print(f"\nSupported services updated.")


if __name__ == "__main__":
    main()
