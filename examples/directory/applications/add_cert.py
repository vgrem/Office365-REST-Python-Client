"""
Add a certificate to an app using Microsoft Graph

To create the self-signed certificate, run the following command at a terminal prompt:
- openssl req -x509 -newkey rsa:2048 -keyout selfsignkey.pem -out selfsigncert.pem -nodes -days 365

https://learn.microsoft.com/en-us/graph/applications-how-to-add-certificate
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

cert_path = "../../selfsigncert.pem"

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
target_app = client.applications.get_by_app_id(test_client_id)
with open(cert_path, "rb") as f:
    cert_data = f.read()
target_app.add_certificate(cert_data, "Internet Widgits Pty Ltd").execute_query()
