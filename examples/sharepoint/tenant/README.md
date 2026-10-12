# Tenant Administration

Manage SharePoint tenant settings, sites, admins, sharing, and licensing.
These examples use the **tenant admin** API via the **tenant admin site**
(`https://contoso-admin.sharepoint.com`).

---

## Prerequisites

| Requirement | Description | Reference |
|---|---|---|
| **SharePoint Administrator** or **Global Administrator** role | Required for all tenant-level operations. Connection to the tenant admin site (`-admin.sharepoint.com`). | [SharePoint admin roles](https://learn.microsoft.com/en-us/sharepoint/sharepoint-admin-role) |

A `Tenant` object is the entry point for all tenant-level operations.

---

## Examples

### Configure settings

| Operation | File | Required role | API reference |
|---|---|---|---|
| Allow or block custom script on sites | [`allow_custom_script.py`](./allow_custom_script.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Change tenant sharing capability | [`change_sharing_capability.py`](./change_sharing_capability.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Enable app-only authentication (legacy ACS — deprecated) | [`enable_app_only_authentication.py`](./enable_app_only_authentication.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Check if legacy auth is enabled | [`is_legacy_auth_enabled.py`](./is_legacy_auth_enabled.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |

### Browse and discover

| Operation | File | Required role | API reference |
|---|---|---|---|
| List all site collections | [`get_all_sites.py`](./get_all_sites.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| List my sites (via search) | [`get_my_sites.py`](./get_my_sites.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Get a site by URL | [`get_site.py`](./get_site.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| List home sites | [`get_home_sites.py`](./get_home_sites.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Find sites without a Microsoft 365 group | [`sites_without_a_group.py`](./sites_without_a_group.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |

### Manage admins and sites

| Operation | File | Required role | API reference |
|---|---|---|---|
| Get site collection admins | [`get_site_admin.py`](./get_site_admin.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Set site collection admins | [`set_site_admin.py`](./set_site_admin.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Delete site collections | [`delete_sites.py`](./delete_sites.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| List / restore deleted sites | [`restore_deleted_site.py`](./restore_deleted_site.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |

### Reports and settings

| Operation | File | Required role | API reference |
|---|---|---|---|
| Check user license assignments | [`check_licenses.py`](./check_licenses.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Export all tenant settings to file | [`export_tenant_settings.py`](./export_tenant_settings.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Print tenant settings | [`print_tenant_settings.py`](./print_tenant_settings.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Print server settings | [`print_server_settings.py`](./print_server_settings.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Add a tenant theme | [`add_tenant_theme.py`](./add_tenant_theme.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |

### Storage & resource reporting

| Operation | File | Required role | API reference |
|---|---|---|---|
| File version policy (read / set / clear) | [`file_version_policy.py`](./file_version_policy.py) | SharePoint Admin + `Sites.FullControl.All` | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Storage usage report (all sites) | [`site_storage_report.py`](./site_storage_report.py) | SharePoint Admin + `Sites.Read.All` | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Quota management (site + OneDrive) | [`quota_management.py`](./quota_management.py) | SharePoint Admin + `Sites.FullControl.All` | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Find orphan OneDrive sites | [`find_orphan_onedrives.py`](./find_orphan_onedrives.py) | SharePoint Admin + `Directory.Read.All` | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |
| Export every OneDrive site's collection admins to CSV | [`export_onedrive_admins.py`](./export_onedrive_admins.py) | SharePoint Admin | [Tenant REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api) |

---

## Quick start

```python
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant

ctx = ClientContext("https://contoso-admin.sharepoint.com").with_client_certificate(
    "contoso.onmicrosoft.com", client_id="client_id", thumbprint="thumbprint", cert_path="./cert.pem"
)

tenant = Tenant(ctx)
sites = tenant.get_site_properties_from_sharepoint().execute_query()
for site in sites:
    print(f"  {site.Url}  ({site.Title})")
```

---

## Related recipes

- [Grant app site access](../recipes/grant_app_site_access.py) — bulk grant or revoke an app's `Sites.Selected` access across sites.
- [Search content inventory](../recipes/search_content_inventory.py) — tenant-wide content inventory with a stale-document count.

---

## API reference

- [SharePoint tenant administration REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api)
