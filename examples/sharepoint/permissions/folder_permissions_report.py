"""
Report on folders with unique permissions across a SharePoint site.

Traverses all folders in a document library and identifies those that have
broken permission inheritance — a common security and governance concern.

Inspired by Report-PermissionsFolderLevel.PS1 from Office 365 for IT Pros.

Required delegated permissions:
    Sites.Read.All          Read site, library, and folder structures
    Sites.FullControl.All   (if reading role assignments is needed)

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/folder-operations
"""

from __future__ import annotations

import argparse

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.principal.type import PrincipalType
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant

_MAX_MEMBERS = 5


def _member_names(role_assignments) -> list[str]:
    names = []
    for assignment in role_assignments:
        member = assignment.member
        kind = "Group" if member.principal_type == PrincipalType.SharePointGroup else "User"
        names.append(f"{member.title or str(member)} ({kind})")
    return names


def scan_folder_permissions(ctx: ClientContext, folder_url: str) -> list[dict]:
    """Recursively collect folders that have unique (broken) permissions."""
    results: list[dict] = []

    try:
        folder = ctx.web.get_folder_by_server_relative_url(folder_url)
        folder_item = folder.list_item_all_fields
        ctx.load(folder_item, ["HasUniqueRoleAssignments"])
        sub_folders = folder.folders.get().execute_query()

        if folder_item.has_unique_role_assignments:
            assignments = folder_item.role_assignments.expand(["Member"]).get().execute_query()
            results.append(
                {
                    "path": folder_url,
                    "role_assignment_count": len(assignments),
                    "members": _member_names(assignments),
                }
            )

        for sub_folder in sub_folders:
            sub_url = sub_folder.server_relative_url
            if sub_url:
                results.extend(scan_folder_permissions(ctx, sub_url))

    except Exception as e:
        print(f"Error scanning {folder_url}: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Report folders with unique permissions")
    parser.add_argument(
        "--list", dest="list_title", default=None, help="library to scan (default: default document library)"
    )
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    if args.list_title:
        lib = ctx.web.lists.get_by_title(args.list_title).expand(["RootFolder"]).get().execute_query()
    else:
        lib = ctx.web.default_document_library().expand(["RootFolder"]).get().execute_query()
    library_path = lib.root_folder.server_relative_url
    if not library_path:
        print("Could not resolve library path")
        return

    print(f"Scanning library: {library_path}\n")
    folders = scan_folder_permissions(ctx, library_path)

    if not folders:
        print("No folders with unique permissions found (all inherit from parent).")
        return

    print(f"Found {len(folders)} folders with unique permissions:\n")
    for folder in sorted(folders, key=lambda f: f["path"]):
        print(f"  {folder['path']}")
        print(f"    Role assignments: {folder['role_assignment_count']}")
        for member in folder["members"][:_MAX_MEMBERS]:
            print(f"      - {member}")
        if len(folder["members"]) > _MAX_MEMBERS:
            print(f"      ... and {len(folder['members']) - _MAX_MEMBERS} more")
        print()


if __name__ == "__main__":
    main()
