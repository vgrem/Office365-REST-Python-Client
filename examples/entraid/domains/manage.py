"""
Domain management — add, verify, inspect DNS records, and configure services.

Managing custom domains is one of the first steps when onboarding a new
tenant. This example covers the full lifecycle:

  - list the tenant's domains
  - add a custom domain idempotently (``client.domains.ensure(...)``)
  - read the verification DNS records to paste into your registrar
  - verify domain ownership
  - show service configuration DNS records
  - set supported services (Email, OfficeCommunicationsOnline, ...)

Requires delegated permission ``Domain.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/resources/domain
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username

DEFAULT_DOMAIN = "contoso-marketing.com"


def _print_dns_records(records, title: str) -> None:
    """Print the DNS records a registrar needs to host."""
    print(f"\n{title}:")
    if not records:
        print("  (none — the domain may already be verified)")
        return
    for record in records:
        print(f"  {record.record_type or '?':<6} {record.label or '?':<35} -> {record.value or '?'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", default=DEFAULT_DOMAIN, help="custom domain to manage")
    parser.add_argument(
        "--services",
        nargs="*",
        help="supported services to enable (e.g. Email OfficeCommunicationsOnline)",
    )
    parser.add_argument("--verify", action="store_true", help="verify ownership (add the DNS records first)")
    parser.add_argument("--apply", action="store_true", help="apply changes (default: dry run)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    client.require_delegated_permission("Domain.ReadWrite.All")

    # -- Step 1: list existing domains --
    domains = client.domains.get().execute_query()
    print("Domain(s):")
    print(domains.to_string())

    # -- Step 2: add the custom domain if it is missing (idempotent) --
    exists = any(d.id == args.domain for d in domains)
    if not exists and not args.apply:
        print(f"\nDomain '{args.domain}' is not present. Re-run with --apply to add it.")
        return
    domain = client.domains.ensure(args.domain)
    try:
        domain = domain.execute_query()
    except ClientRequestException as e:
        # Adding a domain also requires the signed-in user to administer domains.
        print(f"\nCould not add '{args.domain}': {e}")
        return
    print(f"\nDomain '{args.domain}' is {'present' if exists else 'added'}.")

    # -- Step 3: show the verification DNS records --
    records = domain.verification_dns_records.get().execute_query()
    _print_dns_records(records, f"Verification DNS records for '{args.domain}'")

    # -- Step 4: verify ownership (only after the DNS records are live) --
    if args.verify:
        if not args.apply:
            print("\nVerification skipped (dry run). Re-run with --apply --verify.")
        else:
            domain = domain.verify().execute_query()
            ok = domain.state and domain.state.status == "Verified"
            print(f"\nDomain verification: {'SUCCESS' if ok else 'FAILED (DNS records not yet visible?)'}")

    # -- Step 5: show service configuration DNS records --
    records = domain.service_configuration_records.get().execute_query()
    _print_dns_records(records, f"Service configuration DNS records for '{args.domain}'")

    # -- Step 6: set supported services (optional) --
    if args.services:
        if args.apply:
            domain.set_property("supportedServices", args.services)
            domain.update().execute_query()
            print(f"\nSupported services set to: {', '.join(args.services)}")
        else:
            print(f"\nWould set supported services to: {', '.join(args.services)} (dry run).")


if __name__ == "__main__":
    main()
