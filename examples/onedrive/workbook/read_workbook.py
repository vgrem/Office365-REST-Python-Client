"""
Get workbook
"""

from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_password,
    test_team_site_url,
    test_tenant,
    test_username,
)

file_abs_url = "{0}/Shared Documents/Financial Sample.xlsx".format(test_team_site_url)

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
drive_item = client.shares.by_url(file_abs_url).drive_item.get().execute_query()
worksheets = drive_item.workbook.worksheets.get().execute_query()
for ws in worksheets:
    print(ws)
