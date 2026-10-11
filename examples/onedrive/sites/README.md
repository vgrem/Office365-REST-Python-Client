# Working with SharePoint sites

A **site** is a container — of drives, lists, pages, permissions and members.
Start from a site's URL or server-relative path, then descend into whatever it
holds. These examples cover discovery, administration, sharing and reporting.
Requires `Sites.Read.All` to read, `Sites.ReadWrite.All` to change.

## Get a site

```python
client.sites.root  # the tenant root site
client.sites["contoso.sharepoint.com:/sites/marketing"]  # by host + path
client.sites.get_by_path("/sites/marketing").get().execute_query()
```

→ [`get_site.py`](./get_site.py) · [`get_site_by_path.py`](./get_site_by_path.py) · [`list_all.py`](./list_all.py) · [`subsites.py`](./subsites.py)

## Permissions & sharing

```python
site = client.sites.get_by_path("/sites/marketing").get().execute_query()
site.add_permission(...).execute_query()  # grant access
site.share("organization").execute_query()  # sharing link
```

→ [`site_permissions.py`](./site_permissions.py) · [`grant_permission.py`](./grant_permission.py) / [`revoke_permission.py`](./revoke_permission.py) · [`share_site_link.py`](./share_site_link.py) · [`external_sharing.py`](./external_sharing.py)

## Admins & follow

```python
site.admins.add(user).execute_query()
client.me.followed_sites.add(site.id).execute_query()
```

→ [`add_admin.py`](./add_admin.py) / [`remove_admin.py`](./remove_admin.py) · [`search_and_follow.py`](./search_and_follow.py) · [`unfollow_site.py`](./unfollow_site.py)

## Governance & reporting

Activity windows, stale-site detection, content-type/column inventory and CSV
exports — the "keep the tenant tidy" toolbox.

→ [`analytics_report.py`](./analytics_report.py) · [`site_activities.py`](./site_activities.py) · [`find_stale.py`](./find_stale.py) · [`stale_lifecycle.py`](./stale_lifecycle.py) · [`site_governance.py`](./site_governance.py) · [`storage_report.py`](./storage_report.py) · [`export_csv.py`](./export_csv.py)
