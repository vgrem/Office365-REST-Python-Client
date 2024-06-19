"""
Demonstrates how to get a drive by path.
"""

from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_client_secret,
    test_site_url,
    test_tenant,
)

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
drive_abs_url = "{0}/Documents".format(test_site_url)
result = client.shares.by_url(drive_abs_url).site.drive.get().execute_query()
print("Drive url: {0}".format(result))
