# office365-rest-python-client

**A Python client library for Microsoft 365, the SharePoint REST API and Microsoft Graph.**

[![Downloads](https://pepy.tech/badge/office365-rest-python-client/month)](https://pepy.tech/project/office365-rest-python-client)
[![PyPI](https://img.shields.io/pypi/v/office365-rest-python-client.svg)](https://pypi.python.org/pypi/office365-rest-python-client)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/office365-rest-python-client.svg)](https://pypi.python.org/pypi/office365-rest-python-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/vgrem/office365-rest-python-client/blob/master/LICENSE)
[![Sponsor](https://img.shields.io/badge/sponsor-vgrem-ea4aaa.svg?logo=github-sponsors)](https://github.com/sponsors/vgrem)

**Python 3.8+** · typed models · fluent queries · deferred execution · 700+ runnable examples

- **Two clients, one library** — `ClientContext` speaks the SharePoint REST API; `GraphClient` speaks Microsoft Graph.
- **Fluent and deferred** — chain `.select()`, `.filter()`, `.expand()`, `.top()`, `.order_by()` and only hit the wire when you call `execute_query()`.
- **Typed models** — every entity is a real Python class (`List`, `File`, `Team`, `Message`, …), not a dictionary.
- **Copy-paste examples** — a runnable script for every service and scenario under [`examples/`](https://github.com/vgrem/office365-rest-python-client/tree/master/examples).

> **New here?** Pick a client in [Choose your client](#choose-your-client), then jump straight to a runnable snippet in [Examples by product](#examples-by-product).

## Table of contents

- [Choose your client](#choose-your-client)
- [Installation](#installation)
- [Authentication](#authentication)
- [Quick start](#quick-start)
- [Examples by product](#examples-by-product)
- [Common patterns](#common-patterns)
- [Async / await](#async--await)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [Support](#support)

## Choose your client

The library ships two clients. Pick the one that matches the API you need.

| | `ClientContext` | `GraphClient` |
|---|---|---|
| **Talks to** | SharePoint REST API v1 | Microsoft Graph (`graph.microsoft.com`) |
| **Entry point** | `ClientContext("https://contoso.sharepoint.com/sites/team")` | `GraphClient(tenant="contoso.onmicrosoft.com")` |
| **Best for** | SharePoint lists, items, files, folders, search, permissions, site and tenant administration, taxonomy, webhooks | Outlook, OneDrive, Teams, OneNote, Planner, To Do, Entra ID, Intune, Purview, Bookings, reports, security… |
| **SharePoint** | Full fidelity | Partial — prefer `ClientContext` for SharePoint-only work |
| **Typed models** | `List`, `ListItem`, `File`, `Folder`, `Web`, `Site`, `User` … | `DriveItem`, `Team`, `Message`, `Event`, `User`, `Group`, `PlannerTask` … |
| **Auth** | certificate, interactive, device flow, cookies, NTLM (on-prem) | client secret, certificate, interactive, device flow, ROPC |
| **Examples** | [`examples/sharepoint/`](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint) | [`examples/`](https://github.com/vgrem/office365-rest-python-client/tree/master/examples) by product |
| **API reference** | [SharePoint REST](https://learn.microsoft.com/sharepoint/dev/sp-add-ins/get-to-know-the-sharepoint-rest-service) | [Microsoft Graph](https://learn.microsoft.com/graph/overview) |

**Rule of thumb**

- SharePoint lists, files, site or tenant administration → **`ClientContext`**
- Teams, Outlook, OneDrive, Entra ID, Intune, Purview, reports → **`GraphClient`**
- OneDrive files work with either client; `GraphClient` is the modern, cross-service path.

## Installation

```bash
pip install office365-rest-python-client
```

With [uv](https://docs.astral.sh/uv/):

```bash
uv add office365-rest-python-client
```

Directly from source:

```bash
pip install git+https://github.com/vgrem/office365-rest-python-client.git
```

## Authentication

Modern flows authenticate through **Microsoft Entra ID** using [MSAL](https://learn.microsoft.com/entra/identity-platform/msal-overview). Both clients support delegated (user) and app-only (application) access.

> [!IMPORTANT]
> SharePoint **ACS app-only** access was retired in April 2026 and **SAML-based** authentication in May 2026. Use the certificate, interactive or device-code flows below instead — see [`examples/sharepoint/auth/modern/`](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/auth/modern) and the migration script [`migrate_from_saml_to_cert.py`](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/sharepoint/auth/modern/migrate_from_saml_to_cert.py).

### ClientContext (SharePoint)

| Flow | Access | Method |
|---|---|---|
| Certificate | App-only | `with_client_certificate(tenant, client_id, thumbprint, cert_path=...)` |
| Interactive | Delegated (MFA) | `with_interactive(tenant, client_id)` |
| Device code | Delegated (MFA) | `with_device_flow(tenant, client_id)` |
| Username / password | Delegated | `with_username_and_password(tenant, client_id, username, password)` |
| Custom token | Either | `with_access_token(token_func)` |
| Browser cookies | Delegated | `with_cookies(cookie_source)` |
| NTLM | On-premises | `ClientContext(url, allow_ntlm=True).with_user_credentials(username, password)` |
| ACS / SAML | On-premises (legacy) | [legacy app-only](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/sharepoint/auth/legacy/with_app_only.py) · [legacy SAML](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/sharepoint/auth/legacy/with_user_credential.py) |

> [!NOTE]
> SharePoint app-only access requires a **certificate**. A client secret is not accepted by SharePoint REST API v1 — use `GraphClient` for secret-based app-only. See [why a client secret doesn't work for SharePoint](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/sharepoint/auth/README.md).

```python
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext("https://contoso.sharepoint.com/sites/team").with_client_certificate(
    "contoso.onmicrosoft.com",
    client_id="00000000-0000-0000-0000-000000000000",
    thumbprint="AA11BB22CC33DD44EE55FF66AA77BB88CC99DD00",
    cert_path="./private.pem",
)

web = ctx.web.get().execute_query()
print(web.title)
```

Ready-made scripts: [certificate](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/sharepoint/auth/modern/with_certificate.py) ·
[certificate (private key)](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/sharepoint/auth/modern/with_certificate_and_privkey.py) ·
[custom scopes](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/sharepoint/auth/modern/with_certificate_and_scopes.py) ·
[interactive](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/sharepoint/auth/modern/with_interactive.py) ·
[device flow](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/sharepoint/auth/modern/with_device_flow.py) ·
[username/password](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/sharepoint/auth/modern/with_username_and_password.py) ·
[access token](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/sharepoint/files/download_parallel.py) ·
[cookies](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/sharepoint/auth/modern/with_cookies.py) ·
[NTLM](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/sharepoint/auth/legacy/with_ntlm.py)

### GraphClient (Microsoft Graph)

| Flow | Access | Method |
|---|---|---|
| Client secret | App-only | `with_client_secret(client_id, client_secret)` |
| Certificate | App-only | `with_certificate(client_id, thumbprint, private_key)` |
| Interactive | Delegated (MFA) | `with_token_interactive(client_id)` |
| Device code | Delegated (MFA) | `with_device_flow(client_id)` |
| Username / password | Delegated | `with_username_and_password(client_id, username, password)` |
| Custom token | Either | `GraphClient(token_callback, tenant=...)` |

```python
from office365.graph_client import GraphClient

client = GraphClient(tenant="contoso.onmicrosoft.com").with_client_secret(
    client_id="00000000-0000-0000-0000-000000000000",
    client_secret="your-client-secret",
)

users = client.users.get().execute_query()
print(len(users), "users")
```

Ready-made scripts: [client secret](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/auth/with_client_secret.py) ·
[certificate](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/auth/with_client_cert.py) ·
[interactive](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/auth/interactive.py) ·
[device flow](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/auth/with_device_flow.py) ·
[username/password](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/auth/with_user_creds.py) ·
[custom token callback](https://github.com/vgrem/office365-rest-python-client/blob/master/examples/auth/with_token_callback.py)

## Quick start

**SharePoint list — read and write items**

```python
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext("https://contoso.sharepoint.com/sites/team").with_client_certificate(
    "contoso.onmicrosoft.com", client_id, thumbprint, cert_path="./private.pem"
)

tasks = ctx.web.lists.get_by_title("Tasks")
item = tasks.add_item({"Title": "Write the release notes"}).execute_query()
print("Created item:", item.id)

for task in tasks.items.get_all().execute_query():
    print(task.properties["Title"])
```

**Microsoft Graph — send an email**

```python
from office365.graph_client import GraphClient

client = GraphClient(tenant="contoso.onmicrosoft.com").with_client_secret(client_id, client_secret)

client.me.send_mail(
    subject="Hello from Graph API",
    body="This email was sent using the Microsoft Graph API.",
    to_recipients=["alex@contoso.onmicrosoft.com"],
).execute_query()
```

## Examples by product

Every snippet below is lifted from a runnable script. Follow the **More →** link for the full example and its required permissions.

### SharePoint (ClientContext)

```python
# Lists and items
tasks = ctx.web.lists.get_by_title("Tasks")
item = tasks.add_item({"Title": "Ship it", "Status": "Active"}).execute_query()
tasks.items.get_all().execute_query()  # or .filter("Status eq 'Active'").get_all()

# Files and folders
folder = ctx.web.get_folder_by_server_relative_url("/sites/team/Shared Documents")
with open("report.pdf", "rb") as f:
    file = folder.files.upload(f).execute_query()

with open("report.pdf", "wb") as f:
    ctx.web.get_file_by_server_relative_path("/sites/team/Shared Documents/report.pdf").download(f).execute_query()

# Large file (chunked upload session)
with open("video.mp4", "rb") as f:
    folder.files.create_upload_session(f, 10 * 1024 * 1024).execute_query()
```

| Area | Examples |
|---|---|
| Lists and items | [lists](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/lists) · [listitems](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/listitems) · [views](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/views) |
| Files and folders | [files](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/files) · [folders](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/folders) |
| Sites and webs | [sites](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/sites) · [webs](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/webs) · [hubsites](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/hubsites) |
| Search | [search](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/search) |
| Permissions and sharing | [permissions](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/permissions) · [sharing](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/sharing) |
| Fields and content types | [fields](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/fields) · [contenttypes](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/contenttypes) |
| Pages and navigation | [pages](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/pages) · [navigation](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/navigation) |
| Taxonomy and profiles | [taxonomy](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/taxonomy) · [userprofile](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/userprofile) |
| Tenant administration | [tenant](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/tenant) · [groups](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/groups) · [users](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/users) |
| Webhooks, migration, advanced | [webhooks](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/webhooks) · [migration](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/migration) · [advanced](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/sharepoint/advanced) |

### OneDrive

```python
uploaded = client.me.drive.root.upload_file("report.xlsx").execute_query()

with open("report.xlsx", "wb") as f:
    client.me.drive.root.get_by_path("report.xlsx").download(f).execute_query()
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/onedrive)

### Teams

```python
team = client.teams.create_and_wait("Contoso Project", "All project collaboration").execute_query()

channel = team.channels.add("Project Chat").execute_query()
channel.messages.add("Hello team!").execute_query()
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/teams)

### Outlook (mail and calendar)

```python
from datetime import datetime, timedelta, timezone

# Send mail
client.me.send_mail(
    subject="Hello from Graph API",
    body="This email was sent using the Microsoft Graph API.",
    to_recipients=["alex@contoso.onmicrosoft.com"],
).execute_query()

# Create a calendar event
when = datetime.now(timezone.utc) + timedelta(days=1)
client.me.calendar.events.add(
    subject="Team Lunch",
    body="Let's grab lunch together.",
    start=when,
    end=when + timedelta(hours=1),
    attendees=["alex@contoso.onmicrosoft.com"],
).execute_query()
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/outlook)

### Entra ID

```python
from office365.directory.users.password_profile import PasswordProfile
from office365.directory.users.profile import UserProfile

profile = UserProfile(
    displayName="Alex Wilber",
    userPrincipalName="alex@contoso.onmicrosoft.com",
    mailNickname="alex",
    accountEnabled=True,
    passwordProfile=PasswordProfile(password="P@ssw0rd!", forceChangePasswordNextSignIn=True),
)
user = client.users.add(profile).execute_query()
print(user.display_name)
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/entraid)

### Planner

```python
group = client.groups.find_by_name("My Sample Team", required=True).execute_query()
plans = group.planner.plans.get().execute_query()
task = client.planner.tasks.add("Update client list", plans[0].id).execute_query()
print(task.title)
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/planner)

### To Do

```python
for task_list in client.me.todo.lists.get().execute_query():
    print(task_list.display_name, len(task_list.tasks.get().execute_query()), "tasks")
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/todo)

### OneNote

```python
with open("Sample.html", "rb") as page_html:
    page = client.me.onenote.pages.add(presentation_file=page_html).execute_query()
print(page.links.oneNoteWebUrl)
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/onenote)

<details>
<summary><strong>More services</strong> — Admin, Reports, Defender, Intune, Purview, Bookings, Communications, Security, Insights, Backup Storage</summary>

#### Microsoft 365 admin

```python
announcement = client.admin.service_announcement
health = announcement.health_overviews.get().execute_query()
issues = announcement.issues.get().execute_query()
messages = announcement.messages.get().execute_query()
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/admin)

#### Usage reports

```python
report = client.reports.get_email_activity_counts("D30").execute_query()
print(report.value)  # CSV payload
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/reports)

#### Microsoft Defender

```python
alerts = client.security.alerts_v2.top(20).get().execute_query()
for alert in alerts:
    print(alert)
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/defender)

#### Microsoft Intune

```python
devices = client.device_management.managed_devices.get().execute_query()
for device in devices:
    print(device.device_name, device.operating_system, device.compliance_state)
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/intune)

#### Microsoft Purview

```python
labels = client.security.data_security_and_governance.sensitivity_labels.get().execute_query()
for label in labels:
    print(label.display_name, label.id)
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/purview)

#### Microsoft Bookings

```python
businesses = client.solutions.booking_businesses.get().execute_query()
for business in businesses:
    print(business.display_name)
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/booking)

#### Cloud communications

```python
presence = client.users["alex@contoso.onmicrosoft.com"].presence.get().execute_query()
print(presence.availability, presence.activity)
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/communications)

#### Security (threat intelligence)

```python
host = client.security.threat_intelligence.hosts["contoso.com"].get().execute_query()
reputation = host.reputation.get().execute_query()
print(reputation.properties.get("score"))
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/security)

#### Insights

```python
for item in client.me.insights.trending.get().execute_query():
    print(item.resource_reference)
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/insights)

#### Backup Storage

```python
backup = client.solutions.backup_restore
backup.get().execute_query()
print(backup.service_status.status)
```

[More →](https://github.com/vgrem/office365-rest-python-client/tree/master/examples/backuprestore)

</details>

## Common patterns

**Deferred execution.** Requests are queued and sent only when you call `execute_query()`. Chain the fluent methods first, then execute once.

```python
items = (
    ctx.web.lists.get_by_title("Tasks")
    .items.select(["Title", "Status"])
    .filter("Status eq 'Active'")
    .order_by("Title")
    .top(100)
    .get()
    .execute_query()
)
```

**Addressing resources.** Entities are addressed by the key you already know, so you rarely need an opaque id: user principal name, site path or URL, file path, list title. `get_by_url`/`get_by_path` on `client.sites` fetch when you call `execute_query()`; keyed/UPN forms and `driveItem.get_by_path` are lazy, so chain `.get()` first.

```python
user = client.users["ada@contoso.com"].get().execute_query()  # a user, by UPN
site = client.sites.get_by_url("https://contoso.sharepoint.com/sites/marketing").execute_query()
file = client.me.drive.root.get_by_path("Reports/Q1.xlsx").get().execute_query()
items = ctx.web.lists.get_by_title("Tasks").items.get().execute_query()
```

**Reading large collections.** Use `get_all()` to follow paging automatically, and `page_size` to stay under server limits.

```python
items = ctx.web.lists.get_by_title("Orders").items.get_all(page_size=2000).execute_query()

files = (
    ctx.web.get_folder_by_server_relative_url("/sites/team/Shared Documents")
    .get_files(recursive=True, page_size=2000)
    .execute_query()
)
```

**Batching.** Dispatch many queued operations in one round trip. Raise `concurrency` to run batches in parallel; throttled sub-requests are retried individually, honoring `Retry-After`.

```python
for row in rows:
    ctx.web.lists.get_by_title("Contacts").add_item(row)

ctx.execute_batch()  # sequential
ctx.execute_batch(concurrency=5)  # up to 5 batches in flight

# Graph
for user in new_users:
    client.users.add(user)
client.execute_batch(concurrency=5)
```

**Large lists (> 5,000 items).** SharePoint refuses filtered/sorted queries on non-indexed columns. The library can tell you what to index and pre-flight the query.

```python
from office365.sharepoint.listitems.caml import Caml, CamlQuery

query = CamlQuery.builder().where(Caml.text("Status").eq("Active")).order_by("ID").row_limit(2000, paged=True).build()

lst.check_query(query)  # raises with a clear message if an index is missing
print(lst.index_candidates(query))  # columns worth indexing
lst.ensure_indexed("Status").execute_query()  # create the index (builds in the background)
```

**Import and export DataFrames.** Optional helpers turn list items into [pandas](https://pandas.pydata.org/) / [Polars](https://pola.rs/) frames and back.

```python
lst = ctx.web.lists.ensure_list("Orders").execute_query()

df = lst.to_dataframe().execute_query().value
lst.from_dataframe(df, chunksize=100).execute_query()
```

## Async / await

Every call that reaches the network has an `await` twin. Builders stay synchronous — only the terminal call changes. No extra dependency is required: by default the blocking HTTP call is handed to a worker thread, so the event loop stays free.

```python
import asyncio


async def main() -> None:
    web = await ctx.web.get().execute_query_async()
    print(web.title)


asyncio.run(main())
```

`execute_query_async()`, `execute_batch_async()`, `get_all_async()`, `execute_query_parallel_async()`, streaming downloads/exports and long-running-operation polling all have async twins, and collections support `async for`. See the [async guide](https://vgrem.github.io/office365-rest-python-client/async/).

## Dependencies

Install the core package on its own, or add the extras you need:

| Extra | Adds | Use it for |
|---|---|---|
| `azure` | `azure-storage-blob`, `cryptography` | Azure Blob Storage and certificate helpers |
| `excel` | `openpyxl` | Reading and writing Excel workbooks |
| `examples` | `faker` | Running the sample scripts |
| `ntlm` | `requests-ntlm` | On-premises SharePoint with NTLM |
| `pandas` | `pandas` | `to_dataframe()` / `from_dataframe()` |
| `parquet` | `pyarrow` | Parquet import and export |
| `duckdb` | `duckdb` | Querying exported data locally |
| `sql` | `sqlalchemy` | SQL-backed import and export |
| `notebooks` | `jupyter`, `nbformat`, `jinja2` | Running the notebook samples |

```bash
pip install "office365-rest-python-client[pandas,excel]"
```

## Contributing

Issues and pull requests are welcome — please use the
[issue tracker](https://github.com/vgrem/office365-rest-python-client/issues) for bugs and ideas.

```bash
git clone https://github.com/vgrem/office365-rest-python-client.git
cd office365-rest-python-client
uv sync --all-extras
pytest --offline -q
```

See [CONTRIBUTING.md](https://github.com/vgrem/office365-rest-python-client/blob/master/CONTRIBUTING.md) for the full development setup. Run the gate before submitting: `ruff check .`, `ruff format --check .`, `pyright` and `pytest --offline -q`.

## Support

- **Source and examples** — [github.com/vgrem/office365-rest-python-client](https://github.com/vgrem/office365-rest-python-client)
- **Documentation** — [vgrem.github.io/office365-rest-python-client](https://vgrem.github.io/office365-rest-python-client/)
- **Changelog** — [CHANGELOG.md](https://github.com/vgrem/office365-rest-python-client/blob/master/CHANGELOG.md)
- **Questions** — [GitHub Discussions](https://github.com/vgrem/office365-rest-python-client/discussions) or tag [`office365-rest-python-client` on Stack Overflow](https://stackoverflow.com/questions/tagged/office365-rest-python-client)

If this project saves you time, please consider [sponsoring its development](https://github.com/sponsors/vgrem). ⭐

## License

Released under the [MIT License](https://github.com/vgrem/office365-rest-python-client/blob/master/LICENSE).
