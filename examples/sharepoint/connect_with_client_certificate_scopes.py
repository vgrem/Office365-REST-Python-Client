"""
Demonstrates how to authenticate using App-Only flow

Refer this article for a detailed instruction:
https://learn.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azuread
"""
import os

from office365.sharepoint.client_context import ClientContext
from tests import (
    test_cert_thumbprint,
    test_client_id,
    test_site_url,
    test_tenant,
)

cert_credentials = {
    "tenant": test_tenant,
    "client_id": test_client_id,
    "thumbprint": test_cert_thumbprint,
    "cert_path": "{0}/../selfsignkey.pem".format(os.path.dirname(__file__)),
    "scopes": ["{0}/.default".format(test_site_url)],
}

ctx = ClientContext(test_site_url).with_client_certificate(**cert_credentials)
current_web = ctx.web.get().execute_query()
print(current_web)
