# Getting started

Connect to SharePoint Online, grant the **least access you need**, and make your
first call. By the end of this page you will have:

- one **app registration** (provisioned or reused by name),
- a **certificate** attached to it,
- the **`Sites.Selected`** application permission consented,
- access to the **specific site(s)** you choose,
- and the connection values to add to `.env` so every example under `examples/` runs.

> The SharePoint REST API (`/_api`) app-only model **requires a certificate**.
> A client secret works for Microsoft Graph, but not for SharePoint — see
> [Why a certificate?](#why-a-certificate-and-not-a-client-secret).

---

## The three questions

1. **Do I need a new app registration?** Usually no — one app covers every
   SharePoint example. The setup script **provisions or reuses** an app named
   `--app-name` (default `sharepoint-app`); re-running reuses it. Keep the admin
   app you sign in with in `OFFICE365_SETUP_CLIENT_ID`.
2. **How does the certificate get attached?** The script generates a self-signed
   certificate and uploads its **public** part to the app. The **private** key
   stays local as `tests/selfsigncert.pem` and is what the client signs with.
3. **What permission, and which sites?** Grant **`Sites.Selected`** once (admin
   consent), then grant the app `read`/`write` on only the sites it needs. Use
   `--scope all` if you prefer a single tenant-wide `Sites.FullControl.All`.

---

## Step 1 — Register (or reuse) an app

App-only automation signs in as an application, so it still needs one app
registration in Microsoft Entra ID. You do **not** need a separate app per
script.

1. Have (or create) an app the setup script can sign in with. It must allow
   **public client flows** and have the delegated **`Application.ReadWrite.All`**
   permission with admin consent. If you are starting from scratch, follow
   [Set up live authentication](https://github.com/vgrem/office365-rest-python-client/blob/master/README-dev.md#set-up-live-authentication).
2. Put its tenant, id, and an admin account in `.env`:

   ```dotenv
   OFFICE365_TENANT=contoso.onmicrosoft.com
   OFFICE365_CLIENT_ID=00000000-0000-0000-0000-000000000000
   OFFICE365_ADMIN_USERNAME=admin@contoso.onmicrosoft.com
   ```

The admin you sign in with needs **Global Administrator** or **Privileged Role
Administrator**.

> **Sign-in app vs. provisioned app.** The script signs in with `--client-id`,
> `OFFICE365_SETUP_CLIENT_ID`, or `OFFICE365_CLIENT_ID` (in that order), then
> provisions or reuses a dedicated app named `--app-name` for app-only access. It
> prints the provisioned app as `OFFICE365_CLIENT_ID` and the sign-in app as
> `OFFICE365_SETUP_CLIENT_ID`, so your delegated admin app stays separate from
> the app that receives SharePoint permissions — and re-runs keep working.

## Step 2 — Run the full-cycle setup

[`setup_sharepoint_app.py`](./setup_sharepoint_app.py) walks the whole cycle in one
command:

```bash
uv run python examples/sharepoint/getting-started/setup_sharepoint_app.py \
    --site https://contoso.sharepoint.com/sites/team
```

The script tells you what it did:

| Step | What happens |
|---|---|
| App | Provisions or reuses the app named `--app-name` (default `sharepoint-app`) and its service principal |
| Certificate | Generates `tests/selfsigncert.{crt,pem}` and attaches the public part to the app |
| Permission | Grants **`Sites.Selected`** to the app with admin consent |
| Site access | Grants the app `write` on each `--site` |
| Output | Prints the connection values to add to `.env` (`OFFICE365_CLIENT_ID`, `OFFICE365_SETUP_CLIENT_ID`, certificate thumbprint/path) |

Useful flags:

| Flag | Effect |
|---|---|
| `--site URL` | Site to grant access to; repeat for several sites |
| `--role read\|write\|manage\|fullcontrol` | Per-site role with `Sites.Selected` (default `write`) |
| `--scope all` | Grant tenant-wide `Sites.FullControl.All` instead of per-site grants |
| `--app-name NAME` | App to provision or reuse (default `sharepoint-app`) |
| `--interactive` | Browser sign-in instead of the device code flow |

Re-running is safe: an already-attached certificate and an already-granted
permission are detected and skipped.

## Step 3 — Make your first call

[`hello_sharepoint.py`](./hello_sharepoint.py) connects with the certificate and
reads the site:

```python
from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant

ctx = ClientContext(site_url).with_client_certificate(
    tenant=tenant,
    client_id=client_id,
    thumbprint=cert_thumbprint,
    cert_path=cert_path,
)
web = ctx.web.get().execute_query()
print(f"Connected to {web.title} ({web.url})")
```

Then browse the [product catalog](../README.md) — sites, lists, files,
permissions, search, and more — and run any example the same way.

---

## `Sites.Selected` vs `Sites.FullControl.All`

| | `Sites.Selected` (recommended) | `Sites.FullControl.All` |
|---|---|---|
| Consent | Grant once, then per-site | Grant once, tenant-wide |
| Blast radius | Only the sites you grant | Every site in the tenant |
| SharePoint admin UI | Visible under **Active sites** → **Sharing** | Not per-site |
| Use when | A tool touches a few known sites | A tenant-wide reporting / migration tool |
| In this script | `--scope selected` (default) | `--scope all` |

`Sites.Selected` follows the principle of least privilege: a compromised
certificate exposes only the sites you explicitly granted.

## Why a certificate (and not a client secret)?

The SharePoint REST API (`/_api`) app-only flow only accepts certificates — a
client secret is rejected. A **certificate** is also more secure: the private key
never leaves your machine and the app presents a public-key proof instead of
sending a shared secret on every token request.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `401 Unauthorized` | Certificate not attached, or `OFFICE365_CERT_THUMBPRINT` / `OFFICE365_CERT_PATH` stale — re-run the setup |
| `403 Forbidden` on one site | The app has no per-site grant — re-run with `--site <url>` |
| `403 Forbidden` everywhere | `Sites.Selected` was never granted with admin consent |
| `Need one of: Global Administrator…` | Sign in with an admin, or grant the role first |
| `Could not verify roles` | The sign-in app needs delegated `RoleManagement.Read.Directory` |

## References

- <https://learn.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azuread>
- <https://learn.microsoft.com/en-us/graph/permissions-reference>
