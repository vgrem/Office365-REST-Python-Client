"""
Controlling app access on a specific SharePoint site collection

Refer for doc:
https://developer.microsoft.com/en-us/office/blogs/controlling-app-access-on-specific-sharepoint-site-collections/

"""
from examples import acquire_token_by_client_credentials
from office365.graph_client import GraphClient
from office365.onedrive.permissions.permission import Permission
from office365.onedrive.sites.site import Site

client = GraphClient(acquire_token_by_client_credentials)

site = client.sites.root  # type: Site
site_permission = site.permissions.add(
    roles=["write"],
    grantedToIdentities=[{
        "application": {
            "id": "89ea5c94-7736-4e25-95ad-3fa95f62b66e",
            "displayName": "Contoso Time Manager App"
        }
    }]
).execute_query()   # type: Permission

