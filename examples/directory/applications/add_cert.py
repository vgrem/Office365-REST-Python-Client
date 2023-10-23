"""
Add a certificate to an app using Microsoft Graph

To create the self-signed certificate, run the following command at a terminal prompt:
- openssl req -x509 -newkey rsa:2048 -keyout selfsignkey.pem -out selfsigncert.pem -nodes -days 365

https://learn.microsoft.com/en-us/graph/applications-how-to-add-certificate
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_tenant
from tests.graph_case import acquire_token_by_username_password


def verify_connect():
    """Test the app-only authentication"""

    thumbprint = "12FC1BB6796D114AF4FEBBE95FCA8084CF47D81F"
    cert_key_path = "../../selfsignkey.pem"
    with open(cert_key_path, "r") as fh:
        private_key = fh.read()

    ctx = GraphClient.with_certificate(
        test_tenant, test_client_id, thumbprint, private_key
    )
    site = ctx.sites.root.get().execute_query()
    print(site.web_url)


cert_path = "../../selfsigncert.pem"

client = GraphClient(acquire_token_by_username_password)
target_app = client.applications.get_by_app_id(test_client_id)
with open(cert_path, "rb") as f:
    cert_data = f.read()
target_app.add_certificate(cert_data, "Internet Widgits Pty Ltd").execute_query()

verify_connect()
