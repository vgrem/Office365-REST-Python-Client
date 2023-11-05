"""
Add a certificate to an app using Microsoft Graph

To create the self-signed certificate, run the following command at a terminal prompt:
- openssl req -x509 -newkey rsa:2048 -keyout selfsignkey.pem -out selfsigncert.pem -nodes -days 365

https://learn.microsoft.com/en-us/graph/applications-how-to-add-certificate
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_tenant
from tests.graph_case import acquire_token_by_username_password

cert_path = "../../selfsigncert.pem"

client = GraphClient(acquire_token_by_username_password)
target_app = client.applications.get_by_app_id(test_client_id)
with open(cert_path, "rb") as f:
    cert_data = f.read()
target_app.add_certificate(cert_data, "Internet Widgits Pty Ltd").execute_query()
