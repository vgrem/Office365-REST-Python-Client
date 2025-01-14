"""
Setting up an Azure AD app for app-only access for SharePoint API

Steps:

1. create and configure a self-signed X.509 certificate, which will be used to authenticate your Application
    against Azure AD, while requesting the App Only access token. For example, to create the self-signed certificate,
    run the following command at a terminal prompt:
    openssl req -x509 -newkey rsa:2048 -keyout selfsignkey.pem -out selfsigncert.pem -nodes -days 365

2. register Azure AD application
3. add permissions
4. upload certificate (public key)

"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

admin_client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
