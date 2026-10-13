"""
Provision an application end to end: register, credentials, permissions, consent.

This is the pipeline behind "give a new service a runnable identity". It walks
through every step a platform team usually automates:

1. **register** the application (``applications.add``);
2. **create the service principal** (``servicePrincipals.ensure``) so the app can
   actually hold grants and be assigned roles;
3. **add credentials** — a client secret (``addPassword``) and a certificate
   (``addCertificate``);
4. **declare permissions** in the manifest (``requiredResourceAccess``);
5. **grant admin consent** — delegated scopes are granted directly; application
   (app role) grants require ``AppRoleAssignment.ReadWrite.All`` and are
   attempted with a graceful, explanatory failure when the caller lacks it.

By default the app and its service principal are deleted again (clean run);
pass ``--keep`` to leave them in place and print a ready ``.env`` block.

Usage:

    python provision.py --delegated User.Read Mail.Read --application User.Read.All

Requires an interactive sign-in by a Global Administrator or Privileged Role
Administrator for the writes (the delegated ``Application.ReadWrite.All`` scope
is carried by the signed-in account); granting *application* permissions also
needs ``AppRoleAssignment.ReadWrite.All``, so ``provision.py`` attempts it and
reports the requirement when the sign-in lacks it.

Reference:
    https://learn.microsoft.com/en-us/graph/api/application-post-applications
    https://learn.microsoft.com/en-us/graph/api/application-addpassword
    https://learn.microsoft.com/en-us/graph/api/application-post-certificates
    https://learn.microsoft.com/en-us/graph/api/serviceprincipal-post-delegatedpermissions
    https://learn.microsoft.com/en-us/graph/api/serviceprincipal-post-approleassignments
"""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

from office365.directory.applications.required_resource_access import RequiredResourceAccess
from office365.directory.applications.resource_access import ResourceAccess
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_value_collection import ClientValueCollection
from tests import create_unique_name
from tests.settings import admin_username, client_id, tenant

GRAPH_RESOURCE = "Microsoft Graph"


def _privileged_client() -> GraphClient:
    return (
        GraphClient(tenant=tenant)
        .with_token_interactive(client_id, admin_username)
        .require_role("Global Administrator", "Privileged Role Administrator")
    )


def _generate_certificate(directory: Path, common_name: str) -> tuple[Path, Path]:
    """Create a self-signed certificate/key pair and return their paths."""
    key_path = directory / "private.pem"
    cert_path = directory / "public.crt"
    subprocess.run(["openssl", "genrsa", "-out", str(key_path), "2048"], check=True, capture_output=True)
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-new",
            "-key",
            str(key_path),
            "-out",
            str(cert_path),
            "-days",
            "365",
            "-subj",
            f"/CN={common_name}",
        ],
        check=True,
        capture_output=True,
    )
    return key_path, cert_path


def _required_resource_access(client: GraphClient, delegated: list[str], application: list[str]):
    """Build the ``requiredResourceAccess`` entry for the Microsoft Graph resource."""
    sp = client.service_principals.find_by_name(GRAPH_RESOURCE, required=True).get().execute_query()
    scopes = {s.value: s.id for s in sp.oauth2_permission_scopes}
    roles = {r.value: r.id for r in sp.app_roles}

    entry = RequiredResourceAccess(resourceAppId=sp.app_id)
    for name in delegated:
        entry.resourceAccess.add(ResourceAccess(id=scopes[name], type="Scope"))
    for name in application:
        entry.resourceAccess.add(ResourceAccess(id=roles[name], type="Role"))
    return ClientValueCollection(RequiredResourceAccess, [entry])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", help="display name (default: ProvisionedApp + random suffix)")
    parser.add_argument("--delegated", nargs="*", default=["User.Read", "Mail.Read"], help="delegated scopes to request")
    parser.add_argument("--application", nargs="*", default=[], help="application roles to request")
    parser.add_argument("--keep", action="store_true", help="keep the app instead of deleting it")
    args = parser.parse_args()

    name = args.name or create_unique_name("ProvisionedApp")
    client = _privileged_client()

    # 1. Register the application
    app = client.applications.add(name, signInAudience="AzureADMyOrg").execute_query()
    if app.app_id is None:
        raise RuntimeError("Application was created without an appId")
    app_id = app.app_id
    print(f"1. Registered: {app.display_name} (appId={app_id})")

    # 2. Create its service principal
    sp = client.service_principals.ensure(app_id).execute_query()
    print(f"2. Service principal: {sp.id}")

    # 3. Add credentials (secret + certificate)
    secret = app.add_password("Provisioned secret").execute_query().value
    print(f"3a. Client secret created (keyId={secret.keyId})")
    key_path, cert_path = _generate_certificate(Path(tempfile.mkdtemp()), name)
    app.add_certificate(cert_path.read_bytes(), name).execute_query()
    print(f"3b. Certificate uploaded from {cert_path}")

    # 4. Declare the requested permissions in the manifest
    app.set_property("requiredResourceAccess", _required_resource_access(client, args.delegated, args.application))
    app.update().execute_query()
    print(f"4. Requested delegated={args.delegated} application={args.application}")

    # 5. Grant admin consent
    for scope in args.delegated:
        client.grant_delegated_permissions(app_id, scope).execute_query()
        print(f"5a. Granted delegated scope: {scope}")
    for role in args.application:
        try:
            client.grant_application_permissions(app_id, role).execute_query()
            print(f"5b. Granted application role: {role}")
        except ClientRequestException as exc:
            print(f"5b. Could not grant application role {role}: {exc}.")
            print("    Application-role consent requires AppRoleAssignment.ReadWrite.All.")

    if args.keep:
        print("\nAdd to .env:")
        print(f"OFFICE365_TENANT={tenant}")
        print(f"OFFICE365_CLIENT_ID={app.app_id}")
        print(f"OFFICE365_CLIENT_SECRET={secret.secretText}")
        print(f"OFFICE365_CERT_PATH={key_path}")
    else:
        sp.delete_object().execute_query()
        app.delete_object(permanent_delete=True).execute_query()
        print("\nCleaned up the application and its service principal.")


if __name__ == "__main__":
    main()
