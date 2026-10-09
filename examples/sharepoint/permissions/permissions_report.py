"""
Report role assignments across a SharePoint site (access review / least privilege).

Who (users/groups) holds which role on the site and, optionally, on each list.

    python permissions_report.py --all-lists
    python permissions_report.py --list "Documents"

Requires read access; role assignments need an owner-level account or the
Sites.FullControl.All application permission.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/permissions-api-reference
"""

from __future__ import annotations

import argparse

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.principal.principal import Principal
from office365.sharepoint.principal.type import PrincipalType
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant

MAX_MEMBERS = 10


def _member_kind(member: Principal) -> str:
    return "Group" if member.principal_type == PrincipalType.SharePointGroup else "User"


def _role_rows(role_assignments) -> list[str]:
    return [
        f"  {ra.member.title or str(ra.member)} ({_member_kind(ra.member)}): "
        f"{', '.join(r.name for r in ra.role_definition_bindings)}"
        for ra in role_assignments
    ]


def _print_securable(label: str, securable) -> None:
    securable.context.load(securable, ["HasUniqueRoleAssignments"])
    assignments = securable.role_assignments.expand(["Member", "RoleDefinitionBindings"]).get().execute_query()
    unique = "unique" if securable.has_unique_role_assignments else "inherited"
    rows = _role_rows(assignments)
    print(f"{label}  ({len(assignments)} assignment(s), {unique}):")
    print("\n".join(rows[:MAX_MEMBERS]))
    if len(rows) > MAX_MEMBERS:
        print(f"  ... and {len(rows) - MAX_MEMBERS} more")
    print()


def main():
    parser = argparse.ArgumentParser(description="Report role assignments across a site")
    parser.add_argument("--list", dest="list_title", default=None, help="report only this list")
    parser.add_argument("--all-lists", action="store_true", help="report every (non-hidden) list")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )

    _print_securable("Site:", ctx.web)

    if args.list_title:
        _print_securable(f"List: {args.list_title}", ctx.web.lists.get_by_title(args.list_title))
    elif args.all_lists:
        for lst in ctx.web.lists.get().execute_query():
            if not lst.hidden:
                _print_securable(f"List: {lst.title}", lst)


if __name__ == "__main__":
    main()
