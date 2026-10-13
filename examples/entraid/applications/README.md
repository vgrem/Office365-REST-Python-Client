# Application Registration & Permissions

App registrations are the identity half of Entra ID: an app registration declares
*who* an application is and *what it asks for*, while its service principal is the
per-tenant object that actually receives permissions and credentials. This tour
walks from listing and creating apps, through credential lifecycle (rotate,
renew, clean up), to consent (check, grant, revoke) and the governance reports
you need to keep the directory clean.

## Which client do I use?

The scripts split into two groups:

- **Read-only reports** sign in with an **app-only client secret** (e.g.
  `credentials_report.py`, `permissions_report.py`, `list_*`) and need
  `Directory.Read.All`.
- **Privileged writes** sign in **interactively as an administrator** with
  `with_token_interactive(...).require_role("Global Administrator", "Privileged Role Administrator")`,
  because no app-only role in this library consents to consent. The helper is
  named `_privileged_client()` so the intent is obvious.

## 1. Get your bearings

| What | File | Notes |
|------|------|-------|
| List app registrations | [`list.py`](./list.py) | First 100 app registrations (name, app id, created date) |
| Look up one app by client ID | [`get_by_app_id.py`](./get_by_app_id.py) | `applications.get_by_app_id(...)` |
| Register a new app | [`create.py`](./create.py) | Creates an app, then deletes it again |
| Update redirect URIs | [`redirect_uris.py`](./redirect_uris.py) | Merge new URIs into the existing `web` object |

```python
app = client.applications.get_by_app_id("00000000-0000-0000-0000-000000000000").get().execute_query()
print(app.display_name, app.app_id)
```

## 2. Inventory credentials

Start here if you have inherited a tenant. Every app is listed with its password
and certificate credentials and their expiry, so you can see what is about to
break.

| What | File | Notes |
|------|------|-------|
| All app credentials + expiry | [`credentials_report.py`](./credentials_report.py) | Passwords and certificates; `--warn-days`, `--expired-only` |
| Service-principal credentials | [`sp_report.py`](./sp_report.py) | Credentials on service principals (not just app objects) |
| Certificates only | [`list_certificates.py`](./list_certificates.py) | Per-certificate expiry status (`--warn-days`) |
| All consent grants | [`consent_grants.py`](./consent_grants.py) | Tenant-wide and user-scoped OAuth2 grants |
| App sign-in activity | [`app_signins.py`](./app_signins.py) | Last sign-in per app to spot unused registrations |

```python
for cred in app.password_credentials:
    print(f"[{cred.kind}] {cred}  {cred.expiry_status(warn_days=30)}")
```

## 3. Rotate and renew credentials

The credential properties `is_expired` and `days_until_expiry` interpret a naive
`endDateTime` as UTC, so the checks below are portable. `expiry_status(warn_days)`
wraps them into a printable label (`expired 3d ago`, `expiring in 9d`, ...).

| What | File | Notes |
|------|------|-------|
| Add a client secret | [`rotate_secret.py`](./rotate_secret.py) | Generate a password, optionally print `CLIENT_SECRET=...` |
| Renew a secret before it expires | [`renew_secret.py`](./renew_secret.py) | No-op unless within `--days` |
| Upload a certificate | [`rotate_cert.py`](./rotate_cert.py) | Self-signed cert generated into a temp dir |
| Renew a certificate | [`renew_cert.py`](./renew_cert.py) | Same check-then-add flow for certs |
| Rotate every expired secret | [`rotate_all_expired.py`](./rotate_all_expired.py) | Dry-run by default; `--apply` to write |
| Remove expired secrets | [`cleanup_old.py`](./cleanup_old.py) | Dry-run by default; keeps a grace period |

```python
new = app.add_password("rotated-by-sdk").execute_query()  # or add_certificate(cert, ...)
print(new.key_id)  # keep the secretText, it is shown once
```

## 4. Check and list permissions

| What | File | Notes |
|------|------|-------|
| Full permission inventory | [`permissions_report.py`](./permissions_report.py) | Requested + granted, names resolved per resource |
| Does the app have a delegated scope? | [`has_delegated_perms.py`](./has_delegated_perms.py) | Returns `bool` |
| Does the app have an application role? | [`has_application_perms.py`](./has_application_perms.py) | Returns `bool` |
| List granted delegated scopes | [`list_delegated_perms.py`](./list_delegated_perms.py) | All-principals grants on Microsoft Graph |
| List granted application roles | [`list_application_perms.py`](./list_application_perms.py) | App-role assignments on Microsoft Graph |

`permissions_report.py` is the one to reach for first: it resolves each
`resourceAppId` against that resource's own service principal, so roles on
non-Graph resources are named too — a report that only maps Microsoft Graph
leaks raw GUIDs for everything else.

## 5. Grant and revoke consent

Grant and revoke scripts sign in as an administrator because consent is a
privileged operation.

| What | File | Notes |
|------|------|-------|
| Grant a delegated scope | [`grant_delegated_perms.py`](./grant_delegated_perms.py) | AllPrincipals; idempotent |
| Grant an application role | [`grant_application_perms.py`](./grant_application_perms.py) | Needs `AppRoleAssignment.ReadWrite.All` |
| Revoke a delegated scope | [`revoke_delegated_perms.py`](./revoke_delegated_perms.py) | Delete the OAuth2 grant |
| Revoke an application role | [`revoke_application_perms.py`](./revoke_application_perms.py) | Delete the app-role assignment |
| Grant a site-scoped role | [`grant_site_selected_permission.py`](./grant_site_selected_permission.py) | `Sites.Selected` pattern for one SharePoint site |

The full pipeline — register → create service principal → add secret and
certificate → request permissions → consent — is wired together in
[`provision.py`](./provision.py). It cleans up after itself and is the best
end-to-end reference.

```python
# delegated consent (works with Directory.ReadWrite.All)
client.grant_delegated_permissions(app_id, "User.Read").execute_query()

# application consent needs AppRoleAssignment.ReadWrite.All
client.grant_application_permissions(app_id, "User.Read.All").execute_query()
```

## 6. Governance and hygiene

| What | File | Notes |
|------|------|-------|
| Apps with no valid credentials | [`find_stale_apps.py`](./find_stale_apps.py) | Candidates for deletion |
| Apps with no owners | [`find_orphans.py`](./find_orphans.py) | Ownerless registrations are a risk |
| Over-privileged service principals | [`high_privilege_service_principals.py`](./high_privilege_service_principals.py) | Directory-role holders |
| Delete stale apps | [`cleanup_stale.py`](./cleanup_stale.py) | Dry-run by default; `--apply` to delete |
| Restore a deleted app | [`restore_app.py`](./restore_app.py) | Uses `deleted_items` |

## Sharp edges

- **Reading app registrations works app-only; writing needs delegated consent.**
  `Directory.Read.All` covers the read-only reports (`list.py`,
  `get_by_app_id.py`, `permissions_report.py`), but app-only roles here do not
  include `Application.ReadWrite.All`, so the lifecycle scripts sign in
  interactively as an administrator instead.
- **Granting an application role needs `AppRoleAssignment.ReadWrite.All`.**
  Blanket admin consent via `Directory.ReadWrite.All` grants *delegated* scopes
  but **not** app roles; `grant_application_perms.py` and `provision.py` catch the
  `Authorization_RequestDenied` and print the requirement instead of crashing.
- **Creating an app does not create its service principal.** Call
  `client.service_principals.ensure(app_id).execute_query()` before using any
  service-principal-scoped helper.
- **`add_password` does not return a `displayName`.** The secret text is returned
  once; read `key_id` and `secret_text`, and label the secret in your own store.
  Portal-created secrets *do* carry a `displayName`.
- **PATCHing `web` replaces the whole object.** Read
  `dict(app.properties.get("web") or {})`, mutate `redirectUris`, then write it
  back — otherwise you drop the other `web` keys.

---

## Official docs

- [Register an application](https://learn.microsoft.com/en-us/graph/auth-register-app-v2)
- [Permissions grant via Graph API](https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph)
- [Service principal objects](https://learn.microsoft.com/en-us/entra/identity-platform/app-objects-and-service-principals)
