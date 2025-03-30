"""
Setting up an Azure AD app for app-only access for SharePoint API

Steps:

1. create and configure a self-signed X.509 certificate, which will be used to authenticate your Application
    against Azure AD, while requesting the App Only access token. For example, to create the self-signed certificate,
    run the following command at a terminal prompt:
    openssl req -x509 -newkey rsa:2048 -keyout selfsignkey.pem -out selfsigncert.pem -nodes -days 365

2. register Azure AD application
3. assign permissions (for instance Sites.FullControl.All permission)
4. grant Admin Consent.
4. create and upload certificate (public key).
5. assign App-Only Role to SharePoint.

"""

from office365.directory.applications.app_ids import MsAppIds
from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)
# client = GraphClient(tenant=test_tenant).with_token_interactive(test_client_id)
resource = client.service_principals.get_by_app_id(
    MsAppIds.Office_365_SharePoint_Online
)
app = client.applications.get_by_app_id(test_client_id)
resource.grant_application_permissions(app, "Sites.FullControl.All").execute_query()
